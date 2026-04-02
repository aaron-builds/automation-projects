import json
from pathlib import Path

from app.models.schemas import EnrichedCompany, LeadScore

FIXTURES = Path(__file__).parents[2] / "fixtures"

LONDON_POSTAL_PREFIXES = {"E", "EC", "N", "NW", "SE", "SW", "W", "WC"}

# SIC code ranges of interest
TECH_SICS = {str(c) for c in range(62000, 63200)}        # IT/software/data
PROPERTY_SICS = {str(c) for c in range(68000, 68400)}    # Real estate


def is_london(company: EnrichedCompany) -> bool:
    if company.region and company.region.lower() == "london":
        return True
    if company.registered_office_address and company.registered_office_address.postal_code:
        prefix = company.registered_office_address.postal_code.split()[0]
        alpha = "".join(c for c in prefix if c.isalpha()).upper()
        return alpha in LONDON_POSTAL_PREFIXES
    return False


def score_company(company: EnrichedCompany) -> LeadScore:
    points = 0
    reasons = []

    # --- Incorporation age ---
    age = company.company_age_days or 0
    if age < 30:
        points += 40
        reasons.append("Very recently incorporated")
    elif age < 90:
        points += 25
        reasons.append("Recently incorporated")

    # --- Geography ---
    if is_london(company):
        points += 20
        reasons.append("London-based company")

    # --- Company type ---
    # CH API returns "ltd" or "private-limited-company" for the same entity type
    if company.company_type in ("ltd", "private-limited-company"):
        points += 20
        reasons.append("Private limited company")

    # --- SIC code signals ---
    sics = set(company.sic_codes or [])
    if sics & TECH_SICS:
        points += 15
        reasons.append("Tech / IT sector (SIC 62xxx-63xxx)")
    if sics & PROPERTY_SICS:
        points += 10
        reasons.append("Property / real estate sector (SIC 68xxx)")
    if len(sics) >= 3:
        points += 5
        reasons.append("Diversified SIC profile (3+ codes)")

    score = min(points, 100)

    if score <= 40:
        band = "low"
    elif score <= 70:
        band = "medium"
    else:
        band = "high"

    return LeadScore(
        company_number=company.company_number,
        score=score,
        band=band,
        score_reasons=reasons,
    )


def main():
    raw = json.loads((FIXTURES / "enriched_companies.json").read_text())
    companies = [EnrichedCompany(**item) for item in raw]

    scores = [score_company(c) for c in companies]

    name_map = {c.company_number: c.company_name for c in companies}
    for s in scores:
        reasons_str = ", ".join(s.score_reasons)
        print(f"{name_map[s.company_number]} | Score: {s.score} | Band: {s.band} | Reasons: {reasons_str}")

    output = [json.loads(s.model_dump_json()) for s in scores]
    (FIXTURES / "scored_leads.json").write_text(json.dumps(output, indent=2))
    print(f"\nSaved {len(scores)} scored leads to fixtures/scored_leads.json")


if __name__ == "__main__":
    main()

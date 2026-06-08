import csv
import json
from pathlib import Path

FIXTURES = Path(__file__).parents[2] / "fixtures"
OUTPUTS = Path(__file__).parents[2] / "outputs"

COLUMNS = [
    "lead_id",
    "event_date",
    "company_number",
    "company_name",
    "region",
    "company_age_days",
    "score",
    "band",
    "score_reasons",
    "director_name",
    "director_appointed",
    "why_it_matters",
    "suggested_outreach_line",
]

COLUMN_LABELS = {
    "company_number": "Company Number",
    "company_name": "Company Name",
    "region": "Region",
    "company_age_days": "Age (Days)",
    "score": "Lead Score",
    "band": "Priority",
    "score_reasons": "Why This Lead",
    "director_name": "Director Name",
    "director_appointed": "Director Appointed",
    "why_it_matters": "Opportunity",
    "suggested_outreach_line": "Suggested Outreach",
}

SUMMARY_COLUMNS = ["Company Name", "Region", "Priority", "Suggested Outreach"]


def build_why_it_matters(reasons: list[str], band: str) -> str:
    if not reasons:
        return "This company was recently incorporated."
    parts = []
    if any("recently incorporated" in r.lower() for r in reasons):
        parts.append("just incorporated")
    if any("london" in r.lower() for r in reasons):
        parts.append("based in London")
    if any("tech" in r.lower() for r in reasons):
        parts.append("operating in the tech sector")
    if any("property" in r.lower() for r in reasons):
        parts.append("active in property and real estate")
    if any("diversified" in r.lower() for r in reasons):
        parts.append("with a diversified business profile")

    if parts:
        joined = ", ".join(parts[:-1]) + (" and " + parts[-1] if len(parts) > 1 else parts[0])
        return f"This company is {joined}, making it a {band}-priority lead for early-stage accounting services."
    return f"This is a {band}-priority lead based on incorporation signals."


def build_outreach_line(company_name: str, reasons: list[str]) -> str:
    is_london = any("london" in r.lower() for r in reasons)
    is_tech = any("tech" in r.lower() for r in reasons)
    is_property = any("property" in r.lower() for r in reasons)
    is_diversified = any("diversified" in r.lower() for r in reasons)

    name = company_name.title()

    if is_tech and is_london:
        variants = [
            f"{name} incorporated recently in London — R&D tax relief, EMI share schemes, and early structure decisions are worth getting right from month one. Worth a conversation?",
            f"R&D tax relief and EMI share schemes are time-sensitive for {name} — getting the structure right early in London makes a real difference. Happy to talk?",
            f"For a newly incorporated London tech business like {name}, early R&D and share scheme advice tends to pay for itself several times over. Worth a call?",
            f"Getting {name}'s R&D tax position and share scheme setup right from the start is much easier than correcting it later. Open to a quick conversation?",
        ]
    elif is_tech:
        variants = [
            f"{name} is a newly incorporated tech business — R&D tax credits and share scheme setup are time-sensitive from incorporation. Happy to run through what applies?",
            f"Early R&D tax credit and EMI setup advice could save {name} significantly — these are most effective when structured from the start. Worth a quick call?",
            f"Tech businesses like {name} often leave R&D relief and share scheme value on the table by leaving it too late. Happy to have a conversation?",
            f"Sorting {name}'s R&D position and share scheme structure early avoids costly corrections later. Open to a brief conversation?",
        ]
    elif is_property and is_london:
        variants = [
            f"{name} has just incorporated in London with property activity — VAT elections, SDLT structure, and ownership setup are worth reviewing early. Would a quick conversation be useful?",
            f"VAT elections and SDLT structure decisions made early can save {name} significantly — London property businesses benefit most from getting this right at incorporation. Worth a call?",
            f"For {name}, incorporating in London with property interests means VAT, SDLT, and ownership structure decisions are time-sensitive. Happy to run through what matters most?",
            f"Property businesses like {name} face real VAT and SDLT exposure from day one in London — early advice is far cheaper than correcting mistakes later. Open to a conversation?",
        ]
    elif is_property:
        variants = [
            f"{name} incorporated recently with property interests — SDLT structure, VAT position, and ownership setup are worth reviewing before their first transaction. Worth a brief call?",
            f"SDLT structure and VAT elections are time-sensitive for {name} — getting these right before the first transaction is far easier than fixing them afterwards. Happy to help?",
            f"Property businesses like {name} often face avoidable SDLT and VAT exposure from day one — early advice tends to pay for itself quickly. Worth a conversation?",
            f"Reviewing {name}'s SDLT and VAT position before their first transaction could prevent some expensive mistakes. Open to a brief call?",
        ]
    elif is_london and is_diversified:
        variants = [
            f"{name} is a newly incorporated London business with activity across multiple sectors — early advice on structure, VAT, and reporting obligations tends to save significant cost later. Open to a conversation?",
            f"With activity across multiple sectors, {name} would benefit from early advice on structure, VAT registration, and reporting — getting this right in London from the start pays off. Worth a call?",
            f"A newly incorporated London business operating across sectors, {name} would benefit from early structure and VAT advice — it tends to save meaningful cost later. Happy to have a conversation?",
            f"Diversified from the start, {name} faces reporting and VAT decisions across multiple sectors — early London accountancy advice tends to save significant cost. Open to a brief call?",
        ]
    elif is_london:
        variants = [
            f"{name} incorporated recently in London — getting accounts, tax registration, and payroll set up correctly from the start avoids costly corrections later. Would it be worth a brief call?",
            f"A new London company like {name} has a short window to get accounts, tax registration, and payroll set up correctly — it's much easier at the start. Happy to help?",
            f"Getting {name}'s accounts, tax registration, and payroll set up correctly from day one in London is much simpler than fixing it later. Worth a quick conversation?",
            f"Early-stage London businesses like {name} often underestimate the cost of getting accounts, tax, and payroll wrong — it's much cheaper to get right from the start. Open to a call?",
        ]
    else:
        variants = [
            f"{name} incorporated recently — early advice on accounts, corporation tax, and payroll setup prevents the common mistakes that cost new businesses later. Happy to have a quick conversation if useful?",
            f"New businesses like {name} often encounter avoidable tax and payroll mistakes in the first year — early advice tends to be straightforward and well worth it. Worth a call?",
            f"Getting {name}'s accounts, corporation tax, and payroll set up correctly from the start prevents costly corrections later. Happy to have a brief conversation?",
            f"Most new businesses make avoidable tax and payroll errors in year one — a quick conversation with {name} now could save meaningful cost later. Open to it?",
        ]

    return variants[hash(company_name) % len(variants)]


def main():
    scores = {s["company_number"]: s for s in json.loads((FIXTURES / "scored_leads.json").read_text())}
    enriched = {c["company_number"]: c for c in json.loads((FIXTURES / "enriched_companies.json").read_text())}

    OUTPUTS.mkdir(exist_ok=True)
    output_path = OUTPUTS / "leads_export.csv"
    summary_path = OUTPUTS / "summary.csv"

    rows = []
    for number, score in scores.items():
        company = enriched.get(number, {})
        reasons = score.get("score_reasons", [])
        band = score["band"]

        rows.append({
            "lead_id": number,
            "event_date": company.get("incorporated_date", ""),
            "company_number": number,
            "company_name": company.get("company_name", ""),
            "region": company.get("region", ""),
            "company_age_days": company.get("company_age_days", ""),
            "score": score["score"],
            "band": band,
            "score_reasons": "; ".join(reasons),
            "director_name": company.get("director_name", "Not listed"),
            "director_appointed": company.get("director_appointed", ""),
            "why_it_matters": build_why_it_matters(reasons, band),
            "suggested_outreach_line": build_outreach_line(company.get("company_name", ""), reasons),
        })

    rows = [r for r in rows if r["band"] != "excluded"]
    rows.sort(key=lambda r: r["score"], reverse=True)

    # Rename columns for human-readable export
    labeled_columns = [COLUMN_LABELS.get(c, c) for c in COLUMNS]
    labeled_rows = [
        {COLUMN_LABELS.get(k, k): v for k, v in row.items()}
        for row in rows
    ]

    with output_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=labeled_columns)
        writer.writeheader()
        writer.writerows(labeled_rows)

    with summary_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=SUMMARY_COLUMNS)
        writer.writeheader()
        for row in labeled_rows:
            writer.writerow({
                "Company Name": row["Company Name"],
                "Region": row["Region"],
                "Priority": row["Priority"],
                "Suggested Outreach": row["Suggested Outreach"],
            })

    print(f"Export complete: {len(rows)} leads written to {output_path}")
    print(f"Summary written to {summary_path}")


if __name__ == "__main__":
    main()

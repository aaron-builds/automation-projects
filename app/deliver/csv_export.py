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
        return (
            f"{name} incorporated recently in London — R&D tax relief, EMI share schemes, "
            f"and early structure decisions are worth getting right from month one. "
            f"Worth a conversation?"
        )
    elif is_tech:
        return (
            f"{name} is a newly incorporated tech business — R&D tax credits and share scheme "
            f"setup are time-sensitive from incorporation. Happy to run through what applies to them?"
        )
    elif is_property and is_london:
        return (
            f"{name} has just incorporated in London with property activity — VAT elections, "
            f"SDLT structure, and ownership setup are worth reviewing early. "
            f"Would a quick conversation be useful?"
        )
    elif is_property:
        return (
            f"{name} incorporated recently with property interests — SDLT structure, VAT position, "
            f"and ownership setup are worth reviewing before their first transaction. "
            f"Worth a brief call?"
        )
    elif is_london and is_diversified:
        return (
            f"{name} is a newly incorporated London business with activity across multiple sectors — "
            f"early advice on structure, VAT, and reporting obligations tends to save significant cost later. "
            f"Open to a conversation?"
        )
    elif is_london:
        return (
            f"{name} incorporated recently in London — getting accounts, tax registration, "
            f"and payroll set up correctly from the start avoids costly corrections later. "
            f"Would it be worth a brief call?"
        )
    else:
        return (
            f"{name} incorporated recently — early advice on accounts, corporation tax, "
            f"and payroll setup prevents the common mistakes that cost new businesses later. "
            f"Happy to have a quick conversation if useful?"
        )


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

    with output_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=labeled_columns)
        writer.writeheader()
        writer.writerows(labeled_rows)

    with summary_path.open("w", newline="", encoding="utf-8") as f:
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

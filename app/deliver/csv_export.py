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

    if is_tech:
        angle = "tech startups often need specialist advice on R&D tax credits and share schemes from day one"
    elif is_property:
        angle = "property companies benefit from early advice on VAT elections, stamp duty, and structure"
    elif is_london:
        angle = "new London businesses often benefit from early advice on company structure and tax planning"
    else:
        angle = "new companies often benefit from getting their accounts and tax set up correctly from the start"

    name_title = company_name.title()
    return (
        f"Hi, I noticed {name_title} was recently incorporated - "
        f"{angle}. Would you be open to a brief chat?"
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

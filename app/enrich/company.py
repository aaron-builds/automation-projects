import json
from datetime import date
from pathlib import Path

from app.models.schemas import Address, EnrichedCompany

FIXTURES = Path(__file__).parents[2] / "fixtures"


def extract_region(address: dict) -> str | None:
    if not address:
        return None
    if locality := address.get("locality"):
        return locality
    if postal_code := address.get("postal_code"):
        return postal_code[:2]
    return None


def enrich(raw_items: list[dict]) -> list[EnrichedCompany]:
    today = date.today()
    enriched = []
    for item in raw_items:
        incorporated_date = date.fromisoformat(item["date_of_creation"])
        address_data = item.get("registered_office_address", {})
        enriched.append(
            EnrichedCompany(
                company_number=item["company_number"],
                company_name=item["company_name"],
                incorporated_date=incorporated_date,
                company_type=item.get("company_type"),
                company_status=item.get("company_status"),
                registered_office_address=Address(**address_data) if address_data else None,
                region=extract_region(address_data),
                company_age_days=(today - incorporated_date).days,
                sic_codes=item.get("sic_codes"),
            )
        )
    return enriched


def main():
    raw = json.loads((FIXTURES / "raw_events.json").read_text())
    companies = enrich(raw["items"])

    for c in companies:
        print(f"{c.company_name} | {c.region} | Age: {c.company_age_days} days")

    output = [json.loads(c.model_dump_json()) for c in companies]
    (FIXTURES / "enriched_companies.json").write_text(json.dumps(output, indent=2, default=str))
    print(f"\nSaved {len(companies)} enriched companies to fixtures/enriched_companies.json")


if __name__ == "__main__":
    main()

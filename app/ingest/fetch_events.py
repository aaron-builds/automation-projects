import json
import logging
import os
import time
from datetime import date, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)

API_KEY = os.getenv("CH_API_KEY")
BASE_URL = "https://api.company-information.service.gov.uk/advanced-search/companies"
OFFICERS_BASE_URL = "https://api.company-information.service.gov.uk/company/{}/officers"
FIXTURES_PATH = Path(__file__).parents[2] / "fixtures" / "raw_events.json"
INTER_REQUEST_DELAY = 0.5  # seconds; keeps well under 600 req/5 min


def fetch_recent_incorporations() -> dict:
    today = date.today()
    thirty_days_ago = today - timedelta(days=30)
    params = {
        "incorporated_from": thirty_days_ago.isoformat(),
        "incorporated_to": today.isoformat(),
        "size": 50,
    }
    response = requests.get(BASE_URL, params=params, auth=(API_KEY, ""))
    response.raise_for_status()
    return response.json()


def _format_director_name(raw: str) -> str:
    if "," in raw:
        surname, _, forenames = raw.partition(",")
        return f"{forenames.strip()} {surname.strip()}".title()
    return raw.title()


def fetch_first_active_director(company_number: str) -> tuple[str, str | None]:
    try:
        url = OFFICERS_BASE_URL.format(company_number)
        response = requests.get(url, auth=(API_KEY, ""), timeout=10)
        response.raise_for_status()
        officers = response.json().get("items", [])
        for officer in officers:
            if officer.get("officer_role") == "director" and "resigned_on" not in officer:
                name = _format_director_name(officer.get("name", "Not listed"))
                appointed = officer.get("appointed_on")
                return name, appointed
        return "Not listed", None
    except Exception as exc:
        log.warning("Officers lookup failed for %s: %s", company_number, exc)
        return "Not listed", None
    finally:
        time.sleep(INTER_REQUEST_DELAY)


def main():
    data = fetch_recent_incorporations()
    items = data.get("items", [])

    hit, miss = 0, 0
    for item in items:
        number = item["company_number"]
        name, appointed = fetch_first_active_director(number)
        item["director_name"] = name
        item["director_appointed"] = appointed
        if name != "Not listed":
            hit += 1
        else:
            miss += 1

    log.info(
        "Director lookup complete: %d found, %d not listed (%.0f%% hit rate)",
        hit, miss, 100 * hit / len(items) if items else 0,
    )

    print(json.dumps(items[:50], indent=2))

    FIXTURES_PATH.parent.mkdir(parents=True, exist_ok=True)
    FIXTURES_PATH.write_text(json.dumps(data, indent=2))
    print(f"\nSaved raw response to {FIXTURES_PATH}")


if __name__ == "__main__":
    main()

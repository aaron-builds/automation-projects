import json
import os
from datetime import date, timedelta
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("CH_API_KEY")
BASE_URL = "https://api.company-information.service.gov.uk/advanced-search/companies"
FIXTURES_PATH = Path(__file__).parents[2] / "fixtures" / "raw_events.json"


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

def main():
    data = fetch_recent_incorporations()

    items = data.get("items", [])
    print(json.dumps(items[:50], indent=2))

    FIXTURES_PATH.parent.mkdir(parents=True, exist_ok=True)
    FIXTURES_PATH.write_text(json.dumps(data, indent=2))
    print(f"\nSaved raw response to {FIXTURES_PATH}")


if __name__ == "__main__":
    main()

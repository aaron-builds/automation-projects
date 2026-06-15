#!/usr/bin/env python3
"""
Find UK accountancy practices for cold outreach using Google Places API.
Usage: python scripts/find_prospects.py [city1 city2 ...]
"""
import csv
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

DEFAULT_CITIES = [
    "Bromley", "Croydon", "Lewisham", "Greenwich", "Hackney",
    "Camden", "Wandsworth", "Battersea", "Southwark", "Lambeth",
]

GENERIC_PREFIXES = {
    "info", "hello", "office", "admin", "contact", "enquiries",
    "enquiry", "support", "team", "mail", "post", "accounts",
    "reception", "noreply", "no-reply", "sales",
}

OUTPUT_PATH = Path("outputs/prospects.csv")
CSV_HEADERS = ["Firm", "City", "Website", "Email", "Email Quality", "Phone"]

PLACES_SEARCH_URL = "https://places.googleapis.com/v1/places:searchText"
PLACES_DETAIL_URL = "https://places.googleapis.com/v1/places/{place_id}"

USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)

EMAIL_RE = re.compile(
    r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"
)


def delay():
    time.sleep(1)


def search_places(city: str) -> list[dict]:
    """Return up to 10 places for 'independent accountants {city}'."""
    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
        "X-Goog-FieldMask": "places.id,places.displayName,places.nationalPhoneNumber",
    }
    body = {
        "textQuery": f"independent accountants {city}",
        "maxResultCount": 10,
        "locationBias": {
            "circle": {
                "center": {"latitude": 51.5074, "longitude": -0.1278},
                "radius": 50000.0,
            }
        },
    }
    try:
        resp = requests.post(PLACES_SEARCH_URL, json=body, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json().get("places", [])
    except Exception as exc:
        print(f"  [warn] Places search failed for {city}: {exc}")
        return []


def get_place_details(place_id: str) -> dict:
    """Fetch websiteUri for a place."""
    url = PLACES_DETAIL_URL.format(place_id=place_id)
    headers = {
        "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
        "X-Goog-FieldMask": "websiteUri",
    }
    delay()
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as exc:
        print(f"  [warn] Details fetch failed for {place_id}: {exc}")
        return {}


def fetch_html(url: str) -> str:
    """Fetch a URL and return HTML text, or empty string on failure."""
    delay()
    try:
        resp = requests.get(
            url,
            headers={"User-Agent": USER_AGENT},
            timeout=10,
            allow_redirects=True,
        )
        resp.raise_for_status()
        return resp.text
    except Exception as exc:
        print(f"  [warn] HTTP fetch failed for {url}: {exc}")
        return ""


def extract_emails_from_html(html: str) -> list[str]:
    """Extract emails: mailto links first, then regex."""
    if not html:
        return []
    soup = BeautifulSoup(html, "html.parser")
    emails = []
    for tag in soup.find_all("a", href=True):
        href = tag["href"]
        if href.lower().startswith("mailto:"):
            addr = href[7:].split("?")[0].strip()
            if addr and EMAIL_RE.match(addr):
                emails.append(addr.lower())
    if not emails:
        emails = [e.lower() for e in EMAIL_RE.findall(html)]
    return list(dict.fromkeys(emails))  # deduplicate, preserve order


def find_email(website: str) -> str:
    """Try homepage then /contact page; return first email found or empty string."""
    if not website:
        return ""
    base = website.rstrip("/")
    for url in [base, base + "/contact"]:
        html = fetch_html(url)
        emails = extract_emails_from_html(html)
        if emails:
            return emails[0]
    return ""


def classify_email(email: str) -> str:
    if not email:
        return "not found"
    local = email.split("@")[0].lower().strip()
    if local in GENERIC_PREFIXES:
        return "generic"
    return "direct"


def normalise_name(name: str) -> str:
    return re.sub(r"\s+", " ", name.strip().lower())


def main():
    if not GOOGLE_MAPS_API_KEY:
        print("Error: GOOGLE_MAPS_API_KEY not set in .env")
        sys.exit(1)

    cities = sys.argv[1:] if len(sys.argv) > 1 else DEFAULT_CITIES
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    seen_firms: set[str] = set()

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()

        for city in cities:
            print(f"\n--- {city} ---")
            places = search_places(city)
            print(f"  Found {len(places)} places")

            for place in places:
                name = place.get("displayName", {}).get("text", "").strip()
                phone = place.get("nationalPhoneNumber", "").strip()
                place_id = place.get("id", "")

                if not name:
                    continue

                key = normalise_name(name)
                if key in seen_firms:
                    print(f"  [skip] {name} (duplicate)")
                    continue
                seen_firms.add(key)

                print(f"  {name} ...", end=" ", flush=True)

                details = get_place_details(place_id)
                website = details.get("websiteUri", "").strip()

                email = find_email(website)
                quality = classify_email(email)

                print(f"{quality} — {email or 'no email'}")

                row = {
                    "Firm": name,
                    "City": city,
                    "Website": website,
                    "Email": email,
                    "Email Quality": quality,
                    "Phone": phone,
                }
                writer.writerow(row)
                f.flush()

    print(f"\nDone. Results saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()

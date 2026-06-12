#!/usr/bin/env python3
import csv
import sys
from datetime import date, datetime
from pathlib import Path

DEFAULT_CSV = "outputs/outreach_tracker.csv"
TODAY = date.today()

GENERIC_PREFIXES = {
    "info", "contact", "admin", "hello", "enquiries", "enquiry",
    "support", "office", "team", "mail", "post", "accounts", "reception",
}

def parse_date(date_str):
    if not date_str or not date_str.strip():
        return None
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(date_str.strip(), fmt).date()
        except ValueError:
            continue
    return None

def days_since(date_str):
    d = parse_date(date_str)
    return (TODAY - d).days if d else None

def is_direct_email(email):
    if not email:
        return False
    local = email.split("@")[0].lower().strip()
    return local not in GENERIC_PREFIXES

def load_rows(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))

def header(title):
    bar = "=" * 60
    print(f"\n{bar}")
    print(f"  {title}")
    print(bar)

def main():
    csv_path = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_CSV
    path = Path(csv_path)
    if not path.exists():
        print(f"Error: file not found — {path}")
        sys.exit(1)

    rows = load_rows(path)

    # --- FOLLOW UP TODAY: Sent, 4–13 days ago ---
    follow_ups = []
    for row in rows:
        status = row.get("Status", "").strip().lower()
        if status == "sent":
            days = days_since(row.get("Date Sent", ""))
            if days is not None and 4 <= days < 14:
                follow_ups.append((days, row))
    follow_ups.sort(key=lambda x: x[0], reverse=True)

    header("FOLLOW UP TODAY")
    if follow_ups:
        print(f"  {'Firm':<32} {'Contact':<18} {'Email':<34} Sent")
        print(f"  {'-'*32} {'-'*18} {'-'*34} ----")
        for days, r in follow_ups:
            print(f"  {r['Firm']:<32} {r['Contact Name']:<18} {r['Email']:<34} {days}d ago")
    else:
        print("  None today")

    # --- FRESH SENDS TODAY: no status, has email, top 5 ---
    fresh = [
        r for r in rows
        if not r.get("Status", "").strip() and r.get("Email", "").strip()
    ]
    fresh.sort(key=lambda r: (0 if is_direct_email(r["Email"]) else 1))
    fresh = fresh[:5]

    header("FRESH SENDS TODAY  (top 5)")
    if fresh:
        print(f"  {'Firm':<32} {'Contact':<18} {'Email':<34} Type")
        print(f"  {'-'*32} {'-'*18} {'-'*34} -------")
        for r in fresh:
            tag = "direct " if is_direct_email(r["Email"]) else "generic"
            print(f"  {r['Firm']:<32} {r['Contact Name']:<18} {r['Email']:<34} {tag}")
    else:
        print("  None today")

    # --- GONE COLD: Sent, 14+ days ago ---
    gone_cold = []
    for row in rows:
        status = row.get("Status", "").strip().lower()
        if status == "sent":
            days = days_since(row.get("Date Sent", ""))
            if days is not None and days >= 14:
                gone_cold.append((days, row))
    gone_cold.sort(key=lambda x: x[0], reverse=True)

    header("GONE COLD  →  mark as Dead")
    if gone_cold:
        print(f"  {'Firm':<32} {'Contact':<18} {'Email':<34} Sent")
        print(f"  {'-'*32} {'-'*18} {'-'*34} ----")
        for days, r in gone_cold:
            print(f"  {r['Firm']:<32} {r['Contact Name']:<18} {r['Email']:<34} {days}d ago")
    else:
        print("  None today")

    print()

if __name__ == "__main__":
    main()

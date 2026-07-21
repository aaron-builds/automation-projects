import csv
import gspread
from pathlib import Path
from google.oauth2.service_account import Credentials

SHEET_ID = "1Nm31a082RhKSt6O9Y8veWEn1FE_OkkIs6lwBMumK0Jw"
CREDS_PATH = Path(__file__).parent.parent / "credentials" / "sheets_service_account.json"
OUTPUT_PATH = Path(__file__).parent.parent / "outputs" / "prospects.csv"

scopes = ["https://www.googleapis.com/auth/spreadsheets"]
creds = Credentials.from_service_account_file(str(CREDS_PATH), scopes=scopes)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1

existing = set(sheet.col_values(4)[1:])

rows = []
with open(OUTPUT_PATH, "r", encoding="utf-8") as f:
    for r in csv.DictReader(f):
        email = r.get("Email", "")
        if email and email not in existing:
            rows.append(["", r["Firm"], r["Firm"], email, r["City"], "", "", r["Website"], ""])

if rows:
    sheet.append_rows(rows, value_input_option="RAW")
    print(f"Pushed {len(rows)} prospects to Sheets.")
else:
    print("Nothing new to push.")
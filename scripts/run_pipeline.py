import sys
import os

# Ensure the project root is on the path so app modules can be imported
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ingest.fetch_events import main as ingest_main
from app.enrich.company import main as enrich_main
from app.score.lead_scorer import main as score_main
from app.deliver.csv_export import main as deliver_main

print("Running step 1: Ingest...")
ingest_main()

print("Running step 2: Enrich...")
enrich_main()

print("Running step 3: Score...")
score_main()

print("Running step 4: Export...")
deliver_main()

print("Pipeline complete. Check outputs/leads_export.csv")

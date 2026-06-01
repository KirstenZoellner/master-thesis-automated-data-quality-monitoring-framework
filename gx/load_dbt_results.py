import json
import sys
import os
from datetime import datetime, timezone
from google.cloud import bigquery

sys.path.append(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

PROJECT_ID = "project-b27d4192-1221-4ffd-b03"
DATASET = "weather_dq"

SCENARIO = sys.argv[1]

RUN_RESULTS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "weather_pipeline",
    "target",
    "run_results.json"
)

with open(RUN_RESULTS_PATH, "r", encoding="utf-8") as file:
    dbt_results = json.load(file)

client = bigquery.Client(project=PROJECT_ID)

rows_to_insert = []

for result in dbt_results["results"]:
    rows_to_insert.append({
        "run_timestamp": datetime.now(timezone.utc).isoformat(),
        "scenario": SCENARIO,
        "tool": "dbt",
        "quality_gate": "dbt_tests",
        "check_name": result["unique_id"].split(".")[2],
        "success": result["status"] == "pass",
        "unexpected_count": result["failures"],
        "table_name": "stg_daily_weather",
        "total_rows": None,
    })

errors = client.insert_rows_json(
    f"{PROJECT_ID}.{DATASET}.dq_results",
    rows_to_insert
)

if errors:
    print("Fehler beim Schreiben nach dq_results:", errors)
else:
    print("dbt-Ergebnisse nach dq_results geschrieben:", len(rows_to_insert))
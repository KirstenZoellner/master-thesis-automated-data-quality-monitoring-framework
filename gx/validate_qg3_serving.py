import great_expectations as gx
import pandas as pd
import sys
import os
from google.cloud import bigquery
from datetime import datetime, timedelta, timezone

sys.path.append(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

from config import SCENARIO as DEFAULT_SCENARIO

SCENARIO = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SCENARIO

PROJECT_ID = "project-b27d4192-1221-4ffd-b03"
DATASET = "weather_dq"

client = bigquery.Client(project=PROJECT_ID)

query = f"""
SELECT *
FROM `{PROJECT_ID}.{DATASET}.stg_daily_weather`
"""

df = client.query(query).to_dataframe()
df["date"] = pd.to_datetime(df["date"], utc=True)
print("Zeilen geladen:", len(df))
print("Maximales Datum:", df["date"].max())
print("Timeliness-Grenze:", datetime.now(timezone.utc) - timedelta(days=3))

context = gx.get_context()

datasource = context.data_sources.add_pandas("pandas_serving_datasource")
data_asset = datasource.add_dataframe_asset(name="stg_daily_weather_asset")

batch_definition = data_asset.add_batch_definition_whole_dataframe(
    "stg_daily_weather_batch"
)

batch = batch_definition.get_batch(batch_parameters={"dataframe": df})

try:
    context.suites.get("qg3_serving_suite")
except Exception:
    context.suites.add(gx.ExpectationSuite(name="qg3_serving_suite"))

validator = context.get_validator(
    batch=batch,
    expectation_suite_name="qg3_serving_suite",
)

# QG3: Serving / BI-Freigabe
validator.expect_column_values_to_not_be_null("date")

validator.expect_column_max_to_be_between(
    column="date",
    min_value=datetime.now(timezone.utc) - timedelta(days=3),
)

validator.expect_column_values_to_be_between(
    column="avg_temp_c",
    min_value=-90,
    max_value=60,
)

validator.expect_column_values_to_be_between(
    column="precipitation_mm",
    min_value=0,
    max_value=1000,
)

result = validator.validate()

rows_to_insert = []

for r in result.results:
    rows_to_insert.append({
        "run_timestamp": datetime.now(timezone.utc).isoformat(),
        "scenario": SCENARIO,
        "tool": "GX",
        "quality_gate": "QG3",
        "check_name": r.expectation_config.type,
        "success": r.success,
        "unexpected_count": r.result.get("unexpected_count"),
        "table_name": "stg_daily_weather",
        "total_rows": len(df),
    })

errors = client.insert_rows_json(
    f"{PROJECT_ID}.{DATASET}.dq_results",
    rows_to_insert
)

if errors:
    print("Fehler beim Schreiben nach dq_results:", errors)
else:
    print("QG3-Ergebnisse nach dq_results geschrieben:", len(rows_to_insert))

print("QG3 Erfolg:", result.success)

for r in result.results:
    print(
        r.expectation_config.type,
        "=>",
        r.success,
        "| unerwartet:",
        r.result.get("unexpected_count"),
    )

if not result.success:
    sys.exit(1)
else:
    sys.exit(0)
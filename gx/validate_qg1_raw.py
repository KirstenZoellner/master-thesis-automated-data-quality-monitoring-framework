import great_expectations as gx
import sys
import os
from google.cloud import bigquery
from datetime import datetime, timezone

sys.path.append(
    os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))
    )
)

from config import SCENARIO as DEFAULT_SCENARIO, WEATHER_TABLES

SCENARIO = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SCENARIO

PROJECT_ID = "project-b27d4192-1221-4ffd-b03"
DATASET = "weather_dq"
TABLE_NAME = WEATHER_TABLES[SCENARIO]

client = bigquery.Client(project=PROJECT_ID)

query = f"""
SELECT *
FROM `{PROJECT_ID}.{DATASET}.{TABLE_NAME}`
"""

df = client.query(query).to_dataframe()

print("Zeilen geladen:", len(df))

# GX 1.x: DataFrame als Batch validieren
context = gx.get_context()

datasource = context.data_sources.add_pandas("pandas_datasource")
data_asset = datasource.add_dataframe_asset(name="daily_weather_faulty_asset")

batch_definition = data_asset.add_batch_definition_whole_dataframe(
    "daily_weather_faulty_batch"
)

batch = batch_definition.get_batch(batch_parameters={"dataframe": df})

try:
    context.suites.get("qg1_raw_suite")
except Exception:
    context.suites.add(gx.ExpectationSuite(name="qg1_raw_suite"))

validator = context.get_validator(
    batch=batch,
    expectation_suite_name="qg1_raw_suite",
)

# QG1 Checks
validator.expect_column_values_to_not_be_null("station_id")
validator.expect_column_values_to_not_be_null("date")
validator.expect_column_values_to_not_be_null("avg_temp_c")

validator.expect_column_values_to_be_between(
    "max_temp_c",
    min_value=-90,
    max_value=60,
)

validator.expect_column_pair_values_A_to_be_greater_than_B(
    column_A="max_temp_c",
    column_B="min_temp_c",
    or_equal=True,
)

result = validator.validate()

rows_to_insert = []

for r in result.results:
    rows_to_insert.append({
        "run_timestamp": datetime.now(timezone.utc).isoformat(),
        "scenario": SCENARIO,
        "tool": "GX",
        "quality_gate": "QG1",
        "check_name": r.expectation_config.type,
        "success": r.success,
        "unexpected_count": r.result.get("unexpected_count"),
        "table_name": TABLE_NAME,
        "total_rows": len(df),
    })

errors = client.insert_rows_json(
    f"{PROJECT_ID}.{DATASET}.dq_results",
    rows_to_insert
)

if errors:
    print("Fehler beim Schreiben nach dq_results:", errors)
else:
    print("QG1-Ergebnisse nach dq_results geschrieben:", len(rows_to_insert))

print("QG1 Erfolg:", result.success)

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
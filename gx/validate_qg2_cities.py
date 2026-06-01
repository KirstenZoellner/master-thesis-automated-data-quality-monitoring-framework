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

from config import SCENARIO as DEFAULT_SCENARIO, CITY_TABLES

SCENARIO = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SCENARIO

PROJECT_ID = "project-b27d4192-1221-4ffd-b03"
DATASET = "weather_dq"
TABLE_NAME = CITY_TABLES[SCENARIO]

client = bigquery.Client(project=PROJECT_ID)

query = f"""
SELECT *
FROM `{PROJECT_ID}.{DATASET}.{TABLE_NAME}`
"""

df = client.query(query).to_dataframe()

print("Zeilen geladen:", len(df))
print(df.columns.tolist())

if "country_code" in df.columns:
    print("country_code Werte:", df["country_code"].value_counts(dropna=False).head(20))

context = gx.get_context()

datasource = context.data_sources.add_pandas("pandas_cities_datasource")
data_asset = datasource.add_dataframe_asset(name="cities_faulty_asset")

batch_definition = data_asset.add_batch_definition_whole_dataframe(
    "cities_faulty_batch"
)

batch = batch_definition.get_batch(batch_parameters={"dataframe": df})

try:
    context.suites.get("qg2_cities_suite")
except Exception:
    context.suites.add(gx.ExpectationSuite(name="qg2_cities_suite"))

validator = context.get_validator(
    batch=batch,
    expectation_suite_name="qg2_cities_suite",
)

VALID_ISO2_CODES = [
    "AD", "AE", "AF", "AG", "AI", "AL", "AM", "AO", "AQ", "AR", "AS", "AT", "AU", "AW", "AX", "AZ",
    "BA", "BB", "BD", "BE", "BF", "BG", "BH", "BI", "BJ", "BL", "BM", "BN", "BO", "BQ", "BR", "BS",
    "BT", "BV", "BW", "BY", "BZ", "CA", "CC", "CD", "CF", "CG", "CH", "CI", "CK", "CL", "CM", "CN",
    "CO", "CR", "CU", "CV", "CW", "CX", "CY", "CZ", "DE", "DJ", "DK", "DM", "DO", "DZ", "EC", "EE",
    "EG", "EH", "ER", "ES", "ET", "FI", "FJ", "FK", "FM", "FO", "FR", "GA", "GB", "GD", "GE", "GF",
    "GG", "GH", "GI", "GL", "GM", "GN", "GP", "GQ", "GR", "GS", "GT", "GU", "GW", "GY", "HK", "HM",
    "HN", "HR", "HT", "HU", "ID", "IE", "IL", "IM", "IN", "IO", "IQ", "IR", "IS", "IT", "JE", "JM",
    "JO", "JP", "KE", "KG", "KH", "KI", "KM", "KN", "KP", "KR", "KW", "KY", "KZ", "LA", "LB", "LC",
    "LI", "LK", "LR", "LS", "LT", "LU", "LV", "LY", "MA", "MC", "MD", "ME", "MF", "MG", "MH", "MK",
    "ML", "MM", "MN", "MO", "MP", "MQ", "MR", "MS", "MT", "MU", "MV", "MW", "MX", "MY", "MZ", "NA",
    "NC", "NE", "NF", "NG", "NI", "NL", "NO", "NP", "NR", "NU", "NZ", "OM", "PA", "PE", "PF", "PG",
    "PH", "PK", "PL", "PM", "PN", "PR", "PS", "PT", "PW", "PY", "QA", "RE", "RO", "RS", "RU", "RW",
    "SA", "SB", "SC", "SD", "SE", "SG", "SH", "SI", "SJ", "SK", "SL", "SM", "SN", "SO", "SR", "SS",
    "ST", "SV", "SX", "SY", "SZ", "TC", "TD", "TF", "TG", "TH", "TJ", "TK", "TL", "TM", "TN", "TO",
    "TR", "TT", "TV", "TW", "TZ", "UA", "UG", "UM", "US", "UY", "UZ", "VA", "VC", "VE", "VG", "VI",
    "VN", "VU", "WF", "WS", "YE", "YT", "ZA", "ZM", "ZW"
]

# QG2: Formatprüfung ISO-2-Code
validator.expect_column_values_to_match_regex(
    column="iso2",
    regex=r"^[A-Z]{2}$"
)

validator.expect_column_values_to_be_in_set(
    column="iso2",
    value_set=VALID_ISO2_CODES
)

if "country_code" in df.columns:
    validator.expect_column_values_to_be_in_set(
        column="country_code",
        value_set=VALID_ISO2_CODES
    )

result = validator.validate()

print("QG2 Erfolg:", result.success)

rows_to_insert = []

for r in result.results:
    rows_to_insert.append({
        "run_timestamp": datetime.now(timezone.utc).isoformat(),
        "scenario": SCENARIO,
        "tool": "GX",
        "quality_gate": "QG2",
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
    print("QG2-Ergebnisse nach dq_results geschrieben:", len(rows_to_insert))

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
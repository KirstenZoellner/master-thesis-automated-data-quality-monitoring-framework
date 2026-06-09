import subprocess
import sys
from pathlib import Path
from datetime import datetime

from config import SCENARIO as DEFAULT_SCENARIO, WEATHER_TABLES

ROOT = Path(__file__).parent
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

log_file = LOG_DIR / "pipeline_run.log"

SCENARIO = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_SCENARIO
WEATHER_TABLE = WEATHER_TABLES[SCENARIO]

print(f"Szenario: {SCENARIO}")
print(f"Wettertabelle: {WEATHER_TABLE}")


def run_step(name, command, cwd):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n=== {name} ===")

    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"\n\n[{timestamp}] === {name} ===\n")
        log.write(f"Command: {command}\n")

        result = subprocess.run(
            command,
            cwd=cwd,
            shell=True,
            text=True,
            capture_output=True
        )

        log.write(result.stdout)
        log.write(result.stderr)

    print(result.stdout)
    print(result.stderr)

    if result.returncode != 0:
        print(f"{name} FEHLGESCHLAGEN")
        return False

    print(f"{name} ERFOLGREICH")
    return True


steps = [
    (
        "dbt run",
        f'dbt run --vars "{{weather_table: {WEATHER_TABLE}}}"',
        ROOT / "weather_pipeline",
    ),
    (
        "dbt test",
        f'dbt test --vars "{{weather_table: {WEATHER_TABLE}}}"',
        ROOT / "weather_pipeline",
    ),
    (
        "dbt Ergebnisse laden",
        f"python load_dbt_results.py {SCENARIO}",
        ROOT / "gx",
    ),
    (
        "GX QG1 Raw Weather",
        f"python validate_qg1_raw.py {SCENARIO}",
        ROOT / "gx",
    ),
    (
        "GX QG2 Cities Format",
        f"python validate_qg2_cities.py {SCENARIO}",
        ROOT / "gx",
    ),
    (
        "GX QG3 Serving",
        f"python validate_qg3_serving.py {SCENARIO}",
        ROOT / "gx",
    ),
]

overall_success = True

for name, command, cwd in steps:
    success = run_step(name, command, cwd)
    if not success:
        overall_success = False
        # In einer produktiven Pipeline würde hier abgebrochen.
        # Für die Evaluation werden alle Gates weiter ausgeführt.
        # break

if overall_success:
    print("\nPIPELINE ERFOLGREICH ABGESCHLOSSEN")
else:
    print("\nPIPELINE ABGEBROCHEN WEGEN QUALITY-GATE-FEHLER")
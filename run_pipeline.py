import subprocess
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

log_file = LOG_DIR / "pipeline_run.log"


def run_step(name, command, cwd):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n=== {name} ===")

    with open(log_file, "a", encoding="utf-8") as log:
        log.write(f"\n\n[{timestamp}] === {name} ===\n")

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
    ("dbt run", "dbt run", ROOT / "weather_pipeline"),
    ("dbt test", "dbt test", ROOT / "weather_pipeline"),
    ("GX QG1 Raw Weather", "python validate_qg1_raw.py", ROOT / "gx"),
    ("GX QG2 Cities Format", "python validate_qg2_cities.py", ROOT / "gx"),
    ("GX QG3 Serving", "python validate_qg3_serving.py", ROOT / "gx"),
]

overall_success = True

for name, command, cwd in steps:
    success = run_step(name, command, cwd)
    if not success:
        overall_success = False
#        break  "Abbruch in echter Pipeline, für Dokumentationszwcke ohne."

if overall_success:
    print("\nPIPELINE ERFOLGREICH ABGESCHLOSSEN")
else:
    print("\nPIPELINE ABGEBROCHEN WEGEN QUALITY-GATE-FEHLER")
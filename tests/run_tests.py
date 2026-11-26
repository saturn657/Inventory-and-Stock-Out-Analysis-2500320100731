"""Run StockWise pytest checks and export a PASS/FAIL/SKIP CSV report."""
from pathlib import Path
import csv
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

BASE_DIR = Path(__file__).resolve().parents[1]
REPORT_DIR = BASE_DIR / "reports"
REPORT_FILE = REPORT_DIR / "test_results.csv"


def main():
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as temp_dir:
        xml_path = Path(temp_dir) / "pytest-results.xml"
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "tests/test_pipeline.py",
             f"--junitxml={xml_path}"],
            cwd=BASE_DIR,
            text=True,
        )
        root = ET.parse(xml_path).getroot()
        rows = []
        for case in root.findall(".//testcase"):
            failure = case.find("failure")
            error = case.find("error")
            skipped = case.find("skipped")
            status = "FAIL" if failure is not None or error is not None else (
                "SKIP" if skipped is not None else "PASS"
            )
            detail = ""
            if failure is not None:
                detail = failure.get("message", "")
            elif error is not None:
                detail = error.get("message", "")
            elif skipped is not None:
                detail = skipped.get("message", "")
            rows.append({
                "test_name": case.get("name", "unknown"),
                "status": status,
                "details": detail.replace("\n", " ").strip(),
            })
        with REPORT_FILE.open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["test_name", "status", "details"])
            writer.writeheader()
            writer.writerows(rows)
        passed = sum(row["status"] == "PASS" for row in rows)
        failed = sum(row["status"] == "FAIL" for row in rows)
        skipped = sum(row["status"] == "SKIP" for row in rows)
        print(f"Test report: {REPORT_FILE.relative_to(BASE_DIR)}")
        print(f"PASS={passed}, FAIL={failed}, SKIP={skipped}")
        if result.returncode != 0:
            raise SystemExit(result.returncode)


if __name__ == "__main__":
    main()

"""
MochaMate Analytics — Main entry point.
Generates dataset (if needed), runs analysis, exports charts and KPI report.

Usage:
    python main.py               # full pipeline
    python main.py --data-only   # generate data only
    python main.py --report-only # run analysis on existing data
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

DATA_PATH = "data/cafe_sales.csv"


def main(data_only: bool = False, report_only: bool = False) -> None:

    if not report_only:
        print("[1/3] Generating synthetic cafe sales data...")
        from data.generate_data import generate
        generate(output=DATA_PATH)

    if not data_only:
        print("[2/3] Running analytics...")
        from src.analysis import CafeAnalytics
        analytics = CafeAnalytics(DATA_PATH)
        kpis = analytics.kpi_summary()

        print("
  ── KPI SUMMARY ──────────────────────────────")
        for k, v in kpis.items():
            print(f"  {k:<25}: {v}")

        kpi_path = Path("output/kpi_summary.json")
        kpi_path.parent.mkdir(parents=True, exist_ok=True)
        with open(kpi_path, "w") as f:
            json.dump(kpis, f, indent=2)
        print(f"  KPIs saved -> {kpi_path}")

        print("[3/3] Generating charts...")
        from src.visualizations import generate_all
        generate_all(analytics)

    print("
Done. Open output/ to view charts and KPI report.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data-only",   action="store_true")
    parser.add_argument("--report-only", action="store_true")
    args = parser.parse_args()
    main(args.data_only, args.report_only)

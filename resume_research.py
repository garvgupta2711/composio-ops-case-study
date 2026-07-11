#!/usr/bin/env python3
"""Resume only unfinished app research and checkpoint each completed record."""

import argparse
import asyncio
import json
from pathlib import Path

from analyze_patterns import analyze_patterns
from generate_report import generate_html_report
from main import ResearchPipeline, apps_dataset, run_verification


FINDINGS_PATH = Path("final_findings.json")
PATTERNS_PATH = Path("patterns.json")
VERIFICATION_PATH = Path("verification_report.json")
REPORT_PATH = Path("report.html")


def load_findings() -> dict[int, dict]:
    with FINDINGS_PATH.open(encoding="utf-8") as file:
        return {record["id"]: record for record in json.load(file)}


def is_pending(record: dict | None) -> bool:
    if record is None:
        return True
    return (
        record.get("buildability_verdict") == "UNKNOWN"
        or "quota exhausted" in record.get("main_blocker", "").lower()
        or record.get("category_one_liner") == "Not processed"
    )


def save_findings(records_by_id: dict[int, dict]) -> None:
    ordered = [records_by_id[app["id"]] for app in apps_dataset if app["id"] in records_by_id]
    temp_path = FINDINGS_PATH.with_suffix(".json.tmp")
    with temp_path.open("w", encoding="utf-8") as file:
        json.dump(ordered, file, indent=2, ensure_ascii=False)
    temp_path.replace(FINDINGS_PATH)


def regenerate_outputs(records_by_id: dict[int, dict]) -> None:
    records = [records_by_id[app["id"]] for app in apps_dataset]
    verified = run_verification(records)
    save_findings({record["id"]: record for record in verified})

    patterns = analyze_patterns(verified)
    with PATTERNS_PATH.open("w", encoding="utf-8") as file:
        json.dump(patterns, file, indent=2, ensure_ascii=False)

    with VERIFICATION_PATH.open(encoding="utf-8") as file:
        verification = json.load(file)
    REPORT_PATH.write_text(generate_html_report(verified, patterns, verification), encoding="utf-8")


async def resume(dry_run: bool) -> int:
    records_by_id = load_findings()
    pending_apps = [app for app in apps_dataset if is_pending(records_by_id.get(app["id"]))]
    print(f"Found {len(pending_apps)} unfinished apps.")

    if dry_run or not pending_apps:
        for app in pending_apps:
            print(f"  {app['id']:>3}: {app['name']}")
        return 0

    pipeline = ResearchPipeline()
    for index, app in enumerate(pending_apps, start=1):
        print(f"Resuming {index}/{len(pending_apps)}: {app['name']}")
        record = await pipeline.process_app(app)
        records_by_id[app["id"]] = record
        save_findings(records_by_id)

        if record.get("main_blocker") == "OpenAI API quota exhausted":
            print("Stopped without changing remaining records: add API credits or raise the usage limit, then rerun this command.")
            return 2

    regenerate_outputs(records_by_id)
    print("All 100 apps are processed and report.html has been regenerated.")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Resume unfinished Composio app research.")
    parser.add_argument("--dry-run", action="store_true", help="List unfinished apps without calling the API.")
    args = parser.parse_args()
    raise SystemExit(asyncio.run(resume(args.dry_run)))

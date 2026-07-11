#!/usr/bin/env python3
"""Import cited ChatGPT/Claude verification results and regenerate the case study."""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from generate_report import generate_report


FINDINGS_PATH = Path("final_findings.json")
OUTPUT_PATH = Path("verification_report.json")
REQUIRED_FIELDS = {
    "app_id", "app_name", "auth_methods_verified", "accessibility_tier_verified",
    "api_surface_verified", "buildability_verdict_verified", "evidence_url_verified",
    "overall_status", "evidence_summary", "corrections", "evidence_urls",
}
VALID_STATUSES = {"Correct", "Partial", "Incorrect", "Unverifiable"}


def completed_app_ids() -> set[int]:
    with FINDINGS_PATH.open(encoding="utf-8") as file:
        return {
            record["id"] for record in json.load(file)
            if record.get("buildability_verdict") != "UNKNOWN"
        }


def main(input_path: Path) -> None:
    with input_path.open(encoding="utf-8") as file:
        payload = json.load(file)

    records = payload.get("verified_apps")
    if not isinstance(records, list):
        raise ValueError("external_verification.json must contain a verified_apps array.")

    expected_ids = completed_app_ids()
    seen_ids: set[int] = set()
    for record in records:
        missing = REQUIRED_FIELDS - set(record)
        if missing:
            raise ValueError(f"Record {record.get('app_id', 'unknown')} is missing: {', '.join(sorted(missing))}")
        if record["app_id"] not in expected_ids:
            raise ValueError(f"Record ID {record['app_id']} is not in the completed research dataset.")
        if record["app_id"] in seen_ids:
            raise ValueError(f"Duplicate verification record for ID {record['app_id']}.")
        if record["overall_status"] not in VALID_STATUSES:
            raise ValueError(f"Invalid overall_status for ID {record['app_id']}.")
        if not isinstance(record["evidence_urls"], list):
            raise ValueError(f"evidence_urls must be a list for ID {record['app_id']}.")
        seen_ids.add(record["app_id"])

    field_names = (
        "auth_methods_verified", "accessibility_tier_verified",
        "api_surface_verified", "buildability_verdict_verified",
    )
    evaluated = [record[field] for record in records for field in field_names if record[field] is not None]
    passed = sum(value is True for value in evaluated)
    accuracy = round(100 * passed / len(evaluated), 1) if evaluated else 0.0
    evidence_count = sum(bool(record["evidence_urls"]) and record["evidence_url_verified"] for record in records)

    report = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "verification_method": "External LLM-assisted verification with official-documentation citations",
        "provider": payload.get("provider", "External LLM"),
        "sample_size": len(records),
        "source_record_count": len(expected_ids),
        "evidence_retrieved_count": evidence_count,
        "field_checks_evaluated": len(evaluated),
        "field_checks_passed": passed,
        "accuracy_percentage": accuracy,
        "confidence_level": "High" if len(records) == len(expected_ids) and evidence_count == len(expected_ids) and accuracy >= 85 else "Medium" if records else "Low",
        "verified_apps": records,
    }
    with OUTPUT_PATH.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    generate_report()
    print(f"Imported {len(records)} external verification records from {input_path}.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python import_external_verification.py external_verification.json")
    main(Path(sys.argv[1]))

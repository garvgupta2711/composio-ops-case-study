#!/usr/bin/env python3
"""Run the 50-app research subset and regenerate the case-study page."""

import asyncio
import json
import os

from dotenv import load_dotenv

load_dotenv()


async def run_research_pipeline() -> None:
    from analyze_patterns import analyze_patterns
    from main import ResearchPipeline, apps_dataset, run_verification
    from modern_report import generate_html_report

    apps = apps_dataset[:50]
    print(f"Starting research for {len(apps)} apps.")
    pipeline = ResearchPipeline()
    raw_results = await asyncio.gather(*(pipeline.process_app(app) for app in apps))
    results = run_verification(raw_results)

    with open("final_findings.json", "w", encoding="utf-8") as file:
        json.dump(results, file, indent=2, ensure_ascii=False)

    patterns = analyze_patterns(results)
    with open("patterns.json", "w", encoding="utf-8") as file:
        json.dump(patterns, file, indent=2, ensure_ascii=False)

    if os.path.exists("verification_report.json"):
        with open("verification_report.json", encoding="utf-8") as file:
            verification = json.load(file)
    else:
        verification = {"verified_apps": [], "accuracy_percentage": 0}

    with open("report.html", "w", encoding="utf-8") as file:
        file.write(generate_html_report(results, patterns, verification))

    print("Research, pattern analysis, and report generation are complete.")
    print("Import external verification results separately with import_external_verification.py.")


if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is required to run a new research pass.")
    asyncio.run(run_research_pipeline())

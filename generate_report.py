"""Entry point for generating the submission case-study page."""

import json

from modern_report import generate_html_report


def generate_report() -> str:
    with open("final_findings.json", encoding="utf-8") as file:
        findings = json.load(file)
    with open("patterns.json", encoding="utf-8") as file:
        patterns = json.load(file)
    with open("verification_report.json", encoding="utf-8") as file:
        verification = json.load(file)

    html = generate_html_report(findings, patterns, verification)
    with open("report.html", "w", encoding="utf-8") as file:
        file.write(html)
    print("Report generated: report.html")
    return html


if __name__ == "__main__":
    generate_report()

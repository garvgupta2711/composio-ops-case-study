#!/usr/bin/env python3
"""Apply explicit, cited correction proposals from the imported ChatGPT review."""

import json
from pathlib import Path


FINDINGS_PATH = Path("final_findings.json")
VERIFICATION_PATH = Path("verification_report.json")

# These changes are transcribed from the `corrections` field in the imported
# external review. Keeping them explicit makes the refinement pass auditable.
CORRECTIONS = {
    4: {"accessibility_tier": "Tier 1: Fully Self-Serve", "buildability_verdict": "YES", "main_blocker": "None"},
    6: {"accessibility_tier": "Tier 1: Fully Self-Serve", "buildability_verdict": "YES", "main_blocker": "None"},
    9: {"accessibility_tier": "Tier 1: Fully Self-Serve", "buildability_verdict": "YES", "main_blocker": "None"},
    16: {"accessibility_tier": "Tier 1: Fully Self-Serve", "buildability_verdict": "YES", "main_blocker": "None"},
    17: {"auth_methods": ["API Key", "OAuth2"], "api_surface": "GraphQL"},
    19: {"auth_methods": ["OAuth2", "API Key / Basic Auth"]},
    20: {"auth_methods": ["API Token", "Basic Auth"], "accessibility_tier": "Tier 1: Fully Self-Serve", "buildability_verdict": "YES", "main_blocker": "None"},
    26: {"auth_methods": ["OAuth2", "Bot Token"]},
    29: {"auth_methods": ["OAuth2", "API Key / Basic Auth"]},
    30: {"auth_methods": ["API Key + Secret", "JWT"]},
    31: {"auth_methods": ["OAuth2", "Developer Token"], "accessibility_tier": "Tier 2: Self-Serve + Approval", "buildability_verdict": "MAYBE", "main_blocker": "Developer token approval required"},
    34: {"auth_methods": ["OAuth2"]},
    38: {"accessibility_tier": "Tier 2: Self-Serve + Approval", "buildability_verdict": "MAYBE", "main_blocker": "App review required for production access"},
    40: {"auth_methods": ["API Key"]},
    41: {"auth_methods": ["OAuth2", "API Access Token"]},
    42: {"auth_methods": ["API Key / Consumer Secret"]},
    43: {"auth_methods": ["OAuth2", "API Token"]},
    45: {"auth_methods": ["Token", "OAuth 1.0a"]},
    46: {"auth_methods": ["API Key", "OAuth2"]},
    47: {"auth_methods": ["OAuth2"]},
    48: {"auth_methods": ["OAuth2", "Access Token"]},
    49: {"auth_methods": ["OAuth2", "AWS IAM Signatures"]},
    50: {"auth_methods": ["API Key"]},
}


def main() -> None:
    with FINDINGS_PATH.open(encoding="utf-8") as file:
        findings = json.load(file)
    with VERIFICATION_PATH.open(encoding="utf-8") as file:
        verification = json.load(file)

    reviews = {record["app_id"]: record for record in verification["verified_apps"]}
    for record in findings:
        app_id = record["id"]
        if app_id not in CORRECTIONS:
            continue
        review = reviews[app_id]
        record.update(CORRECTIONS[app_id])
        record["refinement_note"] = review["corrections"]
        record["refinement_evidence_urls"] = review["evidence_urls"]
        record["refined_from_external_verification"] = True

    with FINDINGS_PATH.open("w", encoding="utf-8") as file:
        json.dump(findings, file, indent=2, ensure_ascii=False)
    print(f"Applied {len(CORRECTIONS)} explicit external-verification corrections.")


if __name__ == "__main__":
    main()

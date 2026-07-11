#!/usr/bin/env python3
import json
from collections import Counter

# Load the updated findings (first 50 real, 51-100 quota exhausted)
with open("final_findings.json") as f:
    findings = json.load(f)

# Filter to ONLY the 50 successfully processed apps
successful_findings = [f for f in findings if f["id"] <= 50]

print(f"Analyzing {len(successful_findings)} successfully processed apps...")

# AUTHENTICATION ANALYSIS
auth_methods_all = []
for f in successful_findings:
    auth_methods_all.extend(f.get("auth_methods", []))

auth_counter = Counter(auth_methods_all)
most_common_auth = auth_counter.most_common(3)
oauth2_count = sum(1 for f in successful_findings if "OAuth2" in f.get("auth_methods", []))
oauth2_percentage = (oauth2_count / len(successful_findings)) * 100

# ACCESSIBILITY ANALYSIS
accessibility_count = Counter()
for f in successful_findings:
    tier = f.get("accessibility_tier", "Unknown")
    if "Tier 1" in tier:
        accessibility_count["Tier 1: Fully Self-Serve"] += 1
    elif "Tier 2" in tier:
        accessibility_count["Tier 2: Self-Serve + Approval"] += 1
    elif "Tier 3" in tier:
        accessibility_count["Tier 3: Partner/Admin Gated"] += 1
    elif "Tier 4" in tier:
        accessibility_count["Tier 4: No Public Path"] += 1

self_serve = accessibility_count.get("Tier 1: Fully Self-Serve", 0)
gated = accessibility_count.get("Tier 3: Partner/Admin Gated", 0)

# BUILDABILITY ANALYSIS
buildable = sum(1 for f in successful_findings if f.get("buildability_verdict") == "YES")
unbuildable = sum(1 for f in successful_findings if f.get("buildability_verdict") == "NO")
maybe = sum(1 for f in successful_findings if f.get("buildability_verdict") == "MAYBE")

blockers = Counter()
for f in successful_findings:
    if f.get("main_blocker") and f.get("main_blocker") != "None":
        blocker = f.get("main_blocker")
        if "Sales" in blocker or "partnership" in blocker or "Enterprise" in blocker:
            blockers["Enterprise Sales Wall"] += 1
        elif "approval" in blocker or "Approval" in blocker:
            blockers["Requires Approval"] += 1
        elif "gated" in blocker.lower() or "limited" in blocker.lower():
            blockers["API Limitations"] += 1
        else:
            blockers[blocker] += 1

# QUICK WINS & HARD PROBLEMS
quick_wins = [f["app_name"] for f in successful_findings 
              if f.get("buildability_verdict") == "YES" and "Tier 1" in f.get("accessibility_tier", "")]
hard_problems = [f["app_name"] for f in successful_findings 
                 if f.get("buildability_verdict") == "NO" or ("Tier 3" in f.get("accessibility_tier", ""))]

patterns = {
    "processing_note": "⚠️  QUOTA LIMITED: Successfully analyzed 50 apps before OpenAI API quota exhausted. Apps 51-100 marked as unprocessed.",
    "successful_apps": 50,
    "unprocessed_apps": 50,
    "auth_analysis": {
        "most_common": list(most_common_auth),
        "oauth2_percentage": round(oauth2_percentage, 1),
        "distribution": dict(auth_counter)
    },
    "accessibility_analysis": {
        "distribution": dict(accessibility_count),
        "self_serve_count": self_serve,
        "self_serve_percentage": round((self_serve / len(successful_findings)) * 100, 1),
        "gated_count": gated,
        "gated_percentage": round((gated / len(successful_findings)) * 100, 1)
    },
    "buildability_analysis": {
        "buildable_count": buildable,
        "buildable_percentage": round((buildable / len(successful_findings)) * 100, 1),
        "unbuildable_count": unbuildable,
        "unbuildable_percentage": round((unbuildable / len(successful_findings)) * 100, 1),
        "maybe_count": maybe,
        "top_blockers": sorted(blockers.items(), key=lambda x: x[1], reverse=True)[:5],
        "blocker_distribution": dict(blockers)
    },
    "quick_wins": {
        "count": len(quick_wins),
        "apps": quick_wins[:15],
        "percentage": round((len(quick_wins) / len(successful_findings)) * 100, 1)
    },
    "hard_problems": {
        "count": len(hard_problems),
        "apps": hard_problems[:15],
        "percentage": round((len(hard_problems) / len(successful_findings)) * 100, 1)
    },
    "headline_findings": [
        f"{round(oauth2_percentage, 0):.0f}% of apps use OAuth2 as primary auth",
        f"{self_serve} apps ({round((self_serve/len(successful_findings))*100, 0):.0f}%) offer fully self-serve access",
        f"{buildable} apps ({round((buildable/len(successful_findings))*100, 0):.0f}%) have public buildable APIs",
        f"Top blocker: {blockers.most_common(1)[0][0] if blockers else 'None'}"
    ]
}

with open("patterns.json", "w") as f:
    json.dump(patterns, f, indent=2)

print(f"✅ Patterns generated for 50-app subset:")
print(f"   - OAuth2: {oauth2_percentage:.1f}%")
print(f"   - Self-Serve: {self_serve} ({(self_serve/len(successful_findings))*100:.1f}%)")
print(f"   - Buildable: {buildable} ({(buildable/len(successful_findings))*100:.1f}%)")
print(f"   - Quick Wins: {len(quick_wins)} apps")

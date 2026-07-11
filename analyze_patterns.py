"""
Pattern Analysis Module - Extract insights from 100 app research
Identifies trends across auth methods, accessibility, blockers, and buildability
"""

import json
from typing import List, Dict, Tuple
from collections import Counter

def analyze_patterns(results: List[dict]) -> Dict:
    """
    Extract patterns from research results:
    1. Auth method dominance
    2. Accessibility tier distribution  
    3. Main blockers preventing buildability
    4. Buildability by category
    5. Quick wins vs hard problems
    """
    
    print("\n📊 PATTERN ANALYSIS - Extracting insights from 100 apps...\n")
    
    # 1. Auth Method Distribution
    auth_counter = Counter()
    for r in results:
        for auth in r.get("auth_methods", []):
            auth_counter[auth] += 1
    
    auth_patterns = {
        "most_common": auth_counter.most_common(3),
        "distribution": dict(auth_counter),
        "oauth_percentage": (auth_counter.get("OAuth2", 0) / len(results)) * 100
    }
    
    print(f"🔐 AUTH PATTERNS:")
    print(f"   • OAuth2 dominance: {auth_patterns['oauth_percentage']:.1f}%")
    print(f"   • Top 3 methods: {', '.join([f'{m} ({c})' for m, c in auth_patterns['most_common']])}")
    
    # 2. Accessibility Distribution
    tier_counter = Counter()
    for r in results:
        tier = r.get("accessibility_tier", "Unknown")
        # Normalize tier names
        if "Fully Self-Serve" in tier:
            tier = "Tier 1: Fully Self-Serve"
        elif "Friction" in tier:
            tier = "Tier 2: Self-Serve with Friction"
        elif "Partner" in tier or "Gated" in tier:
            tier = "Tier 3: Partner/Admin Gated"
        else:
            tier = "Tier 4: No Public Path"
        tier_counter[tier] += 1
    
    tier_patterns = {
        "distribution": dict(tier_counter),
        "self_serve_count": tier_counter.get("Tier 1: Fully Self-Serve", 0),
        "self_serve_percentage": (tier_counter.get("Tier 1: Fully Self-Serve", 0) / len(results)) * 100,
        "gated_count": tier_counter.get("Tier 3: Partner/Admin Gated", 0),
        "gated_percentage": (tier_counter.get("Tier 3: Partner/Admin Gated", 0) / len(results)) * 100,
    }
    
    print(f"\n🚪 ACCESSIBILITY PATTERNS:")
    print(f"   • Self-Serve (Tier 1): {tier_patterns['self_serve_count']} apps ({tier_patterns['self_serve_percentage']:.1f}%)")
    print(f"   • Gated (Tier 3): {tier_patterns['gated_count']} apps ({tier_patterns['gated_percentage']:.1f}%)")
    print(f"   • Full distribution: {dict(tier_counter)}")
    
    # 3. Main Blockers
    blocker_counter = Counter()
    buildable_count = 0
    unbuildable_reasons = []
    
    for r in results:
        if r.get("buildability_verdict") == "YES":
            buildable_count += 1
        else:
            blocker = r.get("main_blocker", "Unknown")
            if blocker and blocker != "None":
                # Categorize blocker
                if "Sales" in blocker or "Enterprise" in blocker or "Partner" in blocker:
                    blocker = "Enterprise/Sales Wall"
                elif "Auth" in blocker or "authentication" in blocker.lower():
                    blocker = "Auth Complexity"
                elif "paid" in blocker.lower() or "payment" in blocker.lower():
                    blocker = "Paid Plan Required"
                elif "API" in blocker or "documentation" in blocker.lower():
                    blocker = "API Limitations / Poor Docs"
                
                blocker_counter[blocker] += 1
                unbuildable_reasons.append((r.get("app_name"), blocker))
    
    blocker_patterns = {
        "buildable_count": buildable_count,
        "buildable_percentage": (buildable_count / len(results)) * 100,
        "unbuildable_count": len(results) - buildable_count,
        "top_blockers": blocker_counter.most_common(5),
        "blocker_distribution": dict(blocker_counter)
    }
    
    print(f"\n✅ BUILDABILITY PATTERNS:")
    print(f"   • Buildable TODAY: {blocker_patterns['buildable_count']} apps ({blocker_patterns['buildable_percentage']:.1f}%)")
    print(f"   • Blockers exist: {blocker_patterns['unbuildable_count']} apps")
    print(f"   • Top blocker: {blocker_patterns['top_blockers'][0][0] if blocker_patterns['top_blockers'] else 'N/A'}")
    
    # 4. Quick Wins (self-serve + buildable)
    quick_wins = [
        r for r in results 
        if "Tier 1" in r.get("accessibility_tier", "") 
        and r.get("buildability_verdict") == "YES"
    ]
    
    # 5. Hard Problems (gated + unbuildable)
    hard_problems = [
        r for r in results 
        if "Tier 3" in r.get("accessibility_tier", "") 
        or r.get("buildability_verdict") == "NO"
    ]
    
    patterns = {
        "auth_analysis": auth_patterns,
        "accessibility_analysis": tier_patterns,
        "buildability_analysis": blocker_patterns,
        "quick_wins": {
            "count": len(quick_wins),
            "apps": [r.get("app_name") for r in quick_wins[:10]],  # Top 10
            "percentage": (len(quick_wins) / len(results)) * 100
        },
        "hard_problems": {
            "count": len(hard_problems),
            "apps": [r.get("app_name") for r in hard_problems[:10]],  # Top 10
            "percentage": (len(hard_problems) / len(results)) * 100
        },
        "headline_findings": [
            f"{auth_patterns['oauth_percentage']:.0f}% of apps use OAuth2 - the dominant auth standard",
            f"{tier_patterns['self_serve_percentage']:.0f}% have self-serve developer paths - excellent for agents",
            f"{blocker_patterns['buildable_percentage']:.0f}% are ready to build today",
            f"Top blocker: {blocker_patterns['top_blockers'][0][0] if blocker_patterns['top_blockers'] else 'Enterprise walls'} (affects {blocker_patterns['top_blockers'][0][1] if blocker_patterns['top_blockers'] else 0} apps)",
            f"{len(quick_wins)} quick wins: self-serve + buildable = immediate toolkit candidates"
        ]
    }
    
    print(f"\n🎯 QUICK WINS vs HARD PROBLEMS:")
    print(f"   • Immediate toolkit candidates: {patterns['quick_wins']['count']} apps")
    print(f"   • Need partnership outreach: {patterns['hard_problems']['count']} apps")
    
    return patterns

if __name__ == "__main__":
    with open("final_findings.json", "r") as f:
        results = json.load(f)
    
    patterns = analyze_patterns(results)
    with open("patterns.json", "w") as f:
        json.dump(patterns, f, indent=2)
    
    print(f"\n✓ Patterns saved to patterns.json")

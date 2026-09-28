#!/usr/bin/env python3
"""Keep the instruction load per task within what a model can actually retain.

Progressive disclosure only works if the "always loaded" set stays small and each task's required
set stays bounded. This script measures both and fails when a threshold is crossed, so growth in
the template shows up as a red check instead of as a quietly worse agent.

Token estimate: chars / 3.6 (conservative for English markdown with code). Thresholds are in
`budgets` below and are deliberately editable — raise them only with a reason in the commit.

Usage: scripts/check-context-budget.py [--report]
"""
import glob
import json
import os
import sys

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CHARS_PER_TOKEN = 3.6

budgets = {
    "always_loaded_total": 14000,   # AGENTS.md + every file the adapters load unconditionally
    "single_file": 5000,            # any one rule/skill/pattern file
    "skill_frontmatter_desc_words": 120,
    "per_area_total": 22000,        # always_loaded + requires[] of one impact-map area
}

ALWAYS = json.load(open(os.path.join(ROOT, "opencode.json"), encoding="utf-8"))["instructions"]


def toks(path):
    return int(len(open(os.path.join(ROOT, path), encoding="utf-8", errors="replace").read())
               / CHARS_PER_TOKEN)


def main():
    report = "--report" in sys.argv
    failures = []
    always_total = sum(toks(p) for p in ALWAYS)
    print(f"always-loaded set ({len(ALWAYS)} files): ~{always_total} tokens "
          f"[budget {budgets['always_loaded_total']}]")
    for p in ALWAYS:
        print(f"  {toks(p):>6}  {p}")
    if always_total > budgets["always_loaded_total"]:
        failures.append(f"always-loaded set is ~{always_total} tokens > "
                        f"{budgets['always_loaded_total']} — move detail out of the entry files "
                        f"into skills/patterns loaded on demand")

    big = []
    for path in glob.glob(os.path.join(ROOT, "ai", "**", "*.md"), recursive=True):
        rel = os.path.relpath(path, ROOT)
        t = toks(rel)
        if t > budgets["single_file"]:
            big.append((t, rel))
    for t, rel in sorted(big, reverse=True):
        failures.append(f"{rel} is ~{t} tokens > {budgets['single_file']} — split into "
                        f"references/ or trim")

    data = yaml.safe_load(open(os.path.join(ROOT, "ai", "impact-map.yaml"), encoding="utf-8"))
    base_req = set(data.get("always_required", []))
    print("\nper-area load (always-loaded + required rule files):")
    for rule in data["rules"]:
        req = set(rule.get("requires", [])) | base_req
        extra = sum(toks(p) for p in req if p not in ALWAYS and os.path.exists(os.path.join(ROOT, p)))
        total = always_total + extra
        flag = " <-- over budget" if total > budgets["per_area_total"] else ""
        print(f"  {total:>6}  {rule['id']:<14} (+{extra} for {len(req)} required files){flag}")
        if total > budgets["per_area_total"]:
            failures.append(f"area `{rule['id']}` needs ~{total} tokens > "
                            f"{budgets['per_area_total']} — the agent is likely to drop rules "
                            f"mid-task; reduce `requires` or the always-loaded set")

    if failures:
        print("\ncheck-context-budget: FAIL")
        for f in failures:
            print(f"::error:: {f}")
        sys.exit(1)
    print("\ncheck-context-budget: ok")


if __name__ == "__main__":
    main()

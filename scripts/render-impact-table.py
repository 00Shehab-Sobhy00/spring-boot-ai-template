#!/usr/bin/env python3
"""Render the impact table in ai/skills/sync-docs/SKILL.md from ai/impact-map.yaml.

The YAML is the single source; the markdown table between the markers is GENERATED.
Usage:
  scripts/render-impact-table.py            # rewrite the table in place
  scripts/render-impact-table.py --check    # exit 1 if the table is stale (CI)
"""
import os
import re
import sys

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MAP = os.path.join(ROOT, "ai", "impact-map.yaml")
SKILL = os.path.join(ROOT, "ai", "skills", "sync-docs", "SKILL.md")
BEGIN = "<!-- BEGIN GENERATED: impact-table (source: ai/impact-map.yaml) -->"
END = "<!-- END GENERATED: impact-table -->"


def humanize_trigger(rule):
    if rule.get("scope") == "content":
        return f"Added line containing `{rule['code']}`"
    return "`" + rule["code"].replace("|", "` / `") + "`"


def render(data):
    lines = [
        BEGIN,
        "",
        "| Changed (path or construct) | Update | Rule tokens required in the AI Run Report | CI |",
        "| --- | --- | --- | --- |",
    ]
    for r in data["rules"]:
        req = ", ".join(f"`{p}`" for p in r.get("requires", [])) or "—"
        human = " ".join(r["human"].split())
        lines.append(f"| {humanize_trigger(r)} | {human} | {req} | {r['severity']} |")
    for g in data.get("guidance", []):
        human = " ".join(g["human"].split())
        lines.append(f"| {g['changed']} | {human} | — | guidance |")
    lines += ["", END]
    return "\n".join(lines)


def main():
    data = yaml.safe_load(open(MAP, encoding="utf-8"))
    text = open(SKILL, encoding="utf-8").read()
    if BEGIN not in text or END not in text:
        print(f"markers {BEGIN!r} / {END!r} not found in {SKILL}")
        sys.exit(2)
    new_block = render(data)
    pattern = re.compile(re.escape(BEGIN) + r".*?" + re.escape(END), re.S)
    new_text = pattern.sub(lambda _: new_block, text)
    if "--check" in sys.argv:
        if new_text != text:
            print("render-impact-table: ai/skills/sync-docs/SKILL.md impact table is STALE — "
                  "run scripts/render-impact-table.py and commit")
            sys.exit(1)
        print("render-impact-table: table is in sync with ai/impact-map.yaml")
        return
    open(SKILL, "w", encoding="utf-8").write(new_text)
    print("render-impact-table: wrote table")


if __name__ == "__main__":
    main()

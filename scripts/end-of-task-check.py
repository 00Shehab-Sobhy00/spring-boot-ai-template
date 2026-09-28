#!/usr/bin/env python3
"""End-of-task nudge: code changed in a documented area, but its docs did not.

The ONE implementation behind every tool's stop hook (Claude Code, Cursor, Copilot, opencode).
Each adapter only calls this script with its own --format; the logic lives here and the areas
come from ai/impact-map.yaml (single source), so no adapter repeats a rule.

It is a nudge, not a gate: it asks the agent once per new set of changes to run
`ai/skills/sync-docs/`, then lets it stop. The hard gate stays in CI (scripts/check-docs-impact.py).

Changed files = committed since the merge-base with origin/main + staged + unstaged + untracked.

Usage: scripts/end-of-task-check.py [--format text|claude|cursor|copilot]
  text     message on stdout, exit 1 when docs are missing (opencode plugin, humans)
  claude   Stop hook: message on stderr, exit 2 (Claude Code feeds it back and continues)
  cursor   stop hook: {"followup_message": ...} on stdout
  copilot  agentStop hook: {"decision": "block", "reason": ...} on stdout
"""
import hashlib
import json
import os
import re
import subprocess
import sys

import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MAP = os.path.join(ROOT, "ai", "impact-map.yaml")
STATE = os.path.join(ROOT, ".ai-run", "end-of-task.state")  # .ai-run/ is git-ignored
BASE = "origin/main"


def git(*args):
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)
    return r.stdout if r.returncode == 0 else ""


def changed_files():
    files = set()
    merge_base = git("merge-base", BASE, "HEAD").strip()
    if merge_base:
        files.update(git("diff", "--name-only", merge_base, "HEAD").split())
    files.update(git("diff", "--name-only", "HEAD").split())                      # staged + unstaged
    files.update(git("ls-files", "--others", "--exclude-standard").split())       # untracked
    return sorted(files)


def missing_docs(files):
    """Path-triggered impact-map rules whose code matched and whose docs did not."""
    rules = yaml.safe_load(open(MAP, encoding="utf-8"))["rules"]
    missing = []
    for rule in rules:
        if rule.get("scope") or not rule.get("code"):
            continue  # content/enforcement rules need the diff itself — CI covers those
        code, docs = re.compile(rule["code"]), re.compile(rule["docs"])
        hits = [f for f in files if code.search(f)]
        if hits and not any(docs.search(f) for f in files):
            missing.append((rule["id"], " ".join(rule["human"].split()), hits[0]))
    return missing


def fingerprint(files):
    """Same changes as the last nudge → stay quiet. Doubles as every tool's loop guard."""
    h = hashlib.sha256()
    for f in files:
        h.update(f.encode())
        path = os.path.join(ROOT, f)
        if os.path.isfile(path):
            h.update(open(path, "rb").read())
    return h.hexdigest()


def already_nudged(fp):
    try:
        return open(STATE, encoding="utf-8").read().strip() == fp
    except OSError:
        return False


def remember(fp):
    os.makedirs(os.path.dirname(STATE), exist_ok=True)
    with open(STATE, "w", encoding="utf-8") as fh:
        fh.write(fp)


def message(missing):
    lines = ["Code changed in a documented area, but its docs did not:"]
    lines += [f"- {rid} (e.g. {example}): update {human}" for rid, human, example in missing]
    lines.append("Run ai/skills/sync-docs/ now and finish with its close-out block and the AI Run "
                 "Report (ai/CAPACITY.md). If the change is genuinely doc-neutral, say so and why.")
    return "\n".join(lines)


def main():
    fmt = sys.argv[sys.argv.index("--format") + 1] if "--format" in sys.argv else "text"
    if not sys.stdin.isatty():
        sys.stdin.read()  # hook payloads arrive on stdin; nothing in them is needed here

    files = changed_files()
    missing = missing_docs(files)
    if not missing:
        print("{}" if fmt in ("cursor", "copilot") else "", end="")
        return 0
    fp = fingerprint(files)
    if already_nudged(fp):
        print("{}" if fmt in ("cursor", "copilot") else "", end="")
        return 0
    remember(fp)

    text = message(missing)
    if fmt == "claude":
        print(text, file=sys.stderr)
        return 2
    if fmt == "cursor":
        print(json.dumps({"followup_message": text}))
        return 0
    if fmt == "copilot":
        print(json.dumps({"decision": "block", "reason": text}))
        return 0
    print(text)
    return 1


if __name__ == "__main__":
    if os.name == "nt":
        sys.stdout.reconfigure(encoding="utf-8")  # see ai/PROJECT_MEMORY.md → Environment Quirks
        sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())

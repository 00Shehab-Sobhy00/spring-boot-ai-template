#!/usr/bin/env python3
"""Parse and enforce the AI Run Report (format: ai/CAPACITY.md).

What this catches, in order of how often it fires:
  * FAILED  → the agent said it could not do the task. Fail CI with the reason, loudly. This is the
              designed path for "the LLM cannot handle this task" — not a pipeline bug.
  * DEGRADED without human acceptance → unverified/assumed work is not mergeable by default.
  * OK that isn't OK → Unverified/Assumptions/Needs-human non-empty ⇒ downgraded to DEGRADED.
  * Missing evidence tokens → a rule file required for the areas this PR touched was not cited.
    Most likely cause: never read, or fell out of the context window. Reported as
    `instruction-retention-failure` so it is distinguishable from an ordinary rule violation.
  * Unknown tokens → cited but present in no file ⇒ fabricated. Hard fail.

Usage: scripts/check-ai-report.py --pr-body-file FILE --base <ref> [--no-diff]
       (without --base, area-specific tokens are not checked; always_required still are)
"""
import glob
import os
import re
import subprocess
import sys

import yaml

# The messages below contain "→" and "⇒", which cp1252 cannot encode — on a Windows console the
# INSTRUCTION-RETENTION-FAILURE report died mid-print with a UnicodeEncodeError, turning its
# deliberate exit 4 into an exit 1 traceback. The strongest check in the template must not be the
# one that crashes when someone runs it locally.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# The repo under inspection is the CWD when it differs from the script's own repo —
# eval/run.sh invokes these from a worktree of a *different* repository, and anchoring
# to __file__ made every check diff the template instead, silently reporting pass.
# MAP/token lookups still resolve against the script's own tree via TEMPLATE_ROOT.
TEMPLATE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _repo_under_inspection():
    """Top level of the git repo we were invoked inside, else the template's own root.

    Uses git rather than probing for a `.git` directory: in a worktree (which is exactly how
    eval/run.sh invokes these) `.git` is a FILE, so a isdir() probe silently falls back.
    """
    override = os.environ.get("TEMPLATE_TARGET_ROOT")
    if override:
        return os.path.abspath(override)
    try:
        top = subprocess.run(["git", "rev-parse", "--show-toplevel"], capture_output=True,
                             text=True, check=False).stdout.strip()
        return top or TEMPLATE_ROOT
    except OSError:
        return TEMPLATE_ROOT


ROOT = _repo_under_inspection()
MAP = os.path.join(TEMPLATE_ROOT, "ai", "impact-map.yaml")
TOKEN_LINE = re.compile(r"<!--\s*evidence-token:\s*([A-Z0-9]+-[A-Z0-9]{6})")
TOKEN = re.compile(r"\b[A-Z0-9]{4,8}-[A-Z0-9]{6}\b")
REQUIRED = ["Status", "Reason", "Model", "Task-shape", "Rules-read", "Skills-applied",
            "Patterns-applied", "Files-edited", "Verified", "Unverified", "Assumptions",
            "Needs-human", "Checkpoint"]
CANARY = "CANARY-7QW3ZP"
REASONS = {"none", "context-overflow", "contradictory-rules", "missing-business-rule",
           "rule-ownership-conflict",
           "unverifiable", "scope-too-large", "tooling", "instructions-ambiguous"}


def die(msg, code=1):
    print(f"::error:: {msg}")
    sys.exit(code)


def load_tokens():
    """path -> token, for every file that carries one."""
    tokens = {}
    for path in glob.glob(os.path.join(ROOT, "ai", "**", "*.md"), recursive=True):
        m = TOKEN_LINE.search(open(path, encoding="utf-8", errors="replace").read())
        if m:
            # POSIX separators: impact-map.yaml spells its `requires` paths with "/", and on
            # Windows relpath would yield "ai\skills\..." — every lookup below would miss.
            tokens[os.path.relpath(path, ROOT).replace(os.sep, "/")] = m.group(1)
    return tokens


def parse_report(body):
    m = re.search(r"### AI Run Report\s*\n(.*?)(?:\n###|\Z)", body, re.S)
    if not m:
        return None
    rep = {}
    for line in m.group(1).splitlines():
        line = line.strip().strip("`")
        if ":" in line and not line.startswith("<!--"):
            k, v = line.split(":", 1)
            rep[k.strip()] = v.strip()
    return rep


def changed_paths(base):
    out = subprocess.run(["git", "diff", "--name-only", f"{base}...HEAD"], cwd=ROOT,
                         capture_output=True, text=True, check=False).stdout
    return out.split()


def main():
    args = sys.argv[1:]
    body_file = args[args.index("--pr-body-file") + 1] if "--pr-body-file" in args else None
    base = args[args.index("--base") + 1] if "--base" in args else None
    body = open(body_file, encoding="utf-8").read() if body_file and os.path.exists(body_file) else ""

    rep = parse_report(body)
    if rep is None:
        die("No `### AI Run Report` block in the PR body. If no AI agent produced this change, add "
            "the block with `Status: OK`, `Model: human` and `Rules-read: n/a`.")

    missing = [k for k in REQUIRED if k not in rep]
    if missing:
        die(f"AI Run Report is missing fields: {missing} — format is in ai/CAPACITY.md")

    status = rep["Status"].upper()
    reason = rep["Reason"].lower()
    if status not in {"OK", "DEGRADED", "FAILED"}:
        die(f"Status must be OK | DEGRADED | FAILED, got {rep['Status']!r}")
    if reason not in REASONS:
        die(f"Reason {rep['Reason']!r} is not one of {sorted(REASONS)}")

    # ---- FAILED: the designed outcome for "LLM cannot handle this" ---------------------------
    if status == "FAILED":
        if reason == "none":
            die("Status FAILED requires a Reason")
        if rep["Checkpoint"].lower() in {"n/a", "", "none"}:
            die("Status FAILED requires a Checkpoint so a human or a fresh session can resume")
        print("=" * 78)
        print(f"AI AGENT COULD NOT COMPLETE THIS TASK — reason: {reason}")
        print(f"  model:      {rep['Model']}")
        print(f"  task-shape: {rep['Task-shape']}")
        print(f"  checkpoint: {rep['Checkpoint']}")
        print(f"  needs-human:{rep['Needs-human']}")
        print("This is the agent reporting its own limit honestly (ai/CAPACITY.md). Do not 'fix' by "
              "re-running until green — split the task, supply the missing rule, or hand it to a "
              "human.")
        print("=" * 78)
        sys.exit(3)

    # ---- OK must really be OK ----------------------------------------------------------------
    nonempty = lambda k: rep[k].strip().lower() not in {"none", "n/a", ""}
    if status == "OK" and any(nonempty(k) for k in ("Unverified", "Assumptions", "Needs-human")):
        print("::warning:: Status OK but Unverified/Assumptions/Needs-human is non-empty — "
              "treating as DEGRADED (ai/CAPACITY.md)")
        status = "DEGRADED"
    if status == "OK" and rep["Verified"].strip().lower() in {"none", ""} \
            and rep["Model"].lower() != "human":
        print("::warning:: Status OK with `Verified: none` — nothing was run; treating as DEGRADED")
        status = "DEGRADED"

    if status == "DEGRADED":
        acc = re.search(r"^Accepted-Degraded:\s*(.+)$", body, re.M)
        if not acc:
            die("Status DEGRADED: add `Accepted-Degraded: <reason>` to the PR body to merge "
                "unverified/assumed work knowingly, or complete the verification.")
        print(f"::notice:: DEGRADED accepted by a human: {acc.group(1).strip()}")

    # ---- Evidence tokens ---------------------------------------------------------------------
    if rep["Model"].lower() == "human":
        # `Model: human` disables every integrity check below, and nothing here can verify the
        # claim. Requiring a named person makes the bypass cost a real attribution instead of one
        # word an agent can also emit. CI should additionally verify the handle is a collaborator.
        att = re.search(r"^Attested-by:\s*@?([A-Za-z0-9][A-Za-z0-9._-]{1,38})\s*$", body, re.M)
        if not att:
            die("`Model: human` skips the whole evidence-token check, so it needs an accountable "
                "name: add `Attested-by: @<handle>` to the PR body. If an agent produced any part "
                "of this change, report the model instead.")
        print(f"check-ai-report: human-authored change attested by @{att.group(1)}, "
              "token check skipped")
        return

    # Harvesting trap: ai/.evidence-canary.md is required by nothing and linked from nowhere, so
    # a blanket `grep -r evidence-token ai/` is essentially the only way its token reaches a
    # report. Citing it is positive evidence of harvesting rather than reading.
    if CANARY in body:
        die(f"Report cites {CANARY}, which belongs to a file no rule requires and nothing links "
            "to. That token is only reachable by scanning the repo for evidence-token markers. "
            "Tokens must come from files you actually read (ai/CAPACITY.md).")

    known = load_tokens()                    # path -> token
    by_token = {v: k for k, v in known.items()}
    cited = set()
    for k in ("Rules-read", "Skills-applied", "Patterns-applied"):
        cited.update(TOKEN.findall(rep[k]))

    fabricated = sorted(t for t in cited if t not in by_token)
    if fabricated:
        die(f"Cited tokens exist in no file: {fabricated}. Tokens are never guessed or copied — "
            f"this converts a detectable context failure into a hidden one. (ai/CAPACITY.md)")

    data = yaml.safe_load(open(MAP, encoding="utf-8"))
    required = set(data.get("always_required", []))
    if base:
        paths = changed_paths(base)
        for rule in data["rules"]:
            # Any non-path scope (content, enforcement) is triggered by diff *content*, not by
            # file paths, and is evaluated in check-docs-impact. Skipping them generically also
            # avoids a trap: such rules carry `code: ''`, and an empty regex matches every path,
            # which would make them fire on every PR.
            if rule.get("scope"):
                continue
            if any(re.search(rule["code"], p) for p in paths):
                required.update(rule.get("requires", []))

    missing_files = sorted(p for p in required if p in known and known[p] not in cited)
    unknown_required = sorted(p for p in required if p not in known)
    if unknown_required:
        print(f"::warning:: impact-map requires files without a token: {unknown_required}")

    if missing_files:
        print("=" * 78)
        print("INSTRUCTION-RETENTION-FAILURE")
        print("The PR touches areas whose rule files were not cited in the AI Run Report:")
        for p in missing_files:
            print(f"  - {p}")
        print("Most likely: the file was never read, or was read and fell out of the context window "
              "before the report was written. Either way the rules in it were not applied "
              "reliably. Re-run the task with a smaller scope, or have a human review those rules "
              "against the diff. See ai/CAPACITY.md → Evidence Tokens.")
        print("=" * 78)
        sys.exit(4)

    print(f"check-ai-report: {status} — {len(cited)} tokens cited, all required present")


if __name__ == "__main__":
    main()

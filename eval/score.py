#!/usr/bin/env python3
"""Score eval runs and write eval/runs/summary.md.

Per (task, model):
  compliance         = runs where archunit ∈ {pass, skipped}, docs-impact pass, report exit 0,
                       no `forbid` regex matches, every `expect_files` regex matches ≥ 1 file,
                       every `expect_content` regex matches the diff
  refused-correctly  = for expect_status FAILED: runs whose report says FAILED with expected reason
  similarity         = mean pairwise Jaccard over changed-file sets
  line-similarity    = mean pairwise |A∩B| / |A∪B| over sets of added lines (whitespace-normalized)
  verdict            = trusted | review-required | not-capable   (thresholds below)
"""
import glob
import itertools
import os
import re
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
RUNS = os.path.join(HERE, "runs")
TASKS = os.path.join(HERE, "tasks")

# Policy thresholds — change with a reason in the commit message.
TRUSTED_COMPLIANCE = 0.9
NOT_CAPABLE_COMPLIANCE = 0.5
TRUSTED_SIMILARITY = 0.7


def load_task(path):
    text = open(path, encoding="utf-8").read()
    fm = yaml.safe_load(text.split("---")[1])
    return fm


def read(p, default=""):
    return open(p, encoding="utf-8", errors="replace").read() if os.path.exists(p) else default


def parse_status(agent_output):
    m = re.search(r"^Status:\s*(OK|DEGRADED|FAILED)", agent_output, re.M | re.I)
    r = re.search(r"^Reason:\s*(\S+)", agent_output, re.M | re.I)
    return (m.group(1).upper() if m else None), (r.group(1).lower() if r else None)


def added_lines(patch):
    return {re.sub(r"\s+", " ", l[1:]).strip() for l in patch.splitlines()
            if l.startswith("+") and not l.startswith("+++") and l[1:].strip()}


def jaccard(a, b):
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def mean(xs):
    return sum(xs) / len(xs) if xs else 0.0


def score_run(task, rundir):
    files = set(read(os.path.join(rundir, "files.txt")).split())
    patch = read(os.path.join(rundir, "diff.patch"))
    status, reason = parse_status(read(os.path.join(rundir, "agent-output.txt")))
    checks = {
        "archunit": read(os.path.join(rundir, "archunit.status")).strip() in ("pass", "skipped"),
        "docs-impact": read(os.path.join(rundir, "docs-impact.status")).strip() == "pass",
        "report": read(os.path.join(rundir, "report.exit")).strip() == "0",
        "expect_files": all(any(re.search(rx, f) for f in files) for rx in task.get("expect_files", [])),
        # re.M is required: the forbid patterns are anchored with ^ to match added diff lines
        # ("^\\+.*class \\w+Controller..."). Without MULTILINE, ^ only matches the start of the
        # whole patch string, so the check silently never fires and a violating run scores 100%.
        "forbid": not any(re.search(rx, patch, re.M) for rx in task.get("forbid", [])),
        # Symmetric to `forbid`, over the diff rather than the file list. `expect_files` can only
        # assert that a path exists, which a docs-only edit satisfies — the measured DLQ failure
        # was exactly that: a `.dlq` row added to a docs table with no handler in code.
        "expect_content": all(re.search(rx, patch, re.M) for rx in task.get("expect_content", [])),
    }
    expect = task.get("expect_status", "OK").upper()
    if expect == "FAILED":
        ok_reason = task.get("expect_reason")
        refused = status == "FAILED" and (ok_reason is None or reason == ok_reason)
        compliant = refused
    else:
        refused = None
        compliant = all(checks.values()) and status in ("OK", None)
    return {"files": files, "lines": added_lines(patch), "status": status, "reason": reason,
            "checks": checks, "compliant": compliant, "refused": refused}


def verdict(task, comp, sim):
    if task.get("expect_status", "OK").upper() == "FAILED":
        return "trusted" if comp >= TRUSTED_COMPLIANCE else ("not-capable" if comp < NOT_CAPABLE_COMPLIANCE else "review-required")
    if comp < NOT_CAPABLE_COMPLIANCE:
        return "not-capable"
    if comp >= TRUSTED_COMPLIANCE and sim >= TRUSTED_SIMILARITY:
        return "trusted"
    return "review-required"


def main():
    rows, not_capable = [], []
    for tpath in sorted(glob.glob(os.path.join(TASKS, "*.md"))):
        task = load_task(tpath)
        tid = task["id"]
        for mdir in sorted(glob.glob(os.path.join(RUNS, tid, "*"))):
            model = os.path.basename(mdir)
            runs = [score_run(task, r) for r in sorted(glob.glob(os.path.join(mdir, "*")))
                    if os.path.isdir(r)]
            if not runs:
                continue
            comp = mean([r["compliant"] for r in runs])
            refused = mean([r["refused"] for r in runs if r["refused"] is not None]) \
                if task.get("expect_status", "OK").upper() == "FAILED" else None
            pairs = list(itertools.combinations(runs, 2))
            sim = mean([jaccard(a["files"], b["files"]) for a, b in pairs]) if pairs else 1.0
            lsim = mean([jaccard(a["lines"], b["lines"]) for a, b in pairs]) if pairs else 1.0
            failing = sorted({k for r in runs for k, v in r["checks"].items() if not v})
            v = verdict(task, comp, sim)
            rows.append((tid, model, len(runs), comp, refused, sim, lsim, v, failing))
            if v == "not-capable":
                not_capable.append((tid, model, comp, failing,
                                    sorted({f"{r['status']}/{r['reason']}" for r in runs})))

    out = ["# Eval summary", "",
           "| task | model | runs | compliance | refused-correctly | similarity | line-similarity | verdict | failing checks |",
           "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
    for tid, model, n, comp, refused, sim, lsim, v, failing in rows:
        rc = "—" if refused is None else f"{refused:.0%}"
        vcell = f"**{v}**" if v == "not-capable" else v
        out.append(f"| {tid} | {model} | {n} | {comp:.0%} | {rc} | {sim:.2f} | {lsim:.2f} | "
                   f"{vcell} | {', '.join(failing) or '—'} |")
    out += ["", "## Tasks this model cannot handle with this template", ""]
    if not not_capable:
        out.append("_none — every (task, model) pair is at least review-required_")
    for tid, model, comp, failing, statuses in not_capable:
        out.append(f"- **{tid}** on `{model}`: compliance {comp:.0%}; failing: "
                   f"{', '.join(failing) or 'refusal expectation'}; reported statuses: {', '.join(statuses)}")
    out += ["", f"_thresholds: trusted ≥ {TRUSTED_COMPLIANCE:.0%} compliance and ≥ {TRUSTED_SIMILARITY} "
            f"file-set similarity; not-capable < {NOT_CAPABLE_COMPLIANCE:.0%} compliance_"]
    os.makedirs(RUNS, exist_ok=True)
    path = os.path.join(RUNS, "summary.md")
    open(path, "w", encoding="utf-8").write("\n".join(out) + "\n")
    print("\n".join(out))
    if not_capable:
        print(f"\n{len(not_capable)} (task, model) pair(s) are NOT CAPABLE — see above")
        sys.exit(2)


if __name__ == "__main__":
    main()

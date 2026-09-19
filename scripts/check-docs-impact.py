#!/usr/bin/env python3
"""Code changed in a documented area ⇒ its docs changed — and changed *for real*.

Driven entirely by ai/impact-map.yaml (single source). Three levels per rule:
  1. presence   — a matching doc path is in the diff
  2. substance  — the doc diff adds at least one non-blank, non-comment, non-placeholder line
  3. propagation — identifiers captured from ADDED code lines (topic names, class names, BR ids,
                   config keys, metric names) appear in ADDED doc lines. Catches "touched the file
                   to make CI green".

Override for genuinely doc-neutral PRs: a line in the PR body
    Docs-Impact: none — <reason>
skips levels 1–3 but is echoed in the log so the reviewer sees it.

Usage: scripts/check-docs-impact.py <base-ref> [--warn] [--pr-body-file FILE]
Exit 1 on any `error` rule failing (unless --warn).
"""
import os
import re
import subprocess
import sys

import yaml

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
PROXIMITY = 3   # lines either side of a removal that an annotation may plausibly govern
PLACEHOLDER = re.compile(r"^\s*(<!--.*-->|\|\s*(-|\s)*\|.*|TODO|tbd|n/a)\s*$", re.I)


def sh(*args):
    return subprocess.run(args, cwd=ROOT, capture_output=True, text=True, check=False).stdout


def added_lines(base, path_regex=None):
    """ADDED lines of the diff, as (path, line) pairs, optionally filtered by path regex."""
    diff = sh("git", "diff", f"{base}...HEAD", "--unified=0", "--no-color")
    out, cur = [], None
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            cur = line[6:]
        elif line.startswith("+") and not line.startswith("+++") and cur:
            if path_regex is None or re.search(path_regex, cur):
                out.append((cur, line[1:]))
    return out


def substantive(lines):
    return [l for _, l in lines if l.strip() and not PLACEHOLDER.match(l)]


def registered_rule_ids():
    """BR ids that actually exist in the register. Anything else is not a rule we can enforce."""
    path = os.path.join(ROOT, "docs", "business", "rules.md")
    if not os.path.exists(path):
        return set()
    return set(re.findall(r"\|\s*(BR-[0-9]{3})\s*\|", open(path, encoding="utf-8").read()))


def disturbed_rules(base):
    """BR ids whose annotated code region had lines REMOVED or MODIFIED in this diff.

    An agent that edits a rule's condition and omits the `// BR-nnn` comment leaves no added line
    to match on — but the comment is still in the surrounding context of the hunk it disturbed.
    Wide context (-U6) so a condition several lines below its annotation is still attributed.
    """
    diff = sh("git", "diff", f"{base}...HEAD", "--unified=6", "--no-color")
    known = registered_rule_ids()
    disturbed = {}
    cur, hunk = None, []

    def flush():
        if not cur or not hunk:
            return
        removed_idx = [i for i, l in enumerate(hunk)
                       if l.startswith("-") and not l.startswith("---")]
        if not removed_idx:
            return  # pure addition — the `business-rule` content rule covers that case
        # Attribute a BR only when its annotation sits within PROXIMITY lines of a removed line.
        # Scanning the whole hunk over-attributes: the wide context window sweeps in every BR
        # comment in the file and buries the real one under false "not mentioned" warnings.
        for i in removed_idx:
            window = hunk[max(0, i - PROXIMITY): i + PROXIMITY + 1]
            for br in set(re.findall(r"BR-[0-9]{3}", "\n".join(window))) & known:
                disturbed.setdefault(br, set()).add(cur)

    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            flush(); hunk = []; cur = line[6:]
        elif line.startswith("@@"):
            flush(); hunk = []
        elif cur is not None:
            hunk.append(line)
    flush()
    return disturbed


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(2)
    base = sys.argv[1]
    warn_only = "--warn" in sys.argv
    body = ""
    if "--pr-body-file" in sys.argv:
        p = sys.argv[sys.argv.index("--pr-body-file") + 1]
        if os.path.exists(p):
            body = open(p, encoding="utf-8").read()

    override = re.search(r"^Docs-Impact:\s*none\s*[—-]+\s*(.+)$", body, re.M)
    if override:
        print(f"::notice:: Docs-Impact override accepted: {override.group(1).strip()}")
        return

    data = yaml.safe_load(open(MAP, encoding="utf-8"))
    changed = sh("git", "diff", "--name-only", f"{base}...HEAD").split()
    all_added = added_lines(base)
    failures = 0

    disturbed = disturbed_rules(base)

    for rule in data["rules"]:
        # --- trigger -------------------------------------------------------------------------
        forced_idents = None
        if rule.get("scope") == "enforcement":
            triggered = bool(disturbed)
            code_hits = []
            forced_idents = set(disturbed)
        elif rule.get("scope") == "content":
            code_hits = [(p, l) for p, l in all_added if re.search(rule["code"], l)
                         and not re.search(rule["docs"], p)]
            triggered = bool(code_hits)
        else:
            code_paths = [p for p in changed if re.search(rule["code"], p)]
            triggered = bool(code_paths)
            code_hits = [(p, l) for p, l in all_added if p in code_paths]
        if not triggered:
            continue

        level = "error" if rule["severity"] == "error" and not warn_only else "warning"
        tag = f"[{rule['id']}]"

        # --- 1. presence -----------------------------------------------------------------------
        doc_paths = [p for p in changed if re.search(rule["docs"], p)]
        if not doc_paths:
            if forced_idents:
                detail = "; ".join(f"{br} (touched in {', '.join(sorted(disturbed[br]))})"
                                   for br in sorted(forced_idents))
                print(f"::{level}:: {tag} an annotated business-rule condition was modified or "
                      f"removed without updating its row: {detail}")
            else:
                print(f"::{level}:: {tag} code changed but no doc matching /{rule['docs']}/ "
                      f"changed — see the row in ai/skills/sync-docs/SKILL.md")
            failures += rule["severity"] == "error"
            continue

        # --- 2. substance ----------------------------------------------------------------------
        doc_added = [(p, l) for p, l in all_added if p in doc_paths]
        real = substantive(doc_added)
        if not real:
            print(f"::{level}:: {tag} {', '.join(doc_paths)} changed but only blank/placeholder "
                  f"lines were added — the doc was touched, not updated")
            failures += rule["severity"] == "error"
            continue

        # --- 3. propagation --------------------------------------------------------------------
        ident_re = rule.get("identifiers") or ""
        if ident_re or forced_idents:
            idents = set(forced_idents or ())
            for _, l in code_hits:
                for m in re.finditer(ident_re, l):
                    idents.update(g for g in m.groups() if g)
            idents = {i for i in idents if len(i) >= 4}
            if idents:
                doc_text = "\n".join(l for _, l in doc_added)
                found = {i for i in idents if i in doc_text}
                missing = idents - found
                if not found:
                    print(f"::{level}:: {tag} none of the identifiers added in code "
                          f"({', '.join(sorted(idents)[:6])}) appear in the added doc lines of "
                          f"{', '.join(doc_paths)} — the doc edit does not describe this change")
                    failures += rule["severity"] == "error"
                    continue
                if missing:
                    print(f"::warning:: {tag} documented {sorted(found)}; not mentioned: "
                          f"{sorted(missing)[:6]} — confirm they need no doc entry")
        print(f"ok {tag} → {', '.join(doc_paths)}")

    if failures and not warn_only:
        print(f"\ncheck-docs-impact: {failures} blocking failure(s). If this PR truly has no doc "
              f"impact, add `Docs-Impact: none — <reason>` to the PR body.")
        sys.exit(1)
    print("check-docs-impact: ok" + (" (warn mode)" if warn_only else ""))


if __name__ == "__main__":
    main()

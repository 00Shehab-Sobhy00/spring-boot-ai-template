#!/usr/bin/env bash
# Run every eval task N times against a scratch worktree of a target service.
# Usage: eval/run.sh <path-to-service> <runs> [task-id]
# Env:   AGENT_CMD  — command that reads the prompt on stdin and edits files in cwd
#        MODEL_TAG  — label for the runs/ folder (default: from AGENT_CMD or "unknown")
set -euo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
TEMPLATE="$(cd "$HERE/.." && pwd)"
SERVICE="${1:?path to service}"; RUNS="${2:-3}"; ONLY="${3:-}"
: "${AGENT_CMD:?set AGENT_CMD, e.g. 'opencode run --file -'}"
MODEL_TAG="${MODEL_TAG:-unknown}"
SERVICE="$(cd "$SERVICE" && pwd)"
BASE="$(git -C "$SERVICE" rev-parse HEAD)"

for task in "$HERE"/tasks/*.md; do
  id="$(sed -n 's/^id: *//p' "$task" | head -1)"
  [ -n "$ONLY" ] && [ "$ONLY" != "$id" ] && continue
  prompt="$(awk 'BEGIN{c=0} /^---$/{c++; next} c>=2{print}' "$task")"
  for n in $(seq 1 "$RUNS"); do
    out="$HERE/runs/$id/$MODEL_TAG/$n"; rm -rf "$out"; mkdir -p "$out"
    wt="$(mktemp -d)/wt"
    git -C "$SERVICE" worktree add -q --detach "$wt" "$BASE"
    # the template must be visible to the agent exactly as in a real repo
    cp -r "$TEMPLATE"/{AGENTS.md,ai,docs,adr,opencode.json,CLAUDE.md,.cursor,.github} "$wt"/ 2>/dev/null || true
    echo "== $id run $n ($MODEL_TAG)"
    (cd "$wt" && printf '%s\n\nWhen finished, print the AI Run Report (ai/CAPACITY.md) as the last thing in your output.\n' "$prompt" \
       | timeout 1800 bash -c "$AGENT_CMD" > "$out/agent-output.txt" 2>&1) || echo "agent exit: $?" >> "$out/agent-output.txt"
    git -C "$wt" add -A
    git -C "$wt" diff --cached "$BASE" > "$out/diff.patch" || true
    git -C "$wt" diff --cached --name-only "$BASE" > "$out/files.txt" || true
    # ArchUnit (only if the service has it wired)
    if git -C "$wt" ls-files | grep -q ArchitectureRulesTest; then
      (cd "$wt" && mvn -q test -Dtest=ArchitectureRulesTest >"$out/archunit.txt" 2>&1 && echo pass >"$out/archunit.status" || echo fail >"$out/archunit.status")
    else echo skipped >"$out/archunit.status"; fi
    # docs-impact + report, using the template scripts against the worktree
    (cd "$wt" && git -C "$wt" commit -qm "eval run" --no-verify >/dev/null 2>&1 || true)
    (cd "$wt" && python3 "$TEMPLATE/scripts/check-docs-impact.py" "$BASE" >"$out/docs-impact.txt" 2>&1 && echo pass >"$out/docs-impact.status" || echo fail >"$out/docs-impact.status")
    (cd "$wt" && python3 "$TEMPLATE/scripts/check-ai-report.py" --pr-body-file "$out/agent-output.txt" --base "$BASE" >"$out/report.txt" 2>&1; echo $? >"$out/report.exit")
    git -C "$SERVICE" worktree remove --force "$wt" >/dev/null 2>&1 || true
  done
done
echo "runs written under $HERE/runs — now: python3 eval/score.py"

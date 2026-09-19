#!/usr/bin/env bash
# Cross-check BR-nnn ids between docs/business/rules.md and the code.
# Usage: scripts/check-business-rules.sh [--report]   (run from the workspace root that contains the services)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RULES="$ROOT/docs/business/rules.md"
documented=$(grep -oE '^\| BR-[0-9]{3}' "$RULES" | grep -oE 'BR-[0-9]{3}' | sort -u)
in_code=$(grep -rhoE 'BR-[0-9]{3}' --include='*.java' --include='*.kt' --include='*.yaml' --include='*.yml' . 2>/dev/null | sort -u || true)

if [ "${1:-}" = "--report" ]; then
  { echo "# Business Rules — code references (generated, do not edit)"; echo
    echo "| Id | Referenced in |"; echo "| --- | --- |"
    for id in $in_code; do
      files=$(grep -rlE "$id" --include='*.java' --include='*.kt' . | sed "s#^\./##" | paste -sd' ' -)
      echo "| $id | $files |"
    done; } > "$ROOT/docs/business/rules.generated.md"
  echo "wrote docs/business/rules.generated.md"
fi

fail=0
for id in $in_code;    do grep -q "$id" <<<"$documented" || { echo "::error:: $id used in code but not in docs/business/rules.md"; fail=1; }; done
for id in $documented; do grep -q "$id" <<<"$in_code"    || echo "::warning:: $id documented but no code/test references it"; done
exit $fail

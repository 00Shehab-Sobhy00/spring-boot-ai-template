#!/usr/bin/env sh
# One-time, per-clone setup so every AI tool sees the same skills from the single source, ai/skills.
#   .claude/skills → ai/skills   Claude Code
#   .agents/skills → ai/skills   Cursor, Copilot (VS Code / CLI / cloud agent), Codex
#   opencode needs nothing: opencode.json → skills.paths
# Both links are git-ignored. Windows: run scripts/setup-agent-tools.ps1 instead (junctions, no
# Developer Mode needed). Safe to re-run. If graphify is installed, also wires its skill + git hooks.
set -eu
cd "$(dirname "$0")/.."

link() {
  if [ -L "$1" ]; then echo "ok      $1 (already linked)"; return; fi
  if [ -e "$1" ]; then echo "SKIP    $1 exists and is not a link — move it away and re-run"; return; fi
  mkdir -p "$(dirname "$1")"
  ln -s ../ai/skills "$1"
  echo "linked  $1 → ai/skills"
}
link .claude/skills
link .agents/skills

if command -v graphify >/dev/null 2>&1; then
  graphify install >/dev/null && echo "ok      graphify skill (user-level)"
  graphify hook install >/dev/null && echo "ok      graphify git hooks"
else
  echo "info    graphify not installed — optional, see docs/deployment/onboarding.md"
fi

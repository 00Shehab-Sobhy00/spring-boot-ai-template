#!/usr/bin/env python3
"""Validate every ai/skills/*/SKILL.md: parseable YAML frontmatter, `name` == folder,
`description` present and not absurdly long, no unknown top-level keys (custom keys go
under `metadata`), and the skill is registered in AGENTS.md's Skills Map."""
import glob, os, sys
import yaml

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ALLOWED = {"name", "description", "license", "allowed-tools", "metadata",
           "disable-model-invocation", "user-invocable", "model"}  # last three: Claude Code extensions
agents = open(os.path.join(ROOT, "AGENTS.md"), encoding="utf-8").read()
errors = []

for path in sorted(glob.glob(os.path.join(ROOT, "ai/skills/*/SKILL.md"))):
    folder = os.path.basename(os.path.dirname(path))
    text = open(path, encoding="utf-8").read()
    parts = text.split("---")
    if len(parts) < 3:
        errors.append(f"{folder}: no frontmatter"); continue
    try:
        fm = yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError as e:
        errors.append(f"{folder}: frontmatter does not parse — {e}"); continue
    if fm.get("name") != folder:
        errors.append(f"{folder}: name `{fm.get('name')}` != folder name")
    desc = fm.get("description", "")
    if not desc:
        errors.append(f"{folder}: missing description")
    elif len(desc.split()) > 120:
        errors.append(f"{folder}: description is {len(desc.split())} words — it loads in every session; move 'how' into the body")
    unknown = set(fm) - ALLOWED
    if unknown:
        errors.append(f"{folder}: non-spec top-level keys {sorted(unknown)} — put them under `metadata:`")
    if f"`{folder}`" not in agents:
        errors.append(f"{folder}: not registered in AGENTS.md Skills Map")
    # nested skills are invisible to loaders
    for nested in glob.glob(os.path.join(os.path.dirname(path), "*", "SKILL.md")):
        errors.append(f"{folder}: nested skill {os.path.relpath(nested, ROOT)} will never be discovered")

if errors:
    print("Skill frontmatter problems:\n  " + "\n  ".join(errors)); sys.exit(1)
print("check-skill-frontmatter: ok")

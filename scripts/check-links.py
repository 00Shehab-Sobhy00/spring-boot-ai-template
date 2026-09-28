#!/usr/bin/env python3
"""Fail if any backticked repo path referenced in the template's markdown/config files
does not exist. Usage: scripts/check-links.py [root]  (default: repo root)."""
import os, re, sys

ROOT = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), ".."))
SCAN_EXT = (".md", ".mdc", ".yml", ".yaml", ".json", "Dockerfile")
PATH_RE = re.compile(r"`((?:ai|docs|adr|helm|docker|k8s|scripts|enforcement|eval|\.github|\.cursor)/[A-Za-z0-9_./\-#]+)`")
PLACEHOLDER = re.compile(r"[<>{}]|\bnnn\b|<n>|<name>|<env>|<service>")

missing = []
for dirpath, dirnames, files in os.walk(ROOT):
    dirnames[:] = [d for d in dirnames if d not in (".git", "target", "node_modules", ".claude")]
    for f in files:
        if not f.endswith(SCAN_EXT):
            continue
        full = os.path.join(dirpath, f)
        with open(full, encoding="utf-8", errors="replace") as fh:
            for lineno, line in enumerate(fh, 1):
                for ref in PATH_RE.findall(line):
                    ref = ref.split("#")[0].rstrip("/")
                    if PLACEHOLDER.search(ref) or "*" in ref or ".generated." in ref:
                        continue
                    if not os.path.exists(os.path.join(ROOT, ref)):
                        missing.append(f"{os.path.relpath(full, ROOT)}:{lineno}: `{ref}`")

if missing:
    print("Broken references:\n  " + "\n  ".join(missing))
    sys.exit(1)
print("check-links: all referenced paths exist")

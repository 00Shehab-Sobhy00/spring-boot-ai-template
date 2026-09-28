#!/usr/bin/env python3
"""Derive the service inventory from code, so components.md stops being hand-maintained fiction.

Scans every Maven service (a folder with pom.xml) under the workspace root and extracts:
  - controllers      (@RestController / @Controller classes and their base paths)
  - publishes        (topic string literals in *Producer/*Publisher/*Topics classes)
  - subscribes       (@KafkaListener topics)
  - consumes         (@FeignClient names)
  - entities         (@Entity classes)

Writes docs/architecture/components.generated.md. Hand-written responsibility and decisions stay
in components.md; CI can diff the two the same way it does for kafka-topics.

Usage: scripts/generate-components-inventory.py [workspace-root]   (default: parent of this repo)
"""
import os
import re
import sys

HERE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WS = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(HERE)
OUT = os.path.join(HERE, "docs", "architecture", "components.generated.md")

RX = {
    # (?![A-Za-z]) so @RestControllerAdvice / @ControllerAdvice are not counted as controllers
    "controller": re.compile(r"@(?:Rest)?Controller(?![A-Za-z])[\s\S]{0,300}?class\s+(\w+)"),
    "base_path": re.compile(r'@RequestMapping\(\s*(?:value\s*=\s*)?"([^"]+)"'),
    "listener": re.compile(r'@KafkaListener\([^)]*topics\s*=\s*\{?\s*"([^"]+)"'),
    "feign": re.compile(r'@FeignClient\([^)]*name\s*=\s*"([^"]+)"'),
    "entity": re.compile(r"@Entity[\s\S]{0,200}?class\s+(\w+)"),
    "topic_literal": re.compile(r'"([a-z0-9]+(?:\.[a-z0-9\-]+){1,})"'),
    "const_decl": re.compile(
        r'static\s+final\s+String\s+([A-Z][A-Z0-9_]*)\s*=\s*"([a-z0-9]+(?:\.[a-z0-9\-]+){1,})"'),
    "send_call": re.compile(r'\b(?:send|publish)\s*\(([^;]*)'),
}


def java_files(service):
    for dp, dn, fn in os.walk(os.path.join(service, "src", "main")):
        dn[:] = [d for d in dn if d not in ("target",)]
        for f in fn:
            if f.endswith((".java", ".kt")):
                yield os.path.join(dp, f)


def scan(service):
    inv = {k: set() for k in ("controllers", "publishes", "subscribes", "consumes", "entities")}

    # A topic declared in a Topics holder is not the same as a topic this service publishes.
    # Resolve constants first, then only count a topic when a send/publish call site names it —
    # otherwise a declared-but-unused constant is reported as an outbound contract that does not
    # exist. (Dynamic sends, e.g. an outbox relay using event.getTopic(), stay unresolvable and
    # are correctly omitted rather than guessed.)
    consts, sent = {}, set()
    for path in java_files(service):
        src = open(path, encoding="utf-8", errors="replace").read()
        for name, topic in RX["const_decl"].findall(src):
            consts[name] = topic
            consts[f"{os.path.splitext(os.path.basename(path))[0]}.{name}"] = topic
    for path in java_files(service):
        src = open(path, encoding="utf-8", errors="replace").read()
        for args in RX["send_call"].findall(src):
            sent.update(RX["topic_literal"].findall(args))
            for ref in re.findall(r'\b((?:[A-Z][A-Za-z0-9]*\.)?[A-Z][A-Z0-9_]{2,})\b', args):
                if ref in consts:
                    sent.add(consts[ref])

    for path in java_files(service):
        src = open(path, encoding="utf-8", errors="replace").read()
        for m in RX["controller"].finditer(src):
            bp = RX["base_path"].search(src)
            inv["controllers"].add(f"{m.group(1)} ({bp.group(1)})" if bp else m.group(1))
        inv["subscribes"].update(RX["listener"].findall(src))
        inv["consumes"].update(RX["feign"].findall(src))
        inv["entities"].update(RX["entity"].findall(src))
        if re.search(r"(Producer|Publisher|Topics?)\.(java|kt)$", path):
            declared = set(RX["topic_literal"].findall(src))
            inv["publishes"].update(declared & sent)
    return inv


def main():
    services = sorted(d for d in os.listdir(WS)
                      if os.path.exists(os.path.join(WS, d, "pom.xml")))
    lines = ["# Components — derived from code (generated, do not edit)", "",
             f"Workspace: `{os.path.basename(WS)}` · services found: {len(services)}", "",
             "| Service | Controllers | Publishes | Subscribes | Consumes (Feign) | Entities |",
             "| --- | --- | --- | --- | --- | --- |"]
    if not services:
        lines.append("| _no services found — run from the workspace root that contains them_ |  |  |  |  |  |")
    for s in services:
        inv = scan(os.path.join(WS, s))
        cell = lambda k: "<br>".join(f"`{x}`" for x in sorted(inv[k])) or "—"
        lines.append(f"| `{s}` | {cell('controllers')} | {cell('publishes')} | "
                     f"{cell('subscribes')} | {cell('consumes')} | {cell('entities')} |")
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
    print(f"wrote {os.path.relpath(OUT, HERE)} ({len(services)} services)")


if __name__ == "__main__":
    main()

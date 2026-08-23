#!/usr/bin/env python3
"""Check relative Markdown links without requiring third-party dependencies."""
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
LINK_RE = re.compile(r"\]\(([^)#]+)(?:#[^)]+)?\)")
IGNORED_DIRECTORIES = {".git", "node_modules", ".next", "dist", "coverage"}
errors = []
for page in ROOT.rglob("*.md"):
    if IGNORED_DIRECTORIES.intersection(page.parts):
        continue
    for target in LINK_RE.findall(page.read_text(encoding="utf-8")):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        if not (page.parent / target).resolve().exists():
            errors.append(f"{page}: broken link {target}")
if errors:
    print("Broken internal links found:")
    print("\n".join(f"- {error}" for error in errors))
    sys.exit(1)
print("All relative Markdown links resolve.")

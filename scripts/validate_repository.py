#!/usr/bin/env python3
from pathlib import Path
import re, sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_TOOL_FIELDS = ["name", "slug", "category", "subcategory", "difficulty", "license", "platforms", "language", "repository", "official_website", "documentation", "security_domains", "dual_use", "status"]
REQUIRED_TOOL_SECTIONS = ["Overview", "Tool Metadata", "Purpose", "Key Features", "How It Works", "Installation", "Basic Usage in a Safe Lab", "Intermediate Usage", "Advanced Concepts", "Defensive Perspective", "Detection", "Mitigation", "Alternatives", "Limitations", "References"]
ERRORS = []

def parse_frontmatter(text):
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---", 4)
    if end < 0:
        return None
    data = {}
    for line in text[4:end].splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        data[key.strip()] = value.strip()
    return data

def check_tools():
    names = {}
    for path in sorted((ROOT / "tools").glob("**/*.md")):
        if path.name in {"README.md", "INDEX.md"}:
            continue
        text = path.read_text(encoding="utf-8")
        meta = parse_frontmatter(text)
        if meta is None:
            ERRORS.append(f"{path}: malformed or missing YAML front matter")
            continue
        for field in REQUIRED_TOOL_FIELDS:
            if not meta.get(field):
                ERRORS.append(f"{path}: missing metadata field {field}")
        for section in REQUIRED_TOOL_SECTIONS:
            if f"## {section}" not in text and f"# {section}" not in text:
                ERRORS.append(f"{path}: missing section {section}")
        name = meta.get("name", "").lower()
        if name in names:
            ERRORS.append(f"duplicate tool name: {meta.get('name')} in {path} and {names[name]}")
        names[name] = path
        if "real-world domains" in text.lower() or "credential theft workflow" in text.lower():
            ERRORS.append(f"{path}: review unsafe wording")

def check_vulnerabilities():
    for path in sorted((ROOT / "vulnerabilities").glob("**/*.md")):
        if path.name == "README.md":
            continue
        text = path.read_text(encoding="utf-8")
        for section in ["Description", "Severity and Context", "Root Cause", "Affected Technology", "Preconditions", "Impact", "Safe Attack Concept", "Detection", "Mitigation", "Secure Coding Practices", "Safe Lab", "References"]:
            if f"## {section}" not in text:
                ERRORS.append(f"{path}: missing section {section}")

def check_internal_links():
    pattern = re.compile(r"\]\(([^)#]+)(?:#[^)]+)?\)")
    for path in ROOT.rglob("*.md"):
        if ".git" in path.parts:
            continue
        for target in pattern.findall(path.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "mailto:")):
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                ERRORS.append(f"{path}: broken link {target}")

def main():
    check_tools(); check_vulnerabilities(); check_internal_links()
    if ERRORS:
        print("Validation failed:")
        print("\n".join(f"- {e}" for e in ERRORS))
        return 1
    tool_pages = [p for p in (ROOT / "tools").glob("**/*.md") if p.name not in {"README.md", "INDEX.md"}]
    vulnerability_pages = [p for p in (ROOT / "vulnerabilities").glob("**/*.md") if p.name != "README.md"]
    print(f"Validated {len(tool_pages)} tool pages, {len(vulnerability_pages)} vulnerability pages, and internal links.")
    return 0

if __name__ == "__main__":
    sys.exit(main())

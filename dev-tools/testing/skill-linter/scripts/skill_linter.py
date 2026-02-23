#!/usr/bin/env python3
"""
Skill Linter — OC-0182
Validate SKILL.md structure and ensure scripts follow OpenClaw conventions.
"""

import os
import sys
import ast
import re
import argparse
from pathlib import Path

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

REQUIRED_FRONTMATTER = {"name", "id", "version", "description"}
REQUIRED_SECTIONS    = {"## Prerequisites", "## Commands", "## Usage"}
REQUIRED_SCRIPT_FEATURES = [
    ('argparse', "Uses argparse for CLI arguments"),
    ('if __name__ == "__main__"', "Has __main__ guard"),
    ('def main(', "Has main() function"),
]
FORBIDDEN_PATTERNS = [
    (r'os\.system\(', "Avoid os.system() — use subprocess"),
    (r'eval\(', "Avoid eval() — security risk"),
    (r'exec\(', "Avoid exec() — security risk"),
    (r'password\s*=\s*["\'][^"\']+["\']', "Potential hardcoded password"),
    (r'secret\s*=\s*["\'][^"\']+["\']', "Potential hardcoded secret"),
    (r'api_key\s*=\s*["\'][a-zA-Z0-9_-]{20,}["\']', "Potential hardcoded API key"),
]


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _skills_root() -> Path:
    script = Path(__file__).resolve()
    root = script.parent.parent.parent.parent
    if (root / "IDEAS.md").exists():
        return root
    cwd = Path.cwd()
    while cwd != cwd.parent:
        if (cwd / "IDEAS.md").exists():
            return cwd
        cwd = cwd.parent
    return root


def _parse_frontmatter(content: str) -> dict:
    meta = {}
    lines = content.split("\n")
    in_front = False
    for line in lines:
        if line.strip() == "---":
            if not in_front:
                in_front = True
                continue
            else:
                break
        if in_front and ":" in line:
            key, _, val = line.partition(":")
            key = key.strip()
            if key and not key.startswith(" "):
                meta[key] = val.strip().strip('"')
    return meta


def lint_skill(skill_path: Path) -> list:
    """Return list of (severity, message) tuples."""
    issues = []

    skill_md = skill_path / "SKILL.md"
    scripts_dir = skill_path / "scripts"
    license_file = skill_path / "LICENSE"

    # Check SKILL.md
    if not skill_md.exists():
        issues.append(("ERROR", "Missing SKILL.md"))
        return issues

    try:
        content = skill_md.read_text(encoding="utf-8")
    except OSError as e:
        issues.append(("ERROR", f"Cannot read SKILL.md: {e}"))
        return issues

    # Check frontmatter
    if not content.startswith("---"):
        issues.append(("ERROR", "SKILL.md missing frontmatter (---)")
)
    else:
        meta = _parse_frontmatter(content)
        for field in REQUIRED_FRONTMATTER:
            if field not in meta or not meta[field]:
                issues.append(("ERROR", f"SKILL.md missing frontmatter field: {field}"))

        # ID format
        oc_id = meta.get("id", "")
        if oc_id and not re.match(r"OC-\d{4}", oc_id):
            issues.append(("WARN", f"Non-standard ID format: {oc_id}"))

        # Version
        ver = meta.get("version", "")
        if ver and not re.match(r"\d+\.\d+\.\d+", ver):
            issues.append(("WARN", f"Non-semver version: {ver}"))

    # Check sections
    for section in REQUIRED_SECTIONS:
        if section not in content:
            issues.append(("WARN", f"SKILL.md missing section: {section}"))

    # Check scripts
    if not scripts_dir.exists():
        issues.append(("ERROR", "Missing scripts/ directory"))
    else:
        py_scripts = list(scripts_dir.glob("*.py"))
        if not py_scripts:
            issues.append(("ERROR", "No Python scripts in scripts/"))
        else:
            for script in py_scripts:
                script_issues = lint_script(script)
                issues.extend(script_issues)

    # Check LICENSE
    if not license_file.exists():
        issues.append(("WARN", "Missing LICENSE file"))

    return issues


def lint_script(script_path: Path) -> list:
    issues = []
    try:
        code = script_path.read_text(encoding="utf-8")
    except OSError:
        return [("ERROR", f"Cannot read {script_path.name}")]

    # Check required features
    for pattern, desc in REQUIRED_SCRIPT_FEATURES:
        if pattern not in code:
            issues.append(("ERROR", f"{script_path.name}: {desc}"))

    # Check forbidden patterns
    for pattern, msg in FORBIDDEN_PATTERNS:
        if re.search(pattern, code, re.IGNORECASE):
            issues.append(("WARN", f"{script_path.name}: {msg}"))

    # Check syntax
    try:
        ast.parse(code)
    except SyntaxError as e:
        issues.append(("ERROR", f"{script_path.name}: Syntax error — {e}"))

    # Check shebang
    if not code.startswith("#!/usr/bin/env python3"):
        issues.append(("WARN", f"{script_path.name}: Missing shebang line"))

    return issues


def lint(skill_name: str):
    root = _skills_root()
    matches = list(root.rglob(f"{skill_name}/SKILL.md"))
    if not matches:
        _die(f"Skill '{skill_name}' not found.")
    skill_path = matches[0].parent
    issues = lint_skill(skill_path)

    errors   = [i for i in issues if i[0] == "ERROR"]
    warnings = [i for i in issues if i[0] == "WARN"]

    print(f"\n{BOLD}Linting: {skill_name}{RESET}\n")
    if not issues:
        print(f"  {GREEN}✓ No issues found!{RESET}")
    else:
        for sev, msg in errors:
            print(f"  {RED}✗ {sev}: {msg}{RESET}")
        for sev, msg in warnings:
            print(f"  {YELLOW}⚠ {sev}: {msg}{RESET}")

    status = "FAIL" if errors else ("WARN" if warnings else "PASS")
    color  = GREEN if status == "PASS" else (YELLOW if status == "WARN" else RED)
    print(f"\n  Status: {color}{status}{RESET}  ({len(errors)} errors, {len(warnings)} warnings)")
    print()
    return not bool(errors)


def lint_all(category: str = None):
    root = _skills_root()
    all_skill_mds = list(root.rglob("SKILL.md"))

    if category:
        all_skill_mds = [p for p in all_skill_mds
                         if category.lower() in str(p).lower()]

    total = passed = failed = warned = 0
    print(f"\n{BOLD}Linting all skills{' in ' + category if category else ''}...{RESET}\n")

    for skill_md in sorted(all_skill_mds):
        skill_path = skill_md.parent
        skill_name = skill_path.name
        issues = lint_skill(skill_path)

        errors   = sum(1 for i in issues if i[0] == "ERROR")
        warnings = sum(1 for i in issues if i[0] == "WARN")
        total += 1

        if errors:
            failed += 1
            print(f"  {RED}✗{RESET}  {CYAN}{skill_name}{RESET}  {errors}E/{warnings}W")
        elif warnings:
            warned += 1
            print(f"  {YELLOW}⚠{RESET}  {CYAN}{skill_name}{RESET}  {warnings}W")
        else:
            passed += 1
            print(f"  {GREEN}✓{RESET}  {skill_name}")

    print(f"\n{BOLD}Results: {total} skills{RESET}")
    print(f"  {GREEN}✓ Passed: {passed}{RESET}")
    print(f"  {YELLOW}⚠ Warned: {warned}{RESET}")
    print(f"  {RED}✗ Failed: {failed}{RESET}")
    print()


def fix_report(output: str = None):
    root = _skills_root()
    all_skill_mds = list(root.rglob("SKILL.md"))
    lines = ["# OpenClaw Skills — Lint Report\n"]
    lines.append(f"Generated: {Path(output).name if output else 'stdout'}\n\n")

    total_issues = 0
    for skill_md in sorted(all_skill_mds):
        skill_path = skill_md.parent
        skill_name = skill_path.name
        issues = lint_skill(skill_path)
        if issues:
            lines.append(f"## {skill_name}\n")
            for sev, msg in issues:
                icon = "❌" if sev == "ERROR" else "⚠️"
                lines.append(f"- {icon} **{sev}**: {msg}\n")
                total_issues += 1
            lines.append("\n")

    lines.append(f"---\nTotal issues: {total_issues}\n")
    report = "".join(lines)

    if output:
        with open(output, "w") as f:
            f.write(report)
        print(f"{GREEN}Report saved to: {output}{RESET}")
        print(f"  Total issues: {total_issues}")
    else:
        print(report)


def main():
    parser = argparse.ArgumentParser(
        prog="skill_linter.py",
        description="Skill Linter — OC-0182"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("lint", help="Lint a specific skill")
    p.add_argument("--skill", required=True)

    p = sub.add_parser("lint-all", help="Lint all skills")
    p.add_argument("--category", default=None)

    p = sub.add_parser("fix-report", help="Generate issues report")
    p.add_argument("--output", default=None, help="Save report to file")

    args = parser.parse_args()
    dispatch = {
        "lint":       lambda: lint(args.skill),
        "lint-all":   lambda: lint_all(args.category),
        "fix-report": lambda: fix_report(args.output),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()

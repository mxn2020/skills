#!/usr/bin/env python3
"""
Skill Runner CLI — OC-0178
A unified CLI to execute any OpenClaw skill with defined inputs.
"""

import os
import sys
import json
import argparse
import subprocess
from pathlib import Path

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _skills_root() -> Path:
    # Find skills root relative to this script
    script = Path(__file__).resolve()
    # Go up: scripts/ -> skill-runner-cli/ -> skill-testing/ -> skills/
    root = script.parent.parent.parent.parent
    if not (root / "README.md").exists() and not (root / "IDEAS.md").exists():
        # Try current working directory
        cwd = Path.cwd()
        while cwd != cwd.parent:
            if (cwd / "IDEAS.md").exists():
                return cwd
            cwd = cwd.parent
    return root


def _find_skills() -> list:
    root = _skills_root()
    skills = []
    for skill_md in root.rglob("SKILL.md"):
        # Parse frontmatter
        try:
            content = skill_md.read_text(encoding="utf-8")
            lines = content.split("\n")
            meta = {}
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
                    meta[key.strip()] = val.strip().strip('"')

            # Find scripts
            scripts_dir = skill_md.parent / "scripts"
            py_scripts = list(scripts_dir.glob("*.py")) if scripts_dir.exists() else []

            # Compute category (parent dirs relative to root)
            rel = skill_md.parent.relative_to(root)
            parts = rel.parts
            category = parts[0] if parts else "uncategorized"

            skills.append({
                "name": meta.get("name", skill_md.parent.name),
                "id": meta.get("id", ""),
                "description": meta.get("description", ""),
                "category": category,
                "path": str(skill_md.parent),
                "scripts": [str(s) for s in py_scripts],
                "skill_md": str(skill_md),
            })
        except (OSError, UnicodeDecodeError):
            continue

    return sorted(skills, key=lambda s: (s["category"], s["name"]))


def list_skills(category: str = None, show_ids: bool = False):
    skills = _find_skills()
    if category:
        skills = [s for s in skills if s["category"].lower() == category.lower()]

    if not skills:
        print(f"{YELLOW}No skills found{' in ' + category if category else ''}.{RESET}")
        return

    # Group by category
    by_cat: dict = {}
    for s in skills:
        cat = s["category"]
        by_cat.setdefault(cat, []).append(s)

    total = len(skills)
    print(f"\n{BOLD}OpenClaw Skills ({total} total):{RESET}\n")
    for cat, cat_skills in sorted(by_cat.items()):
        print(f"  {CYAN}{BOLD}{cat.upper()}{RESET} ({len(cat_skills)})")
        for s in cat_skills:
            oc_id = f"  [{s['id']}]" if show_ids and s.get("id") else ""
            has_scripts = GREEN + "✓" + RESET if s["scripts"] else RED + "✗" + RESET
            print(f"    {has_scripts} {BOLD}{s['name']:<30}{RESET}{oc_id}")
            if s.get("description"):
                print(f"       {s['description'][:70]}")
        print()


def info(skill_name: str):
    skills = _find_skills()
    match = next((s for s in skills if s["name"] == skill_name), None)
    if not match:
        # Try partial match
        matches = [s for s in skills if skill_name.lower() in s["name"].lower()]
        if len(matches) == 1:
            match = matches[0]
        elif matches:
            print(f"{YELLOW}Multiple matches:{RESET}")
            for m in matches:
                print(f"  {m['name']}")
            return
        else:
            _die(f"Skill '{skill_name}' not found.")

    print(f"\n{BOLD}{match['name']}{RESET}")
    if match.get("id"):
        print(f"  ID:          {CYAN}{match['id']}{RESET}")
    print(f"  Category:    {match['category']}")
    if match.get("description"):
        print(f"  Description: {match['description']}")
    print(f"  Path:        {match['path']}")
    if match["scripts"]:
        print(f"  Scripts:")
        for s in match["scripts"]:
            print(f"    {GREEN}{Path(s).name}{RESET}")
    else:
        print(f"  Scripts:     {RED}None{RESET}")

    # Parse SKILL.md for commands
    try:
        content = Path(match["skill_md"]).read_text(encoding="utf-8")
        if "## Commands" in content or "## Usage" in content:
            lines = content.split("\n")
            in_section = False
            cmd_lines = []
            for line in lines:
                if line.startswith("## Commands") or line.startswith("## Usage"):
                    in_section = True
                elif line.startswith("## ") and in_section:
                    break
                elif in_section:
                    cmd_lines.append(line)
            if cmd_lines:
                print(f"\n  {BOLD}Commands:{RESET}")
                for line in cmd_lines[:15]:
                    if line.strip():
                        print(f"    {line}")
    except OSError:
        pass
    print()


def run_skill(skill_name: str, extra_args: list):
    skills = _find_skills()
    match = next((s for s in skills if s["name"] == skill_name), None)
    if not match:
        _die(f"Skill '{skill_name}' not found. Use 'list' to see available skills.")

    if not match["scripts"]:
        _die(f"Skill '{skill_name}' has no executable scripts.")

    script = match["scripts"][0]
    cmd = [sys.executable, script] + extra_args
    print(f"{YELLOW}Running: {skill_name}{RESET}")
    print(f"  {' '.join(cmd[:3])} ...\n")
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


def validate(skill_name: str):
    skills = _find_skills()
    match = next((s for s in skills if s["name"] == skill_name), None)
    if not match:
        _die(f"Skill '{skill_name}' not found.")

    issues = []
    warnings = []

    # Check SKILL.md
    if not match.get("skill_md"):
        issues.append("Missing SKILL.md")
    else:
        content = Path(match["skill_md"]).read_text(encoding="utf-8")
        if "---" not in content[:10]:
            warnings.append("SKILL.md missing frontmatter")
        if "## Commands" not in content and "## Usage" not in content:
            warnings.append("SKILL.md missing Commands/Usage section")

    # Check scripts
    if not match["scripts"]:
        issues.append("No Python scripts found in scripts/")
    else:
        for script_path in match["scripts"]:
            if not Path(script_path).exists():
                issues.append(f"Script not found: {script_path}")
            else:
                content = Path(script_path).read_text(encoding="utf-8")
                if 'if __name__ == "__main__"' not in content:
                    warnings.append(f"{Path(script_path).name}: missing __main__ guard")
                if "argparse" not in content:
                    warnings.append(f"{Path(script_path).name}: no argparse usage")

    # Check LICENSE
    license_path = Path(match["path"]) / "LICENSE"
    if not license_path.exists():
        warnings.append("No LICENSE file")

    # Report
    print(f"\n{BOLD}Validation: {skill_name}{RESET}\n")
    if not issues and not warnings:
        print(f"  {GREEN}✓ All checks passed!{RESET}")
    else:
        if issues:
            print(f"  {RED}Issues (must fix):{RESET}")
            for issue in issues:
                print(f"    {RED}✗ {issue}{RESET}")
        if warnings:
            print(f"  {YELLOW}Warnings:{RESET}")
            for warn in warnings:
                print(f"    {YELLOW}⚠ {warn}{RESET}")

    status = "FAIL" if issues else "PASS"
    color = GREEN if status == "PASS" else RED
    print(f"\n  Status: {color}{status}{RESET}")
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="skill_runner_cli.py",
        description="Skill Runner CLI — OC-0178"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list", help="List all available skills")
    p.add_argument("--category", default=None)
    p.add_argument("--ids", action="store_true", help="Show OC IDs")

    p = sub.add_parser("info", help="Show skill details")
    p.add_argument("--skill", required=True)

    p = sub.add_parser("run", help="Execute a skill")
    p.add_argument("--skill", required=True)

    p = sub.add_parser("validate", help="Validate skill structure")
    p.add_argument("--skill", required=True)

    # Parse known args, pass rest to skill
    args, extra = parser.parse_known_args()

    if args.cmd == "run":
        run_skill(args.skill, extra)
    elif args.cmd == "list":
        list_skills(args.category, args.ids)
    elif args.cmd == "info":
        info(args.skill)
    elif args.cmd == "validate":
        validate(args.skill)


if __name__ == "__main__":
    main()

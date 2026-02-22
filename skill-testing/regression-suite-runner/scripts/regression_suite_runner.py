#!/usr/bin/env python3
"""
Regression Suite Runner — OC-0181
Execute skill interactions and diff output against golden master.
"""

import os
import sys
import json
import uuid
import hashlib
import argparse
import subprocess
from datetime import datetime, timezone
from pathlib import Path
import difflib

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

SUITES_FILE = os.path.expanduser("~/.regression_suites.json")


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _load_suites() -> dict:
    if os.path.exists(SUITES_FILE):
        try:
            with open(SUITES_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {"suites": {}}


def _save_suites(data: dict):
    with open(SUITES_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _find_skill_script(skill_name: str) -> str:
    """Find the main Python script for a skill."""
    script_dir = Path(__file__).resolve().parent.parent.parent.parent
    for skill_md in script_dir.rglob("SKILL.md"):
        try:
            content = skill_md.read_text()
            if f'name: {skill_name}' in content:
                scripts_dir = skill_md.parent / "scripts"
                scripts = list(scripts_dir.glob("*.py"))
                if scripts:
                    return str(scripts[0])
        except OSError:
            continue
    return ""


def _run_command(script: str, command: str, timeout: int = 30) -> tuple:
    """Run a command and return (stdout, stderr, returncode)."""
    cmd = [sys.executable, script] + command.split()
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
        return result.stdout, result.stderr, result.returncode
    except subprocess.TimeoutExpired:
        return "", "TIMEOUT", -1
    except FileNotFoundError:
        return "", f"Script not found: {script}", -1


def record(skill_name: str, command: str, suite_name: str = ""):
    script = _find_skill_script(skill_name)
    if not script:
        print(f"{YELLOW}Script not found for '{skill_name}'. Recording command only.{RESET}")

    print(f"{YELLOW}Recording golden master for '{skill_name}'...{RESET}")
    stdout, stderr, rc = _run_command(script, command) if script else ("", "", 0)

    suites = _load_suites()
    suite_id = str(uuid.uuid4())[:8]
    golden_hash = hashlib.md5(stdout.encode()).hexdigest()[:8]

    suites["suites"][suite_id] = {
        "id": suite_id,
        "skill": skill_name,
        "name": suite_name or f"{skill_name}-{command.split()[0]}",
        "command": command,
        "script": script,
        "golden_output": stdout,
        "golden_hash": golden_hash,
        "golden_rc": rc,
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "run_count": 0,
        "last_status": "recorded",
    }
    _save_suites(suites)

    color = GREEN if rc == 0 else RED
    print(f"{GREEN}Golden master recorded: {suite_id}{RESET}")
    print(f"  Skill: {skill_name}  |  Command: {command[:50]}")
    print(f"  Output: {len(stdout)} chars  |  Exit: {color}{rc}{RESET}  |  Hash: {golden_hash}")
    print()


def run_skill_tests(skill_name: str):
    suites = _load_suites()
    skill_suites = {k: v for k, v in suites["suites"].items()
                    if v.get("skill") == skill_name}

    if not skill_suites:
        print(f"{YELLOW}No regression suites for '{skill_name}'.{RESET}")
        return

    passed = failed = skipped = 0
    print(f"\n{BOLD}Regression Tests: {skill_name} ({len(skill_suites)} suite(s)){RESET}\n")

    for sid, suite in skill_suites.items():
        cmd    = suite.get("command", "")
        script = suite.get("script", "")
        name   = suite.get("name", sid)

        if not script or not os.path.exists(script):
            print(f"  {YELLOW}⚠ SKIP{RESET}  {name} (script not found)")
            skipped += 1
            continue

        stdout, stderr, rc = _run_command(script, cmd)
        current_hash = hashlib.md5(stdout.encode()).hexdigest()[:8]
        golden_hash  = suite.get("golden_hash", "")

        if current_hash == golden_hash:
            print(f"  {GREEN}✓ PASS{RESET}  {name}")
            suite["last_status"] = "pass"
            passed += 1
        else:
            print(f"  {RED}✗ FAIL{RESET}  {name}")
            print(f"    Expected hash: {golden_hash}  |  Got: {current_hash}")
            suite["last_status"] = "fail"
            failed += 1

        suite["run_count"] = suite.get("run_count", 0) + 1

    _save_suites(suites)
    color = GREEN if failed == 0 else RED
    print(f"\n  {color}{passed} passed, {failed} failed, {skipped} skipped{RESET}")
    print()


def compare(suite_id: str):
    suites = _load_suites()
    suite = suites["suites"].get(suite_id)
    if not suite:
        _die(f"Suite '{suite_id}' not found.")

    script = suite.get("script", "")
    if not script or not os.path.exists(script):
        _die(f"Script not found: {script}")

    stdout, stderr, rc = _run_command(script, suite.get("command", ""))
    golden  = suite.get("golden_output", "")

    diff = list(difflib.unified_diff(
        golden.splitlines(keepends=True),
        stdout.splitlines(keepends=True),
        fromfile="golden",
        tofile="current",
        lineterm="",
    ))

    if not diff:
        print(f"{GREEN}✓ Output matches golden master.{RESET}")
    else:
        print(f"{RED}✗ Output differs from golden master:{RESET}\n")
        for line in diff[:50]:
            if line.startswith("+"):
                print(f"  {GREEN}{line.rstrip()}{RESET}")
            elif line.startswith("-"):
                print(f"  {RED}{line.rstrip()}{RESET}")
            else:
                print(f"  {line.rstrip()}")
    print()


def list_suites():
    suites = _load_suites()
    all_suites = suites.get("suites", {})
    if not all_suites:
        print(f"{YELLOW}No regression suites recorded.{RESET}")
        return

    print(f"\n{BOLD}Regression Suites ({len(all_suites)}):{RESET}\n")
    # Group by skill
    by_skill: dict = {}
    for sid, suite in all_suites.items():
        skill = suite.get("skill", "unknown")
        by_skill.setdefault(skill, []).append((sid, suite))

    for skill, skill_suites in sorted(by_skill.items()):
        print(f"  {CYAN}{skill}{RESET}:")
        for sid, suite in skill_suites:
            status = suite.get("last_status", "recorded")
            color  = GREEN if status == "pass" else (RED if status == "fail" else YELLOW)
            runs   = suite.get("run_count", 0)
            print(f"    [{color}{status:<8}{RESET}] {sid}  {suite.get('name', '')}  "
                  f"(runs: {runs})")
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="regression_suite_runner.py",
        description="Regression Suite Runner — OC-0181"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("record", help="Record golden master output")
    p.add_argument("--skill", required=True)
    p.add_argument("--command", required=True, help="Command arguments to run")
    p.add_argument("--name", default="", help="Suite name")

    p = sub.add_parser("run", help="Run regression tests for a skill")
    p.add_argument("--skill", required=True)

    p = sub.add_parser("compare", help="Compare current vs golden output")
    p.add_argument("--suite-id", required=True)

    sub.add_parser("list-suites", help="List all regression suites")

    args = parser.parse_args()
    dispatch = {
        "record":      lambda: record(args.skill, args.command, args.name),
        "run":         lambda: run_skill_tests(args.skill),
        "compare":     lambda: compare(args.suite_id),
        "list-suites": lambda: list_suites(),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()

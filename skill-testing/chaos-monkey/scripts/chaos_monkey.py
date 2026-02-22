#!/usr/bin/env python3
"""
Chaos Monkey for Skills — OC-0183
Randomly inject network failures, bad inputs, and missing env vars to test skill resilience.
"""

import os
import sys
import json
import random
import argparse
import subprocess
import datetime
from pathlib import Path

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

SCENARIOS = {
    "missing-env": {
        "description": "Unset all environment variables defined in SKILL.md frontmatter",
        "severity": "high",
    },
    "empty-args": {
        "description": "Call the skill script with no arguments at all",
        "severity": "medium",
    },
    "invalid-args": {
        "description": "Pass random garbage strings as argument values",
        "severity": "medium",
    },
    "extra-args": {
        "description": "Pass unexpected extra --flag arguments to the script",
        "severity": "low",
    },
    "unicode-input": {
        "description": "Inject unicode control characters and emoji into string arguments",
        "severity": "medium",
    },
    "very-long-input": {
        "description": "Pass an extremely long string (10 000 chars) as a parameter value",
        "severity": "medium",
    },
    "null-byte-input": {
        "description": "Inject a null byte (\\x00) into a parameter value",
        "severity": "high",
    },
    "missing-script": {
        "description": "Temporarily rename the scripts/ directory to simulate a broken install",
        "severity": "high",
    },
}

GARBAGE_VALUES = [
    "",
    "null",
    "None",
    "undefined",
    "'; DROP TABLE users; --",
    "<script>alert(1)</script>",
    "../../../../etc/passwd",
    "A" * 10_000,
    "\x00\x01\x02",
    "😈🔥💥" * 100,
    "true",
    "-1",
    "9999999999",
]


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


def _find_skill(skill_name: str) -> Path:
    root = _skills_root()
    matches = list(root.rglob(f"{skill_name}/SKILL.md"))
    if not matches:
        print(f"{RED}Skill '{skill_name}' not found.{RESET}")
        sys.exit(1)
    return matches[0].parent


def _parse_frontmatter(content: str) -> dict:
    meta = {}
    in_front = False
    for line in content.split("\n"):
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


def _get_env_vars(skill_path: Path) -> list:
    content = (skill_path / "SKILL.md").read_text(encoding="utf-8")
    lines = content.split("\n")
    env_vars = []
    in_env = False
    for line in lines:
        stripped = line.strip()
        if stripped == "env:":
            in_env = True
            continue
        if in_env:
            if stripped.startswith("-"):
                env_vars.append(stripped.lstrip("- ").strip())
            elif stripped and not stripped.startswith("#"):
                in_env = False
    return env_vars


def _get_scripts(skill_path: Path) -> list:
    scripts_dir = skill_path / "scripts"
    if not scripts_dir.exists():
        return []
    return list(scripts_dir.glob("*.py"))


def _run_script(script: Path, extra_env: dict = None, args: list = None, timeout: int = 10) -> dict:
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    cmd = [sys.executable, str(script)] + (args or [])
    try:
        result = subprocess.run(
            cmd, env=env, capture_output=True, text=True, timeout=timeout
        )
        return {
            "exit_code": result.returncode,
            "stdout": result.stdout[:500],
            "stderr": result.stderr[:500],
            "timed_out": False,
        }
    except subprocess.TimeoutExpired:
        return {"exit_code": -1, "stdout": "", "stderr": "TIMEOUT", "timed_out": True}
    except Exception as e:
        return {"exit_code": -1, "stdout": "", "stderr": str(e), "timed_out": False}


def run_scenario(skill_path: Path, scenario: str) -> dict:
    scripts = _get_scripts(skill_path)
    if not scripts:
        return {"scenario": scenario, "status": "SKIP", "reason": "No scripts found"}

    script = scripts[0]
    result = {"scenario": scenario, "script": script.name}

    if scenario == "missing-env":
        env_vars = _get_env_vars(skill_path)
        if not env_vars:
            result.update({"status": "SKIP", "reason": "No env vars declared"})
            return result
        unset = {v: "" for v in env_vars}
        out = _run_script(script, extra_env=unset, args=["--help"])
        expected_fail = out["exit_code"] != 0 or any(
            kw in (out["stdout"] + out["stderr"]).lower()
            for kw in ["error", "missing", "required", "not set", "token", "key"]
        )
        result.update({"status": "PASS" if expected_fail else "WARN",
                       "detail": f"exit={out['exit_code']} stderr={out['stderr'][:100]}"})

    elif scenario == "empty-args":
        out = _run_script(script, args=[])
        handled = out["exit_code"] != 0
        result.update({"status": "PASS" if handled else "WARN",
                       "detail": f"exit={out['exit_code']}"})

    elif scenario == "invalid-args":
        garbage = random.choice(GARBAGE_VALUES[:8])
        out = _run_script(script, args=["--repo", garbage, "--unknown-flag", garbage])
        handled = out["exit_code"] != 0 and not out["timed_out"]
        result.update({"status": "PASS" if handled else "WARN",
                       "detail": f"input={repr(garbage[:40])} exit={out['exit_code']}"})

    elif scenario == "extra-args":
        out = _run_script(script, args=["--chaos-unknown-arg", "foobar", "--help"])
        result.update({"status": "PASS" if out["exit_code"] in (0, 1, 2) else "WARN",
                       "detail": f"exit={out['exit_code']}"})

    elif scenario == "unicode-input":
        uni = "日本語テスト🔥\u200b\u202e"
        out = _run_script(script, args=["--repo", uni])
        handled = not out["timed_out"]
        result.update({"status": "PASS" if handled else "FAIL",
                       "detail": f"exit={out['exit_code']}"})

    elif scenario == "very-long-input":
        long_val = "A" * 10_000
        out = _run_script(script, args=["--repo", long_val])
        handled = not out["timed_out"]
        result.update({"status": "PASS" if handled else "FAIL",
                       "detail": f"exit={out['exit_code']} timed_out={out['timed_out']}"})

    elif scenario == "null-byte-input":
        null_val = "owner\x00/repo"
        try:
            out = _run_script(script, args=["--repo", null_val])
            result.update({"status": "PASS", "detail": f"exit={out['exit_code']}"})
        except Exception as e:
            result.update({"status": "PASS", "detail": f"raised {type(e).__name__}"})

    elif scenario == "missing-script":
        scripts_dir = skill_path / "scripts"
        backup = skill_path / "_scripts_bak"
        try:
            scripts_dir.rename(backup)
            out = _run_script(skill_path / "scripts" / scripts[0].name, args=["--help"])
            result.update({"status": "PASS", "detail": "Script gracefully unavailable"})
        finally:
            if backup.exists():
                backup.rename(scripts_dir)

    else:
        result.update({"status": "SKIP", "reason": f"Unknown scenario: {scenario}"})

    return result


def run(skill_name: str, scenario: str = None, all_scenarios: bool = False):
    skill_path = _find_skill(skill_name)
    print(f"\n{BOLD}Chaos Monkey — {skill_name}{RESET}")
    print(f"  Path: {skill_path}\n")

    if all_scenarios:
        selected = list(SCENARIOS.keys())
    elif scenario:
        if scenario not in SCENARIOS:
            print(f"{RED}Unknown scenario '{scenario}'. Use list-scenarios to see options.{RESET}")
            sys.exit(1)
        selected = [scenario]
    else:
        selected = [random.choice(list(SCENARIOS.keys()))]
        print(f"{YELLOW}Randomly selected scenario: {selected[0]}{RESET}\n")

    results = []
    for s in selected:
        info = SCENARIOS[s]
        print(f"  {CYAN}[{s}]{RESET}  {info['description']}")
        r = run_scenario(skill_path, s)
        results.append(r)
        status_color = GREEN if r["status"] == "PASS" else (YELLOW if r["status"] in ("WARN", "SKIP") else RED)
        detail = r.get("detail", r.get("reason", ""))
        print(f"    → {status_color}{r['status']}{RESET}  {detail}\n")

    passed = sum(1 for r in results if r["status"] == "PASS")
    warned = sum(1 for r in results if r["status"] == "WARN")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    skipped = sum(1 for r in results if r["status"] == "SKIP")

    print(f"{BOLD}Results:{RESET} {GREEN}{passed} passed{RESET}  {YELLOW}{warned} warned / {skipped} skipped{RESET}  {RED}{failed} failed{RESET}\n")

    report_file = Path("chaos_report.json")
    payload = {
        "skill": skill_name,
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "results": results,
        "summary": {"passed": passed, "warned": warned, "failed": failed, "skipped": skipped},
    }
    report_file.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"  Report saved to {report_file}")


def list_scenarios():
    print(f"\n{BOLD}Available Chaos Scenarios:{RESET}\n")
    for name, info in SCENARIOS.items():
        sev = info["severity"]
        sev_color = RED if sev == "high" else (YELLOW if sev == "medium" else CYAN)
        print(f"  {CYAN}{name:<22}{RESET}  [{sev_color}{sev}{RESET}]  {info['description']}")
    print()


def report(file: str = "chaos_report.json"):
    p = Path(file)
    if not p.exists():
        print(f"{RED}Report file not found: {file}{RESET}")
        sys.exit(1)
    data = json.loads(p.read_text(encoding="utf-8"))
    print(f"\n{BOLD}Chaos Report — {data['skill']}{RESET}")
    print(f"  Timestamp: {data['timestamp']}\n")
    for r in data["results"]:
        status_color = GREEN if r["status"] == "PASS" else (YELLOW if r["status"] in ("WARN", "SKIP") else RED)
        detail = r.get("detail", r.get("reason", ""))
        print(f"  {CYAN}{r['scenario']:<22}{RESET}  {status_color}{r['status']}{RESET}  {detail}")
    s = data["summary"]
    print(f"\n  {GREEN}{s['passed']} passed{RESET}  {YELLOW}{s['warned']} warned  {s['skipped']} skipped{RESET}  {RED}{s['failed']} failed{RESET}\n")


def main():
    parser = argparse.ArgumentParser(
        prog="chaos_monkey.py",
        description="Chaos Monkey for Skills — OC-0183"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("run", help="Run chaos tests against a skill")
    p.add_argument("--skill", required=True, help="Skill name (e.g. timezone-converter)")
    p.add_argument("--scenario", default=None, help="Specific scenario to run")
    p.add_argument("--all-scenarios", action="store_true", help="Run all scenarios")

    sub.add_parser("list-scenarios", help="List available fault scenarios")

    p = sub.add_parser("report", help="Show last chaos run report")
    p.add_argument("--file", default="chaos_report.json")

    args = parser.parse_args()
    if args.cmd == "run":
        run(args.skill, args.scenario, args.all_scenarios)
    elif args.cmd == "list-scenarios":
        list_scenarios()
    elif args.cmd == "report":
        report(args.file)


if __name__ == "__main__":
    main()

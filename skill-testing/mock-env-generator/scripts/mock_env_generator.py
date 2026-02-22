#!/usr/bin/env python3
"""
Mock Environment Generator — OC-0179
Create sandboxed temp directories/files for safe file operation testing.
"""

import os
import sys
import json
import shutil
import argparse
import tempfile
from datetime import datetime, timezone
from pathlib import Path

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

REGISTRY_FILE = os.path.expanduser("~/.mock_envs.json")

FIXTURE_TEMPLATES = {
    "transactions": [
        {"date": "2024-01-15", "description": "Coffee Shop", "amount": 4.50, "type": "expense"},
        {"date": "2024-01-16", "description": "Salary", "amount": 3500.00, "type": "income"},
        {"date": "2024-01-17", "description": "Grocery Store", "amount": 67.20, "type": "expense"},
    ],
    "contacts": [
        {"email": "alice@example.com", "name": "Alice Smith", "company": "Acme Corp"},
        {"email": "bob@example.com", "name": "Bob Jones", "company": "TechCo"},
    ],
    "emails": [
        {"id": "msg001", "subject": "Project Update", "from": "alice@example.com",
         "body": "Hello, just a quick update on the project...", "read": False},
        {"id": "msg002", "subject": "Meeting Tomorrow", "from": "bob@example.com",
         "body": "Can we reschedule our meeting?", "read": False},
    ],
    "habits": {
        "habits": {
            "Read 30 min": {"emoji": "📚", "created": "2024-01-01",
                             "completions": ["2024-01-15", "2024-01-16"]},
            "Exercise": {"emoji": "🏃", "created": "2024-01-01",
                          "completions": ["2024-01-14", "2024-01-15", "2024-01-16"]},
        }
    },
}


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _load_registry() -> dict:
    if os.path.exists(REGISTRY_FILE):
        try:
            with open(REGISTRY_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {"envs": {}}


def _save_registry(data: dict):
    with open(REGISTRY_FILE, "w") as f:
        json.dump(data, f, indent=2)


def create(name: str, files: str = "", env_vars: str = ""):
    reg = _load_registry()
    if name in reg["envs"]:
        print(f"{YELLOW}Environment '{name}' already exists.{RESET}")
        return

    # Create temp directory
    tmp_dir = tempfile.mkdtemp(prefix=f"oc_mock_{name}_")

    created_files = []
    if files:
        for fname in files.split(","):
            fname = fname.strip()
            if not fname:
                continue
            fpath = Path(tmp_dir) / fname
            if fname.endswith(".json"):
                fpath.write_text(json.dumps({"mock": True, "name": fname}, indent=2))
            elif fname.endswith(".txt"):
                fpath.write_text(f"# Mock file: {fname}\n")
            elif fname.endswith(".csv"):
                fpath.write_text("date,description,amount,type\n2024-01-15,Coffee,4.50,expense\n")
            else:
                fpath.touch()
            created_files.append(str(fpath))

    # Generate .env file
    env_file = None
    if env_vars:
        env_path = Path(tmp_dir) / ".env"
        env_content = "\n".join(f"{v.strip()}=MOCK_VALUE" for v in env_vars.split(","))
        env_path.write_text(env_content)
        env_file = str(env_path)
        created_files.append(env_file)

    reg["envs"][name] = {
        "path": tmp_dir,
        "created": datetime.now(timezone.utc).isoformat(),
        "files": created_files,
        "env_file": env_file,
    }
    _save_registry(reg)

    print(f"{GREEN}Mock environment created: {name}{RESET}")
    print(f"  Path: {CYAN}{tmp_dir}{RESET}")
    if created_files:
        print(f"  Files: {len(created_files)}")
        for f in created_files:
            print(f"    {Path(f).name}")
    print()


def teardown(name: str):
    reg = _load_registry()
    if name not in reg["envs"]:
        _die(f"Environment '{name}' not found.")

    env = reg["envs"][name]
    path = env.get("path", "")

    if os.path.exists(path):
        shutil.rmtree(path)
        print(f"{GREEN}Removed: {path}{RESET}")

    del reg["envs"][name]
    _save_registry(reg)
    print(f"{GREEN}Environment '{name}' torn down.{RESET}")
    print()


def list_envs():
    reg = _load_registry()
    envs = reg.get("envs", {})
    if not envs:
        print(f"{YELLOW}No active mock environments.{RESET}")
        return

    print(f"\n{BOLD}Active Mock Environments ({len(envs)}):{RESET}\n")
    for name, env in envs.items():
        path    = env.get("path", "")
        exists  = os.path.exists(path)
        color   = GREEN if exists else RED
        status  = "active" if exists else "stale"
        created = env.get("created", "")[:10]
        files   = len(env.get("files", []))
        print(f"  {color}{name}{RESET}  [{status}]  {created}  {files} file(s)")
        print(f"    {path}")
    print()


def scaffold(skill_name: str, fixtures: str = ""):
    tmp_dir = tempfile.mkdtemp(prefix=f"oc_scaffold_{skill_name}_")

    print(f"{YELLOW}Scaffolding test environment for '{skill_name}'...{RESET}")
    print(f"  Path: {CYAN}{tmp_dir}{RESET}\n")

    # Create standard structure
    (Path(tmp_dir) / "fixtures").mkdir()
    (Path(tmp_dir) / "outputs").mkdir()

    created = []
    # Always create a config fixture
    config_path = Path(tmp_dir) / "fixtures" / "config.json"
    config_path.write_text(json.dumps({
        "skill": skill_name,
        "test": True,
        "env": {"mock": True},
    }, indent=2))
    created.append("fixtures/config.json")

    # Create requested fixtures
    if fixtures:
        for fixture_name in fixtures.split(","):
            fixture_name = fixture_name.strip()
            if fixture_name in FIXTURE_TEMPLATES:
                data = FIXTURE_TEMPLATES[fixture_name]
                fpath = Path(tmp_dir) / "fixtures" / f"{fixture_name}.json"
                fpath.write_text(json.dumps(data, indent=2))
                created.append(f"fixtures/{fixture_name}.json")
                print(f"  {GREEN}✓ Created fixture: {fixture_name}{RESET}")

    # Create test runner
    test_runner = Path(tmp_dir) / "run_test.sh"
    test_runner.write_text(
        f"#!/bin/bash\n# Test runner for {skill_name}\n"
        f"# Set up environment\nexport MOCK_MODE=true\n\n"
        f"# Run skill commands here\necho 'Add test commands below'\n"
    )
    test_runner.chmod(0o755)
    created.append("run_test.sh")

    print(f"\n{GREEN}Scaffold created at: {tmp_dir}{RESET}")
    print(f"  Files: {', '.join(created)}")
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="mock_env_generator.py",
        description="Mock Environment Generator — OC-0179"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("create", help="Create a mock environment")
    p.add_argument("--name", required=True)
    p.add_argument("--files", default="", help="Comma-separated filenames to create")
    p.add_argument("--env-vars", default="", help="Comma-separated env var names to mock")

    p = sub.add_parser("teardown", help="Remove a mock environment")
    p.add_argument("--name", required=True)

    sub.add_parser("list", help="List active environments")

    p = sub.add_parser("scaffold", help="Generate test scaffold for a skill")
    p.add_argument("--skill", required=True)
    p.add_argument("--fixtures", default="", help="Comma-separated fixture names")

    args = parser.parse_args()
    dispatch = {
        "create":   lambda: create(args.name, args.files, args.env_vars),
        "teardown": lambda: teardown(args.name),
        "list":     lambda: list_envs(),
        "scaffold": lambda: scaffold(args.skill, args.fixtures),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()

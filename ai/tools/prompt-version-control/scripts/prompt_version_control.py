#!/usr/bin/env python3
"""Prompt Version Control – OC-0115"""

import argparse
import os
import sys
import subprocess

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

STORE = os.path.expanduser("~/.openclaw/prompts")


def _git(args, cwd=STORE, check=True):
    result = subprocess.run(["git"] + args, cwd=cwd, capture_output=True, text=True)
    if check and result.returncode != 0:
        print(f"{RED}git error: {result.stderr}{RESET}")
        sys.exit(1)
    return result.stdout.strip()


def _init_store():
    os.makedirs(STORE, exist_ok=True)
    if not os.path.exists(os.path.join(STORE, ".git")):
        _git(["init"])
        _git(["commit", "--allow-empty", "-m", "Init prompt store"])


def save(args):
    _init_store()
    name = args.name
    prompt_dir = os.path.join(STORE, name)
    os.makedirs(prompt_dir, exist_ok=True)
    dest = os.path.join(prompt_dir, "prompt.txt")
    if args.file:
        with open(args.file) as f:
            content = f.read()
    else:
        print(f"{YELLOW}Enter prompt content (Ctrl+D to finish):{RESET}")
        content = sys.stdin.read()
    with open(dest, "w") as f:
        f.write(content)
    _git(["add", dest])
    msg = args.message or f"Update {name}"
    _git(["commit", "-m", msg])
    print(f"{GREEN}Saved prompt '{name}'{RESET}")


def list_prompts(args):
    _init_store()
    entries = [d for d in os.listdir(STORE) if os.path.isdir(os.path.join(STORE, d)) and d != ".git"]
    if not entries:
        print(f"{YELLOW}No prompts saved yet.{RESET}")
        return
    print(f"{GREEN}Saved prompts:{RESET}")
    for name in sorted(entries):
        log = _git(["log", "--oneline", "-3", "--", f"{name}/prompt.txt"], check=False)
        print(f"  {GREEN}{name}{RESET}")
        for line in log.splitlines():
            print(f"    {line}")


def load(args):
    _init_store()
    prompt_file = os.path.join(STORE, args.name, "prompt.txt")
    if args.version:
        content = _git(["show", f"{args.version}:{args.name}/prompt.txt"])
    elif os.path.exists(prompt_file):
        with open(prompt_file) as f:
            content = f.read()
    else:
        print(f"{RED}Prompt '{args.name}' not found{RESET}")
        sys.exit(1)
    print(content)


def diff(args):
    _init_store()
    result = _git(["diff", args.v1, args.v2, "--", f"{args.name}/prompt.txt"])
    if result:
        print(result)
    else:
        print(f"{YELLOW}No differences found{RESET}")


def tag(args):
    _init_store()
    _git(["tag", args.tag, "HEAD"])
    print(f"{GREEN}Tagged HEAD as '{args.tag}' for prompt '{args.name}'{RESET}")


def rollback(args):
    _init_store()
    content = _git(["show", f"{args.version}:{args.name}/prompt.txt"])
    dest = os.path.join(STORE, args.name, "prompt.txt")
    with open(dest, "w") as f:
        f.write(content)
    _git(["add", dest])
    _git(["commit", "-m", f"Rollback {args.name} to {args.version}"])
    print(f"{GREEN}Rolled back '{args.name}' to {args.version}{RESET}")


def main():
    parser = argparse.ArgumentParser(description="Prompt Version Control")
    sub = parser.add_subparsers(dest="command", required=True)

    p_s = sub.add_parser("save")
    p_s.add_argument("--name", required=True)
    p_s.add_argument("--file", default=None)
    p_s.add_argument("--message", default=None)

    sub.add_parser("list")

    p_l = sub.add_parser("load")
    p_l.add_argument("--name", required=True)
    p_l.add_argument("--version", default=None)

    p_d = sub.add_parser("diff")
    p_d.add_argument("--name", required=True)
    p_d.add_argument("--v1", default="HEAD~1")
    p_d.add_argument("--v2", default="HEAD")

    p_t = sub.add_parser("tag")
    p_t.add_argument("--name", required=True)
    p_t.add_argument("--tag", required=True)

    p_r = sub.add_parser("rollback")
    p_r.add_argument("--name", required=True)
    p_r.add_argument("--version", required=True)

    args = parser.parse_args()
    dispatch = {
        "save": save, "list": list_prompts, "load": load,
        "diff": diff, "tag": tag, "rollback": rollback,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()

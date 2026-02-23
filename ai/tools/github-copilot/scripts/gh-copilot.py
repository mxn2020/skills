#!/usr/bin/env python3
"""
Copilot CLI Skill — wrapper for the `copilot` binary for AI agents.

What this tool IS:
  The GitHub Copilot CLI (`copilot`) is a LOCAL, interactive, agentic terminal
  tool. It runs on the host machine, reads local files, edits local files, and
  runs shell commands — all within the current working directory.

What this tool is NOT:
  - It is NOT `gh copilot` (that extension is deprecated since Oct 25 2025).
  - It is NOT `gh agent-task` (that creates remote tasks that open PRs).
  - It does NOT operate on remote repos by itself.

Install:  npm install -g @github/copilot
Auth:     GH_TOKEN or GITHUB_TOKEN env var (fine-grained PAT with
          "Copilot Requests" permission), or run `copilot` once and use /login.

Programmatic mode:
  copilot --prompt "<task>" [approval flags] [tool flags]

  Approval flags (required for non-interactive use; without them copilot
  pauses and asks before every file write or shell command):
    --allow-all-tools          Allow all tools without individual approval
    --allow-tool <spec>        Allow a specific tool (can repeat)
    --deny-tool  <spec>        Deny a specific tool  (can repeat)

  Tool specs:  shell  write  gh  git  shell(<cmd>)  gh(<subcmd>)  <mcp-server>

  Other flags:
    --experimental             Enable experimental/preview features
    --trust-all-repos          Trust all dirs without a saved trust decision
    --model <name>             Override the AI model

This skill gives AI agents a clean, safe interface for running Copilot CLI
tasks non-interactively from a known working directory.
"""

import sys
import os
import argparse
import subprocess
import shutil
from pathlib import Path


RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"


# ── Helpers ───────────────────────────────────────────────────────────────────

def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def check_copilot():
    """Verify the `copilot` binary is on PATH."""
    if shutil.which("copilot") is None:
        _die(
            "'copilot' binary not found.\n"
            "Install: npm install -g @github/copilot\n"
            "Docs:    https://github.com/github/copilot-cli"
        )


def _build_env(token: str | None = None) -> dict:
    """Build the subprocess environment, optionally injecting a token."""
    env = os.environ.copy()
    if token:
        env["GH_TOKEN"] = token
    return env


# ── Core run function ─────────────────────────────────────────────────────────

def run_task(
    prompt: str,
    cwd: str | None = None,
    allow_all_tools: bool = False,
    allow_tools: list[str] | None = None,
    deny_tools: list[str] | None = None,
    model: str | None = None,
    experimental: bool = False,
    trust_all_repos: bool = False,
    token: str | None = None,
):
    """
    Run a Copilot CLI task non-interactively.

    copilot --prompt "<task>"
            [--allow-all-tools | --allow-tool <spec> ...]
            [--deny-tool <spec> ...]
            [--model <name>]
            [--experimental]
            [--trust-all-repos]

    The process inherits stdout/stderr so streaming output is visible.
    cwd sets the working directory Copilot operates in (defaults to cwd).
    """
    work_dir = Path(cwd).resolve() if cwd else Path.cwd()
    if not work_dir.is_dir():
        _die(f"Working directory does not exist: {work_dir}")

    args = ["copilot", "--prompt", prompt]

    if allow_all_tools:
        args.append("--allow-all-tools")
    else:
        for t in (allow_tools or []):
            args += ["--allow-tool", t]

    for t in (deny_tools or []):
        args += ["--deny-tool", t]

    if model:
        args += ["--model", model]
    if experimental:
        args.append("--experimental")
    if trust_all_repos:
        args.append("--trust-all-repos")

    print(f"{YELLOW}Running Copilot CLI task in: {work_dir}{RESET}")
    print(f"  Prompt: {prompt[:120]}{'…' if len(prompt) > 120 else ''}")
    if allow_all_tools:
        print(f"  {YELLOW}Tools: all allowed (--allow-all-tools){RESET}")
    elif allow_tools:
        print(f"  Tools allowed: {', '.join(allow_tools)}")
    if deny_tools:
        print(f"  Tools denied:  {', '.join(deny_tools)}")

    try:
        subprocess.run(args, cwd=str(work_dir), env=_build_env(token), check=True)
    except subprocess.CalledProcessError as e:
        _die(f"copilot exited with code {e.returncode}")


# ── CLI parser ────────────────────────────────────────────────────────────────

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="copilot_skill.py",
        description=(
            "Copilot CLI skill: runs GitHub Copilot CLI (`copilot`) tasks locally.\n"
            "Operates on files in the current working directory.\n"
            "Install copilot: npm install -g @github/copilot"
        ),
    )
    sub = p.add_subparsers(dest="cmd", required=True)

    # ── run ───────────────────────────────────────────────────────────────────
    r = sub.add_parser(
        "run",
        help="Run a Copilot CLI task non-interactively.",
        description=(
            "Executes: copilot --prompt '<task>' [approval/tool flags]\n\n"
            "Without any --allow-* flag, copilot will pause at every file write\n"
            "or shell command and ask for approval — unusable for automation.\n"
            "Use --allow-all-tools for full autonomy, or list specific tools.\n\n"
            "Tool spec examples: shell  write  gh  git  shell(rm)  gh(pr)"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    r.add_argument(
        "prompt",
        help="Natural language task description.",
    )
    r.add_argument(
        "--cwd",
        default=None,
        help="Working directory for Copilot to operate in (default: current dir).",
    )
    r.add_argument(
        "--allow-all-tools",
        action="store_true",
        dest="allow_all_tools",
        help=(
            "Allow Copilot to use ALL tools (file writes, shell commands, etc.) "
            "without individual approval. Required for non-interactive use. "
            "Copilot has the same access as the current user."
        ),
    )
    r.add_argument(
        "--allow-tool",
        action="append",
        default=[],
        dest="allow_tools",
        metavar="SPEC",
        help=(
            "Allow a specific tool without approval (repeatable). "
            "Examples: shell  write  gh  git  shell(rm)  gh(pr)  <mcp-server-name>"
        ),
    )
    r.add_argument(
        "--deny-tool",
        action="append",
        default=[],
        dest="deny_tools",
        metavar="SPEC",
        help=(
            "Deny a specific tool entirely (repeatable). "
            "Example: --deny-tool 'shell(rm)' blocks any rm command."
        ),
    )
    r.add_argument(
        "--model",
        default=None,
        help=(
            "Override the AI model. Default is Claude Sonnet 4.5. "
            "Other available models: Claude Sonnet 4, GPT-5 (run /model interactively to see full list)."
        ),
    )
    r.add_argument(
        "--experimental",
        action="store_true",
        help="Enable experimental/preview features.",
    )
    r.add_argument(
        "--trust-all-repos",
        action="store_true",
        dest="trust_all_repos",
        help="Trust all directories without a saved trust decision.",
    )
    r.add_argument(
        "--token",
        default=None,
        help=(
            "GitHub token (fine-grained PAT with 'Copilot Requests' permission). "
            "Overrides GH_TOKEN env var."
        ),
    )

    return p


def main():
    args = build_parser().parse_args()
    check_copilot()

    if args.cmd == "run":
        run_task(
            prompt          = args.prompt,
            cwd             = args.cwd,
            allow_all_tools = args.allow_all_tools,
            allow_tools     = args.allow_tools or [],
            deny_tools      = args.deny_tools  or [],
            model           = args.model,
            experimental    = args.experimental,
            trust_all_repos = args.trust_all_repos,
            token           = args.token,
        )


if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Changelog Generator - Auto-generate changelogs from commit history and PR titles.
Uses `gh` CLI and `git` for data collection.
"""

import sys
import os
import re
import json
import argparse
import subprocess
from datetime import datetime

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

COMMIT_TYPE_PATTERN = re.compile(r"^(feat|fix|docs|style|refactor|perf|test|chore|ci|build)(\(.+?\))?[!]?:\s*(.+)")


def run_command(command, check=True):
    try:
        result = subprocess.run(command, shell=True, check=check, capture_output=True, text=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"{RED}Command failed: {command}{RESET}")
        print(f"{RED}Error: {e.stderr}{RESET}")
        if check:
            sys.exit(1)
        return None


def check_dependencies():
    for cmd in ["gh", "git"]:
        try:
            subprocess.run([cmd, "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except (subprocess.CalledProcessError, FileNotFoundError):
            print(f"{RED}Error: '{cmd}' not found. Please install it.{RESET}")
            sys.exit(1)


def get_merged_prs(repo, since=None):
    """Fetch merged PR titles from GitHub."""
    cmd = f"gh pr list --repo {repo} --state merged --limit 100 --json number,title,mergedAt,labels"
    if since:
        cmd += f" --search 'merged:>={since}'"
    output = run_command(cmd, check=False)
    if not output:
        return []
    return json.loads(output)


def get_commits(since=None):
    """Get git log commits."""
    cmd = "git log --oneline --no-merges"
    if since:
        cmd += f" {since}..HEAD"
    cmd += " --format='%h %s'"
    output = run_command(cmd, check=False)
    if not output:
        return []
    lines = []
    for line in output.strip().split("\n"):
        line = line.strip().strip("'")
        if line:
            parts = line.split(" ", 1)
            if len(parts) == 2:
                lines.append({"hash": parts[0], "message": parts[1]})
    return lines


def categorize_entries(commits, prs):
    """Group entries by conventional commit type."""
    categories = {
        "Features": [],
        "Bug Fixes": [],
        "Documentation": [],
        "Performance": [],
        "Refactoring": [],
        "Tests": [],
        "CI/Build": [],
        "Other": [],
    }
    type_map = {
        "feat": "Features",
        "fix": "Bug Fixes",
        "docs": "Documentation",
        "perf": "Performance",
        "refactor": "Refactoring",
        "test": "Tests",
        "ci": "CI/Build",
        "build": "CI/Build",
        "style": "Other",
        "chore": "Other",
    }

    seen = set()

    # Process PRs first
    for pr in prs:
        entry = f"#{pr['number']} {pr['title']}"
        if entry not in seen:
            seen.add(entry)
            match = COMMIT_TYPE_PATTERN.match(pr["title"])
            if match:
                cat = type_map.get(match.group(1), "Other")
                categories[cat].append(entry)
            else:
                categories["Other"].append(entry)

    # Process commits
    for c in commits:
        if c["message"] in seen:
            continue
        seen.add(c["message"])
        match = COMMIT_TYPE_PATTERN.match(c["message"])
        if match:
            cat = type_map.get(match.group(1), "Other")
            categories[cat].append(f"{c['hash']} {c['message']}")
        else:
            categories["Other"].append(f"{c['hash']} {c['message']}")

    return {k: v for k, v in categories.items() if v}


def format_changelog(categories, version=None):
    """Format categorized entries into markdown."""
    date_str = datetime.now().strftime("%Y-%m-%d")
    header = f"## [{version}] - {date_str}" if version else f"## [Unreleased] - {date_str}"

    lines = [header, ""]
    for category, entries in categories.items():
        lines.append(f"### {category}")
        lines.append("")
        for entry in entries:
            lines.append(f"- {entry}")
        lines.append("")

    return "\n".join(lines)


def generate(repo, output="CHANGELOG.md", since=None, group_by="type"):
    print(f"{YELLOW}Generating changelog for {repo}...{RESET}")
    prs = get_merged_prs(repo, since)
    commits = get_commits(since)

    if not prs and not commits:
        print(f"{YELLOW}No entries found.{RESET}")
        return

    categories = categorize_entries(commits, prs)
    content = "# Changelog\n\n" + format_changelog(categories)

    with open(output, "w") as f:
        f.write(content)
    print(f"{GREEN}Changelog written to {output}{RESET}")
    print(f"  PRs processed: {len(prs)}")
    print(f"  Commits processed: {len(commits)}")


def preview(repo, since=None, group_by="type"):
    print(f"{YELLOW}Previewing changelog for {repo}...{RESET}\n")
    prs = get_merged_prs(repo, since)
    commits = get_commits(since)

    if not prs and not commits:
        print(f"{YELLOW}No entries found.{RESET}")
        return

    categories = categorize_entries(commits, prs)
    content = format_changelog(categories)
    print(content)


def append(repo, version, since, output="CHANGELOG.md"):
    print(f"{YELLOW}Appending version {version} to {output}...{RESET}")
    prs = get_merged_prs(repo, since)
    commits = get_commits(since)

    if not prs and not commits:
        print(f"{YELLOW}No entries found since {since}.{RESET}")
        return

    categories = categorize_entries(commits, prs)
    new_section = format_changelog(categories, version=version)

    existing = ""
    if os.path.exists(output):
        with open(output, "r") as f:
            existing = f.read()

    if existing.startswith("# Changelog"):
        header_end = existing.index("\n", existing.index("# Changelog")) + 1
        content = existing[:header_end] + "\n" + new_section + "\n" + existing[header_end:]
    else:
        content = "# Changelog\n\n" + new_section + "\n" + existing

    with open(output, "w") as f:
        f.write(content)
    print(f"{GREEN}Version {version} appended to {output}.{RESET}")


def main():
    parser = argparse.ArgumentParser(description="Changelog Generator")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_gen = subparsers.add_parser("generate", help="Generate full changelog")
    p_gen.add_argument("--repo", required=True, help="Repository (owner/name)")
    p_gen.add_argument("--output", default="CHANGELOG.md")
    p_gen.add_argument("--since", help="Start from tag/ref")
    p_gen.add_argument("--group-by", default="type", choices=["type"])

    p_preview = subparsers.add_parser("preview", help="Preview changelog")
    p_preview.add_argument("--repo", required=True)
    p_preview.add_argument("--since", help="Start from tag/ref")
    p_preview.add_argument("--group-by", default="type", choices=["type"])

    p_append = subparsers.add_parser("append", help="Append new version section")
    p_append.add_argument("--repo", required=True)
    p_append.add_argument("--version", required=True, help="Version string")
    p_append.add_argument("--since", required=True, help="Start from tag/ref")
    p_append.add_argument("--output", default="CHANGELOG.md")

    args = parser.parse_args()
    check_dependencies()

    if args.command == "generate":
        generate(args.repo, args.output, args.since, args.group_by)
    elif args.command == "preview":
        preview(args.repo, args.since, args.group_by)
    elif args.command == "append":
        append(args.repo, args.version, args.since, args.output)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
GitHub PR Automated Reviewer - Verify diffs against style guides and flag violations.
Uses the `gh` CLI for GitHub API interactions.
"""

import sys
import json
import re
import argparse
import subprocess

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"


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
    try:
        subprocess.run(["gh", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print(f"{RED}Error: 'gh' CLI not found. Please install GitHub CLI.{RESET}")
        sys.exit(1)


def list_prs(repo, state="open", limit=30):
    print(f"{YELLOW}Listing {state} PRs for {repo}...{RESET}")
    cmd = f"gh pr list --repo {repo} --state {state} --limit {limit} --json number,title,state,author,url"
    output = run_command(cmd)
    prs = json.loads(output)
    print(f"{GREEN}Found {len(prs)} pull requests:{RESET}")
    for pr in prs:
        author = pr.get("author", {}).get("login", "unknown")
        print(f"  #{pr['number']} [{pr['state']}] {pr['title']} (by {author})")


def review_pr(repo, pr_number, post_comment=False):
    print(f"{YELLOW}Reviewing PR #{pr_number} in {repo}...{RESET}")
    diff = run_command(f"gh pr diff {pr_number} --repo {repo}")
    if not diff:
        print(f"{RED}No diff found for PR #{pr_number}.{RESET}")
        return

    findings = []
    lines = diff.split("\n")
    current_file = None
    line_num = 0

    for line in lines:
        if line.startswith("diff --git"):
            match = re.search(r"b/(.+)$", line)
            current_file = match.group(1) if match else "unknown"
            line_num = 0
        elif line.startswith("@@"):
            match = re.search(r"\+(\d+)", line)
            line_num = int(match.group(1)) if match else 0
        elif line.startswith("+") and not line.startswith("+++"):
            content = line[1:]
            line_num += 1
            if len(content) > 120:
                findings.append(f"  {current_file}:{line_num} - Line exceeds 120 characters ({len(content)})")
            if "TODO" in content or "FIXME" in content or "HACK" in content:
                findings.append(f"  {current_file}:{line_num} - Contains TODO/FIXME/HACK marker")
            if content != content.rstrip():
                findings.append(f"  {current_file}:{line_num} - Trailing whitespace")
            if "\t" in content and current_file and not current_file.endswith(("Makefile", ".go", ".mk")):
                findings.append(f"  {current_file}:{line_num} - Uses tabs instead of spaces")
            if ("console.log(" in content or "print(" in content) and "debug" in content.lower():
                findings.append(f"  {current_file}:{line_num} - Possible debug statement left in code")

    pr_info = json.loads(run_command(
        f"gh pr view {pr_number} --repo {repo} --json title,additions,deletions,changedFiles"
    ))

    print(f"\n{GREEN}PR #{pr_number}: {pr_info['title']}{RESET}")
    print(f"  Files changed: {pr_info['changedFiles']}")
    print(f"  +{pr_info['additions']} / -{pr_info['deletions']}")

    if findings:
        print(f"\n{YELLOW}Findings ({len(findings)}):{RESET}")
        for f in findings:
            print(f)
    else:
        print(f"\n{GREEN}No style issues found.{RESET}")

    if post_comment and findings:
        body = "## Automated Review Findings\\n\\n" + "\\n".join(findings)
        run_command(f'gh pr comment {pr_number} --repo {repo} --body "{body}"')
        print(f"{GREEN}Review comment posted.{RESET}")


def check_style(repo, pr_number, max_line_length=120):
    print(f"{YELLOW}Checking style for PR #{pr_number} in {repo}...{RESET}")
    diff = run_command(f"gh pr diff {pr_number} --repo {repo}")
    if not diff:
        print(f"{RED}No diff found.{RESET}")
        return

    violations = []
    current_file = None
    line_num = 0

    for line in diff.split("\n"):
        if line.startswith("diff --git"):
            match = re.search(r"b/(.+)$", line)
            current_file = match.group(1) if match else "unknown"
            line_num = 0
        elif line.startswith("@@"):
            match = re.search(r"\+(\d+)", line)
            line_num = int(match.group(1)) if match else 0
        elif line.startswith("+") and not line.startswith("+++"):
            content = line[1:]
            line_num += 1
            if len(content) > max_line_length:
                violations.append(
                    f"  {current_file}:{line_num} - Line length {len(content)} > {max_line_length}"
                )
            if content != content.rstrip():
                violations.append(f"  {current_file}:{line_num} - Trailing whitespace")

    if violations:
        print(f"{RED}Found {len(violations)} style violations:{RESET}")
        for v in violations:
            print(v)
    else:
        print(f"{GREEN}No style violations found.{RESET}")


def summarize_diff(repo, pr_number):
    print(f"{YELLOW}Summarizing PR #{pr_number} in {repo}...{RESET}")
    pr_info = json.loads(run_command(
        f"gh pr view {pr_number} --repo {repo} "
        f"--json title,body,additions,deletions,changedFiles,files"
    ))
    files = pr_info.get("files", [])

    print(f"\n{GREEN}PR #{pr_number}: {pr_info['title']}{RESET}")
    print(f"  Total: {pr_info['changedFiles']} files, +{pr_info['additions']}/-{pr_info['deletions']}")
    if pr_info.get("body"):
        desc = pr_info["body"][:200]
        print(f"  Description: {desc}{'...' if len(pr_info['body']) > 200 else ''}")

    if files:
        print(f"\n  {YELLOW}Changed files:{RESET}")
        for f in files:
            print(f"    {f['path']} (+{f['additions']}/-{f['deletions']})")

    # Group by extension
    ext_stats = {}
    for f in files:
        ext = f["path"].rsplit(".", 1)[-1] if "." in f["path"] else "other"
        ext_stats.setdefault(ext, {"count": 0, "adds": 0, "dels": 0})
        ext_stats[ext]["count"] += 1
        ext_stats[ext]["adds"] += f["additions"]
        ext_stats[ext]["dels"] += f["deletions"]

    if ext_stats:
        print(f"\n  {YELLOW}By file type:{RESET}")
        for ext, stats in sorted(ext_stats.items(), key=lambda x: x[1]["count"], reverse=True):
            print(f"    .{ext}: {stats['count']} files (+{stats['adds']}/-{stats['dels']})")


def main():
    parser = argparse.ArgumentParser(description="GitHub PR Automated Reviewer")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_list = subparsers.add_parser("list-prs", help="List pull requests")
    p_list.add_argument("--repo", required=True)
    p_list.add_argument("--state", default="open", choices=["open", "closed", "merged", "all"])
    p_list.add_argument("--limit", type=int, default=30)

    p_review = subparsers.add_parser("review-pr", help="Review a pull request")
    p_review.add_argument("--repo", required=True)
    p_review.add_argument("--pr", type=int, required=True)
    p_review.add_argument("--post-comment", action="store_true")

    p_style = subparsers.add_parser("check-style", help="Check style violations")
    p_style.add_argument("--repo", required=True)
    p_style.add_argument("--pr", type=int, required=True)
    p_style.add_argument("--max-line-length", type=int, default=120)

    p_summary = subparsers.add_parser("summarize-diff", help="Summarize PR diff")
    p_summary.add_argument("--repo", required=True)
    p_summary.add_argument("--pr", type=int, required=True)

    args = parser.parse_args()
    check_dependencies()

    if args.command == "list-prs":
        list_prs(args.repo, args.state, args.limit)
    elif args.command == "review-pr":
        review_pr(args.repo, args.pr, args.post_comment)
    elif args.command == "check-style":
        check_style(args.repo, args.pr, args.max_line_length)
    elif args.command == "summarize-diff":
        summarize_diff(args.repo, args.pr)


if __name__ == "__main__":
    main()

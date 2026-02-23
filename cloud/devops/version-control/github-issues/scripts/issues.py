#!/usr/bin/env python3
"""
GitHub Issues Agent - Label, triage, close, and prioritize issues automatically.
Uses the `gh` CLI for GitHub API interactions.
"""

import sys
import json
import argparse
import subprocess

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

TRIAGE_KEYWORDS = {
    "bug": ["bug", "error", "crash", "fail", "broken", "fix", "issue", "defect"],
    "enhancement": ["feature", "enhance", "improve", "add", "request", "proposal"],
    "documentation": ["docs", "documentation", "readme", "typo", "spelling"],
    "question": ["question", "how", "help", "support", "explain"],
    "security": ["security", "vulnerability", "cve", "exploit", "injection"],
}

PRIORITY_KEYWORDS = {
    "priority: critical": ["critical", "urgent", "production down", "outage", "data loss"],
    "priority: high": ["important", "blocker", "severe", "major"],
    "priority: medium": ["moderate", "should", "needed"],
    "priority: low": ["minor", "cosmetic", "nice to have", "low"],
}


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


def list_issues(repo, state="open", limit=30, label=None):
    print(f"{YELLOW}Listing {state} issues for {repo}...{RESET}")
    cmd = f'gh issue list --repo {repo} --state {state} --limit {limit} --json number,title,state,labels,assignees,url'
    if label:
        cmd += f' --label "{label}"'
    output = run_command(cmd)
    issues = json.loads(output)
    print(f"{GREEN}Found {len(issues)} issues:{RESET}")
    for issue in issues:
        labels = ", ".join(l["name"] for l in issue.get("labels", []))
        label_str = f" [{labels}]" if labels else ""
        print(f"  #{issue['number']} {issue['title']}{label_str}")


def create_issue(repo, title, body="", labels="", assignee=""):
    print(f"{YELLOW}Creating issue in {repo}...{RESET}")
    cmd = f'gh issue create --repo {repo} --title "{title}"'
    if body:
        cmd += f' --body "{body}"'
    if labels:
        cmd += f' --label "{labels}"'
    if assignee:
        cmd += f' --assignee "{assignee}"'
    output = run_command(cmd)
    print(f"{GREEN}Issue created: {output}{RESET}")


def label_issue(repo, issue_number, labels):
    print(f"{YELLOW}Adding labels to #{issue_number} in {repo}...{RESET}")
    for label in labels.split(","):
        label = label.strip()
        run_command(f'gh issue edit {issue_number} --repo {repo} --add-label "{label}"')
        print(f"{GREEN}  Added label: {label}{RESET}")
    print(f"{GREEN}Labels updated for #{issue_number}.{RESET}")


def close_issue(repo, issue_number, comment=""):
    print(f"{YELLOW}Closing issue #{issue_number} in {repo}...{RESET}")
    if comment:
        run_command(f'gh issue comment {issue_number} --repo {repo} --body "{comment}"')
    run_command(f"gh issue close {issue_number} --repo {repo}")
    print(f"{GREEN}Issue #{issue_number} closed.{RESET}")


def triage(repo, limit=20):
    print(f"{YELLOW}Triaging issues in {repo}...{RESET}")
    output = run_command(
        f"gh issue list --repo {repo} --state open --limit {limit} "
        f"--json number,title,body,labels"
    )
    issues = json.loads(output)
    triaged = 0
    for issue in issues:
        existing = {l["name"] for l in issue.get("labels", [])}
        text = (issue.get("title", "") + " " + issue.get("body", "")).lower()
        new_labels = []
        for label, keywords in TRIAGE_KEYWORDS.items():
            if label not in existing and any(kw in text for kw in keywords):
                new_labels.append(label)
        if new_labels:
            for lbl in new_labels:
                run_command(f'gh issue edit {issue["number"]} --repo {repo} --add-label "{lbl}"', check=False)
            print(f"  #{issue['number']}: added [{', '.join(new_labels)}]")
            triaged += 1
    print(f"{GREEN}Triaged {triaged}/{len(issues)} issues.{RESET}")


def prioritize(repo, limit=20):
    print(f"{YELLOW}Prioritizing issues in {repo}...{RESET}")
    output = run_command(
        f"gh issue list --repo {repo} --state open --limit {limit} "
        f"--json number,title,body,labels"
    )
    issues = json.loads(output)
    prioritized = 0
    for issue in issues:
        existing = {l["name"] for l in issue.get("labels", [])}
        if any(l.startswith("priority:") for l in existing):
            continue
        text = (issue.get("title", "") + " " + issue.get("body", "")).lower()
        assigned = None
        for label, keywords in PRIORITY_KEYWORDS.items():
            if any(kw in text for kw in keywords):
                assigned = label
                break
        if assigned:
            run_command(f'gh issue edit {issue["number"]} --repo {repo} --add-label "{assigned}"', check=False)
            print(f"  #{issue['number']}: {assigned}")
            prioritized += 1
    print(f"{GREEN}Prioritized {prioritized}/{len(issues)} issues.{RESET}")


def main():
    parser = argparse.ArgumentParser(description="GitHub Issues Agent")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_list = subparsers.add_parser("list-issues", help="List issues")
    p_list.add_argument("--repo", required=True, help="Repository (owner/name)")
    p_list.add_argument("--state", default="open", choices=["open", "closed", "all"])
    p_list.add_argument("--limit", type=int, default=30)
    p_list.add_argument("--label", help="Filter by label")

    p_create = subparsers.add_parser("create-issue", help="Create an issue")
    p_create.add_argument("--repo", required=True)
    p_create.add_argument("--title", required=True)
    p_create.add_argument("--body", default="")
    p_create.add_argument("--labels", default="")
    p_create.add_argument("--assignee", default="")

    p_label = subparsers.add_parser("label-issue", help="Add labels to an issue")
    p_label.add_argument("--repo", required=True)
    p_label.add_argument("--issue", type=int, required=True)
    p_label.add_argument("--labels", required=True, help="Comma-separated labels")

    p_close = subparsers.add_parser("close-issue", help="Close an issue")
    p_close.add_argument("--repo", required=True)
    p_close.add_argument("--issue", type=int, required=True)
    p_close.add_argument("--comment", default="")

    p_triage = subparsers.add_parser("triage", help="Auto-triage issues")
    p_triage.add_argument("--repo", required=True)
    p_triage.add_argument("--limit", type=int, default=20)

    p_pri = subparsers.add_parser("prioritize", help="Prioritize issues")
    p_pri.add_argument("--repo", required=True)
    p_pri.add_argument("--limit", type=int, default=20)

    args = parser.parse_args()
    check_dependencies()

    if args.command == "list-issues":
        list_issues(args.repo, args.state, args.limit, args.label)
    elif args.command == "create-issue":
        create_issue(args.repo, args.title, args.body, args.labels, args.assignee)
    elif args.command == "label-issue":
        label_issue(args.repo, args.issue, args.labels)
    elif args.command == "close-issue":
        close_issue(args.repo, args.issue, args.comment)
    elif args.command == "triage":
        triage(args.repo, args.limit)
    elif args.command == "prioritize":
        prioritize(args.repo, args.limit)


if __name__ == "__main__":
    main()

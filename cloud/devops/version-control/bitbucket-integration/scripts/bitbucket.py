#!/usr/bin/env python3
"""
Bitbucket Integration - Sync Jira tickets with commits and manage repositories.
Uses Bitbucket REST API 2.0 via requests.
"""

import sys
import os
import re
import json
import argparse

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BITBUCKET_API = "https://api.bitbucket.org/2.0"
JIRA_PATTERN = re.compile(r"[A-Z][A-Z0-9]+-\d+")


def get_auth():
    username = os.environ.get("BITBUCKET_USERNAME")
    password = os.environ.get("BITBUCKET_APP_PASSWORD")
    if not username or not password:
        print(f"{RED}Error: BITBUCKET_USERNAME and BITBUCKET_APP_PASSWORD environment variables required.{RESET}")
        sys.exit(1)
    return (username, password)


def api_request(method, endpoint, auth, params=None, json_data=None):
    try:
        import requests
    except ImportError:
        print(f"{RED}Error: 'requests' library not installed. Run: pip install requests{RESET}")
        sys.exit(1)

    url = f"{BITBUCKET_API}{endpoint}"
    resp = requests.request(method, url, auth=auth, params=params, json=json_data, timeout=30)
    if resp.status_code >= 400:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.text else None


def list_repos(workspace, limit=25):
    auth = get_auth()
    print(f"{YELLOW}Listing repositories in workspace '{workspace}'...{RESET}")

    data = api_request("GET", f"/repositories/{workspace}", auth, params={"pagelen": limit})
    repos = data.get("values", [])
    print(f"{GREEN}Found {len(repos)} repositories:{RESET}")
    for repo in repos:
        lang = repo.get("language", "N/A")
        print(f"  {repo['slug']} ({lang}) - {repo.get('description', 'No description')[:60]}")


def list_prs(workspace, repo, state="OPEN"):
    auth = get_auth()
    print(f"{YELLOW}Listing {state} PRs for {workspace}/{repo}...{RESET}")

    data = api_request("GET", f"/repositories/{workspace}/{repo}/pullrequests", auth,
                       params={"state": state, "pagelen": 25})
    prs = data.get("values", [])
    print(f"{GREEN}Found {len(prs)} pull requests:{RESET}")
    for pr in prs:
        author = pr.get("author", {}).get("display_name", "unknown")
        print(f"  #{pr['id']} [{pr['state']}] {pr['title']} (by {author})")


def get_commits(workspace, repo, limit=20, branch=None):
    auth = get_auth()
    print(f"{YELLOW}Listing commits for {workspace}/{repo}...{RESET}")

    endpoint = f"/repositories/{workspace}/{repo}/commits"
    if branch:
        endpoint += f"/{branch}"
    data = api_request("GET", endpoint, auth, params={"pagelen": limit})
    commits = data.get("values", [])
    print(f"{GREEN}Found {len(commits)} commits:{RESET}")
    for c in commits:
        sha = c["hash"][:12]
        msg = c.get("message", "").split("\n")[0][:80]
        author = c.get("author", {}).get("user", {}).get("display_name",
                 c.get("author", {}).get("raw", "unknown"))
        print(f"  {sha} {msg} ({author})")


def link_jira(workspace, repo, limit=50):
    auth = get_auth()
    print(f"{YELLOW}Scanning commits for Jira ticket references in {workspace}/{repo}...{RESET}")

    data = api_request("GET", f"/repositories/{workspace}/{repo}/commits", auth,
                       params={"pagelen": limit})
    commits = data.get("values", [])

    links = {}
    for c in commits:
        msg = c.get("message", "")
        tickets = JIRA_PATTERN.findall(msg)
        for ticket in tickets:
            links.setdefault(ticket, []).append(c["hash"][:12])

    if links:
        print(f"{GREEN}Found {len(links)} Jira ticket references:{RESET}")
        for ticket, shas in sorted(links.items()):
            print(f"  {ticket}: {', '.join(shas)}")
    else:
        print(f"{YELLOW}No Jira ticket references found in the last {limit} commits.{RESET}")


def list_branches(workspace, repo):
    auth = get_auth()
    print(f"{YELLOW}Listing branches for {workspace}/{repo}...{RESET}")

    data = api_request("GET", f"/repositories/{workspace}/{repo}/refs/branches", auth,
                       params={"pagelen": 50})
    branches = data.get("values", [])
    print(f"{GREEN}Found {len(branches)} branches:{RESET}")
    for b in branches:
        sha = b.get("target", {}).get("hash", "")[:12]
        print(f"  {b['name']} ({sha})")


def main():
    parser = argparse.ArgumentParser(description="Bitbucket Integration")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_repos = subparsers.add_parser("list-repos", help="List repositories")
    p_repos.add_argument("--workspace", required=True, help="Bitbucket workspace slug")
    p_repos.add_argument("--limit", type=int, default=25)

    p_prs = subparsers.add_parser("list-prs", help="List pull requests")
    p_prs.add_argument("--workspace", required=True)
    p_prs.add_argument("--repo", required=True, help="Repository slug")
    p_prs.add_argument("--state", default="OPEN", choices=["OPEN", "MERGED", "DECLINED", "SUPERSEDED"])

    p_commits = subparsers.add_parser("get-commits", help="List commits")
    p_commits.add_argument("--workspace", required=True)
    p_commits.add_argument("--repo", required=True)
    p_commits.add_argument("--limit", type=int, default=20)
    p_commits.add_argument("--branch", help="Filter by branch")

    p_jira = subparsers.add_parser("link-jira", help="Find Jira ticket references in commits")
    p_jira.add_argument("--workspace", required=True)
    p_jira.add_argument("--repo", required=True)
    p_jira.add_argument("--limit", type=int, default=50)

    p_branches = subparsers.add_parser("list-branches", help="List branches")
    p_branches.add_argument("--workspace", required=True)
    p_branches.add_argument("--repo", required=True)

    args = parser.parse_args()

    if args.command == "list-repos":
        list_repos(args.workspace, args.limit)
    elif args.command == "list-prs":
        list_prs(args.workspace, args.repo, args.state)
    elif args.command == "get-commits":
        get_commits(args.workspace, args.repo, args.limit, args.branch)
    elif args.command == "link-jira":
        link_jira(args.workspace, args.repo, args.limit)
    elif args.command == "list-branches":
        list_branches(args.workspace, args.repo)


if __name__ == "__main__":
    main()

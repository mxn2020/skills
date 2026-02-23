#!/usr/bin/env python3
"""
GitLab Merge Request Manager - Auto-assign reviewers and manage MR lifecycle.
Uses GitLab REST API via requests.
"""

import sys
import os
import json
import argparse

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def get_config():
    token = os.environ.get("GITLAB_TOKEN")
    if not token:
        print(f"{RED}Error: GITLAB_TOKEN environment variable not set.{RESET}")
        sys.exit(1)
    url = os.environ.get("GITLAB_URL", "https://gitlab.com").rstrip("/")
    return url, token


def api_request(method, endpoint, token, base_url, params=None, json_data=None):
    try:
        import requests
    except ImportError:
        print(f"{RED}Error: 'requests' library not installed. Run: pip install requests{RESET}")
        sys.exit(1)

    headers = {"PRIVATE-TOKEN": token}
    url = f"{base_url}/api/v4{endpoint}"

    resp = requests.request(method, url, headers=headers, params=params, json=json_data, timeout=30)
    if resp.status_code >= 400:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.text else None


def encode_project(project):
    try:
        from urllib.parse import quote
    except ImportError:
        from urllib import quote
    return quote(project, safe="")


def get_user_id(username, token, base_url):
    """Resolve a GitLab username to a user ID."""
    users = api_request("GET", "/users", token, base_url, params={"username": username})
    if not users:
        print(f"{RED}User '{username}' not found.{RESET}")
        return None
    return users[0]["id"]


def list_mrs(project, state="opened", limit=20):
    base_url, token = get_config()
    encoded = encode_project(project)
    print(f"{YELLOW}Listing {state} merge requests for {project}...{RESET}")

    mrs = api_request("GET", f"/projects/{encoded}/merge_requests", token, base_url,
                      params={"state": state, "per_page": limit})
    print(f"{GREEN}Found {len(mrs)} merge requests:{RESET}")
    for mr in mrs:
        author = mr.get("author", {}).get("username", "unknown")
        reviewers = ", ".join(r["username"] for r in mr.get("reviewers", []))
        reviewer_str = f" reviewers=[{reviewers}]" if reviewers else ""
        print(f"  !{mr['iid']} [{mr['state']}] {mr['title']} (by {author}){reviewer_str}")


def create_mr(project, source, target, title, description=""):
    base_url, token = get_config()
    encoded = encode_project(project)
    print(f"{YELLOW}Creating merge request in {project}...{RESET}")

    data = {
        "source_branch": source,
        "target_branch": target,
        "title": title,
    }
    if description:
        data["description"] = description

    mr = api_request("POST", f"/projects/{encoded}/merge_requests", token, base_url, json_data=data)
    print(f"{GREEN}Merge request created: !{mr['iid']} - {mr['title']}{RESET}")
    print(f"  URL: {mr.get('web_url', 'N/A')}")


def assign_reviewers(project, mr_iid, reviewers):
    base_url, token = get_config()
    encoded = encode_project(project)
    print(f"{YELLOW}Assigning reviewers to !{mr_iid} in {project}...{RESET}")

    reviewer_ids = []
    for username in reviewers.split(","):
        username = username.strip()
        uid = get_user_id(username, token, base_url)
        if uid:
            reviewer_ids.append(uid)
            print(f"  Resolved {username} -> ID {uid}")

    if not reviewer_ids:
        print(f"{RED}No valid reviewers found.{RESET}")
        sys.exit(1)

    api_request("PUT", f"/projects/{encoded}/merge_requests/{mr_iid}", token, base_url,
                json_data={"reviewer_ids": reviewer_ids})
    print(f"{GREEN}Reviewers assigned to !{mr_iid}.{RESET}")


def approve_mr(project, mr_iid):
    base_url, token = get_config()
    encoded = encode_project(project)
    print(f"{YELLOW}Approving merge request !{mr_iid} in {project}...{RESET}")

    api_request("POST", f"/projects/{encoded}/merge_requests/{mr_iid}/approve", token, base_url)
    print(f"{GREEN}Merge request !{mr_iid} approved.{RESET}")


def merge_mr(project, mr_iid, squash=False, delete_branch=False):
    base_url, token = get_config()
    encoded = encode_project(project)
    print(f"{YELLOW}Merging merge request !{mr_iid} in {project}...{RESET}")

    data = {}
    if squash:
        data["squash"] = True
    if delete_branch:
        data["should_remove_source_branch"] = True

    result = api_request("PUT", f"/projects/{encoded}/merge_requests/{mr_iid}/merge", token, base_url,
                         json_data=data)
    print(f"{GREEN}Merge request !{mr_iid} merged.{RESET}")
    if result:
        print(f"  State: {result.get('state', 'N/A')}")


def main():
    parser = argparse.ArgumentParser(description="GitLab Merge Request Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_list = subparsers.add_parser("list-mrs", help="List merge requests")
    p_list.add_argument("--project", required=True, help="GitLab project path (group/project)")
    p_list.add_argument("--state", default="opened", choices=["opened", "closed", "merged", "all"])
    p_list.add_argument("--limit", type=int, default=20)

    p_create = subparsers.add_parser("create-mr", help="Create a merge request")
    p_create.add_argument("--project", required=True)
    p_create.add_argument("--source", required=True, help="Source branch")
    p_create.add_argument("--target", default="main", help="Target branch")
    p_create.add_argument("--title", required=True)
    p_create.add_argument("--description", default="")

    p_assign = subparsers.add_parser("assign-reviewers", help="Assign reviewers to MR")
    p_assign.add_argument("--project", required=True)
    p_assign.add_argument("--mr-id", required=True, type=int, help="Merge request IID")
    p_assign.add_argument("--reviewers", required=True, help="Comma-separated usernames")

    p_approve = subparsers.add_parser("approve-mr", help="Approve a merge request")
    p_approve.add_argument("--project", required=True)
    p_approve.add_argument("--mr-id", required=True, type=int)

    p_merge = subparsers.add_parser("merge-mr", help="Merge a merge request")
    p_merge.add_argument("--project", required=True)
    p_merge.add_argument("--mr-id", required=True, type=int)
    p_merge.add_argument("--squash", action="store_true")
    p_merge.add_argument("--delete-branch", action="store_true")

    args = parser.parse_args()

    if args.command == "list-mrs":
        list_mrs(args.project, args.state, args.limit)
    elif args.command == "create-mr":
        create_mr(args.project, args.source, args.target, args.title, args.description)
    elif args.command == "assign-reviewers":
        assign_reviewers(args.project, args.mr_id, args.reviewers)
    elif args.command == "approve-mr":
        approve_mr(args.project, args.mr_id)
    elif args.command == "merge-mr":
        merge_mr(args.project, args.mr_id, args.squash, args.delete_branch)


if __name__ == "__main__":
    main()

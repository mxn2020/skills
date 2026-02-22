#!/usr/bin/env python3
"""
Neon Branch Manager - Create instant Postgres branches for every PR.
Uses Neon API via requests.
"""

import sys
import os
import json
import argparse

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://console.neon.tech/api/v2"


def get_config():
    api_key = os.environ.get("NEON_API_KEY")
    project_id = os.environ.get("NEON_PROJECT_ID")
    if not api_key:
        print(f"{RED}Error: NEON_API_KEY environment variable not set.{RESET}")
        sys.exit(1)
    if not project_id:
        print(f"{RED}Error: NEON_PROJECT_ID environment variable not set.{RESET}")
        sys.exit(1)
    return api_key, project_id


def api_request(method, endpoint, api_key, params=None, json_data=None):
    try:
        import requests
    except ImportError:
        print(f"{RED}Error: 'requests' library not installed. Run: pip install requests{RESET}")
        sys.exit(1)

    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    url = f"{BASE_URL}{endpoint}"

    resp = requests.request(method, url, headers=headers, params=params, json=json_data, timeout=30)
    if resp.status_code >= 400:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.text else None


def list_branches():
    api_key, project_id = get_config()
    print(f"{YELLOW}Listing branches for project {project_id}...{RESET}")

    data = api_request("GET", f"/projects/{project_id}/branches", api_key)
    branches = data.get("branches", [])
    print(f"{GREEN}Found {len(branches)} branches:{RESET}")
    for b in branches:
        primary = " (primary)" if b.get("primary") else ""
        print(f"  {b['name']} [ID: {b['id']}]{primary} created={b['created_at']}")


def create_branch(name, parent_id=None):
    api_key, project_id = get_config()
    print(f"{YELLOW}Creating branch '{name}'...{RESET}")

    body = {"branch": {"name": name}}
    if parent_id:
        body["branch"]["parent_id"] = parent_id

    data = api_request("POST", f"/projects/{project_id}/branches", api_key, json_data=body)
    branch = data.get("branch", {})
    print(f"{GREEN}Branch created:{RESET}")
    print(f"  Name: {branch.get('name')}")
    print(f"  ID:   {branch.get('id')}")
    print(f"  Host: {data.get('endpoints', [{}])[0].get('host', 'N/A')}")


def delete_branch(branch_id):
    api_key, project_id = get_config()
    print(f"{YELLOW}Deleting branch {branch_id}...{RESET}")

    api_request("DELETE", f"/projects/{project_id}/branches/{branch_id}", api_key)
    print(f"{GREEN}Branch {branch_id} deleted.{RESET}")


def get_branch(branch_id):
    api_key, project_id = get_config()
    print(f"{YELLOW}Getting branch {branch_id}...{RESET}")

    data = api_request("GET", f"/projects/{project_id}/branches/{branch_id}", api_key)
    b = data.get("branch", {})
    print(f"\n{GREEN}Branch: {b.get('name')}{RESET}")
    print(f"  ID:        {b.get('id')}")
    print(f"  Parent:    {b.get('parent_id', 'N/A')}")
    print(f"  Primary:   {b.get('primary', False)}")
    print(f"  Created:   {b.get('created_at')}")
    print(f"  Updated:   {b.get('updated_at')}")


def list_endpoints():
    api_key, project_id = get_config()
    print(f"{YELLOW}Listing endpoints for project {project_id}...{RESET}")

    data = api_request("GET", f"/projects/{project_id}/endpoints", api_key)
    endpoints = data.get("endpoints", [])
    print(f"{GREEN}Found {len(endpoints)} endpoints:{RESET}")
    for ep in endpoints:
        print(f"  {ep.get('host', 'N/A')} [ID: {ep['id']}] branch={ep.get('branch_id')} type={ep.get('type')}")


def main():
    parser = argparse.ArgumentParser(description="Neon Branch Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list-branches", help="List all branches")

    p_create = subparsers.add_parser("create-branch", help="Create a branch")
    p_create.add_argument("--name", required=True, help="Branch name")
    p_create.add_argument("--parent-id", help="Parent branch ID")

    p_delete = subparsers.add_parser("delete-branch", help="Delete a branch")
    p_delete.add_argument("--branch-id", required=True, help="Branch ID")

    p_get = subparsers.add_parser("get-branch", help="Get branch details")
    p_get.add_argument("--branch-id", required=True, help="Branch ID")

    subparsers.add_parser("list-endpoints", help="List endpoints")

    args = parser.parse_args()

    if args.command == "list-branches":
        list_branches()
    elif args.command == "create-branch":
        create_branch(args.name, args.parent_id)
    elif args.command == "delete-branch":
        delete_branch(args.branch_id)
    elif args.command == "get-branch":
        get_branch(args.branch_id)
    elif args.command == "list-endpoints":
        list_endpoints()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""OC-0062: WorkOS Directory Sync - Manage enterprise SSO and SCIM."""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://api.workos.com"


def get_headers():
    key = os.environ.get("WORKOS_API_KEY")
    if not key:
        print(f"{RED}Error: WORKOS_API_KEY environment variable is not set.{RESET}")
        sys.exit(1)
    return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}


def handle_response(resp, success_msg):
    if resp.ok:
        print(f"{GREEN}{success_msg}{RESET}")
        print(json.dumps(resp.json(), indent=2))
    else:
        print(f"{RED}Error {resp.status_code}: {resp.text}{RESET}")
        sys.exit(1)


def list_directories(args):
    params = {"limit": args.limit}
    if args.org_id:
        params["organization_id"] = args.org_id
    resp = requests.get(
        f"{BASE_URL}/directories", headers=get_headers(), params=params
    )
    handle_response(resp, f"Directories (limit={args.limit}):")


def list_users(args):
    params = {"directory": args.directory_id, "limit": args.limit}
    resp = requests.get(
        f"{BASE_URL}/directory_users", headers=get_headers(), params=params
    )
    handle_response(resp, f"Users in directory {args.directory_id}:")


def list_groups(args):
    params = {"directory": args.directory_id, "limit": args.limit}
    resp = requests.get(
        f"{BASE_URL}/directory_groups", headers=get_headers(), params=params
    )
    handle_response(resp, f"Groups in directory {args.directory_id}:")


def get_directory(args):
    resp = requests.get(
        f"{BASE_URL}/directories/{args.directory_id}", headers=get_headers()
    )
    handle_response(resp, f"Directory details for {args.directory_id}:")


def list_connections(args):
    params = {"limit": args.limit}
    if args.org_id:
        params["organization_id"] = args.org_id
    resp = requests.get(
        f"{BASE_URL}/connections", headers=get_headers(), params=params
    )
    handle_response(resp, f"SSO connections (limit={args.limit}):")


def list_orgs(args):
    params = {"limit": args.limit}
    resp = requests.get(
        f"{BASE_URL}/organizations", headers=get_headers(), params=params
    )
    handle_response(resp, f"Organizations (limit={args.limit}):")


def main():
    parser = argparse.ArgumentParser(description="WorkOS Directory Sync (OC-0062)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_dirs = sub.add_parser("list-directories", help="List all directories")
    p_dirs.add_argument("--limit", type=int, default=10)
    p_dirs.add_argument("--org-id", default=None)

    p_users = sub.add_parser("list-users", help="List users in a directory")
    p_users.add_argument("--directory-id", required=True)
    p_users.add_argument("--limit", type=int, default=20)

    p_groups = sub.add_parser("list-groups", help="List groups in a directory")
    p_groups.add_argument("--directory-id", required=True)
    p_groups.add_argument("--limit", type=int, default=20)

    p_get = sub.add_parser("get-directory", help="Get directory details")
    p_get.add_argument("--directory-id", required=True)

    p_conn = sub.add_parser("list-connections", help="List SSO connections")
    p_conn.add_argument("--limit", type=int, default=10)
    p_conn.add_argument("--org-id", default=None)

    p_orgs = sub.add_parser("list-orgs", help="List organizations")
    p_orgs.add_argument("--limit", type=int, default=10)

    args = parser.parse_args()
    commands = {
        "list-directories": list_directories,
        "list-users": list_users,
        "list-groups": list_groups,
        "get-directory": get_directory,
        "list-connections": list_connections,
        "list-orgs": list_orgs,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()

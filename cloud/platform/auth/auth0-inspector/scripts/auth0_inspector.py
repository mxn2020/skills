#!/usr/bin/env python3
"""OC-0060: Auth0 Log Inspector - Check failed login attempts and anomalies."""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def get_config():
    domain = os.environ.get("AUTH0_DOMAIN")
    token = os.environ.get("AUTH0_MGMT_TOKEN")
    if not domain or not token:
        print(f"{RED}Error: AUTH0_DOMAIN and AUTH0_MGMT_TOKEN must be set.{RESET}")
        sys.exit(1)
    base_url = f"https://{domain}/api/v2"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    return base_url, headers


def handle_response(resp, success_msg):
    if resp.ok:
        print(f"{GREEN}{success_msg}{RESET}")
        print(json.dumps(resp.json(), indent=2))
    else:
        print(f"{RED}Error {resp.status_code}: {resp.text}{RESET}")
        sys.exit(1)


def list_logs(args):
    base_url, headers = get_config()
    params = {"per_page": args.limit, "sort": "date:-1"}
    resp = requests.get(f"{base_url}/logs", headers=headers, params=params)
    handle_response(resp, f"Recent log events (limit={args.limit}):")


def search_logs(args):
    base_url, headers = get_config()
    params = {"q": args.query, "per_page": args.limit, "sort": "date:-1"}
    resp = requests.get(f"{base_url}/logs", headers=headers, params=params)
    handle_response(resp, f"Log search results for '{args.query}':")


def list_users(args):
    base_url, headers = get_config()
    params = {"per_page": args.limit, "search_engine": "v3"}
    resp = requests.get(f"{base_url}/users", headers=headers, params=params)
    handle_response(resp, f"Users (limit={args.limit}):")


def get_user(args):
    base_url, headers = get_config()
    resp = requests.get(f"{base_url}/users/{args.user_id}", headers=headers)
    handle_response(resp, f"User details for {args.user_id}:")


def block_user(args):
    base_url, headers = get_config()
    payload = {"blocked": True}
    resp = requests.patch(
        f"{base_url}/users/{args.user_id}", headers=headers, json=payload
    )
    handle_response(resp, f"{YELLOW}User {args.user_id} has been blocked.{RESET}")


def list_connections(args):
    base_url, headers = get_config()
    params = {"per_page": args.limit}
    resp = requests.get(f"{base_url}/connections", headers=headers, params=params)
    handle_response(resp, "Identity connections:")


def main():
    parser = argparse.ArgumentParser(description="Auth0 Log Inspector (OC-0060)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_logs = sub.add_parser("list-logs", help="List recent log events")
    p_logs.add_argument("--limit", type=int, default=25)

    p_search = sub.add_parser("search-logs", help="Search logs with Lucene query")
    p_search.add_argument("--query", required=True)
    p_search.add_argument("--limit", type=int, default=25)

    p_users = sub.add_parser("list-users", help="List all users")
    p_users.add_argument("--limit", type=int, default=20)

    p_get = sub.add_parser("get-user", help="Get user details")
    p_get.add_argument("--user-id", required=True)

    p_block = sub.add_parser("block-user", help="Block a user")
    p_block.add_argument("--user-id", required=True)

    p_conn = sub.add_parser("list-connections", help="List identity connections")
    p_conn.add_argument("--limit", type=int, default=50)

    args = parser.parse_args()
    commands = {
        "list-logs": list_logs,
        "search-logs": search_logs,
        "list-users": list_users,
        "get-user": get_user,
        "block-user": block_user,
        "list-connections": list_connections,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()

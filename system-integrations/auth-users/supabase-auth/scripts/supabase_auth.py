#!/usr/bin/env python3
"""OC-0061: Supabase Auth Helper - Send password reset emails, manage providers."""

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
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not url or not key:
        print(f"{RED}Error: SUPABASE_URL and SUPABASE_SERVICE_KEY must be set.{RESET}")
        sys.exit(1)
    base_url = f"{url.rstrip('/')}/auth/v1"
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
    }
    return base_url, headers


def handle_response(resp, success_msg):
    if resp.ok:
        print(f"{GREEN}{success_msg}{RESET}")
        data = resp.json() if resp.text else {}
        print(json.dumps(data, indent=2))
    else:
        print(f"{RED}Error {resp.status_code}: {resp.text}{RESET}")
        sys.exit(1)


def list_users(args):
    base_url, headers = get_config()
    params = {"page": args.page, "per_page": args.limit}
    resp = requests.get(f"{base_url}/admin/users", headers=headers, params=params)
    handle_response(resp, f"Users (page={args.page}, limit={args.limit}):")


def get_user(args):
    base_url, headers = get_config()
    resp = requests.get(f"{base_url}/admin/users/{args.user_id}", headers=headers)
    handle_response(resp, f"User details for {args.user_id}:")


def create_user(args):
    base_url, headers = get_config()
    payload = {
        "email": args.email,
        "password": args.password,
        "email_confirm": True,
    }
    resp = requests.post(f"{base_url}/admin/users", headers=headers, json=payload)
    handle_response(resp, f"User created with email {args.email}.")


def delete_user(args):
    base_url, headers = get_config()
    print(f"{YELLOW}Warning: This will permanently delete user {args.user_id}.{RESET}")
    resp = requests.delete(f"{base_url}/admin/users/{args.user_id}", headers=headers)
    handle_response(resp, f"User {args.user_id} has been deleted.")


def send_reset(args):
    base_url, headers = get_config()
    payload = {"email": args.email}
    resp = requests.post(f"{base_url}/recover", headers=headers, json=payload)
    if resp.ok:
        print(f"{GREEN}Password reset email sent to {args.email}.{RESET}")
    else:
        print(f"{RED}Error {resp.status_code}: {resp.text}{RESET}")
        sys.exit(1)


def list_factors(args):
    base_url, headers = get_config()
    resp = requests.get(
        f"{base_url}/admin/users/{args.user_id}/factors", headers=headers
    )
    handle_response(resp, f"MFA factors for user {args.user_id}:")


def main():
    parser = argparse.ArgumentParser(description="Supabase Auth Helper (OC-0061)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list-users", help="List all users")
    p_list.add_argument("--limit", type=int, default=20)
    p_list.add_argument("--page", type=int, default=1)

    p_get = sub.add_parser("get-user", help="Get user details")
    p_get.add_argument("--user-id", required=True)

    p_create = sub.add_parser("create-user", help="Create a new user")
    p_create.add_argument("--email", required=True)
    p_create.add_argument("--password", required=True)

    p_del = sub.add_parser("delete-user", help="Delete a user")
    p_del.add_argument("--user-id", required=True)

    p_reset = sub.add_parser("send-reset", help="Send password reset email")
    p_reset.add_argument("--email", required=True)

    p_factors = sub.add_parser("list-factors", help="List MFA factors for a user")
    p_factors.add_argument("--user-id", required=True)

    args = parser.parse_args()
    commands = {
        "list-users": list_users,
        "get-user": get_user,
        "create-user": create_user,
        "delete-user": delete_user,
        "send-reset": send_reset,
        "list-factors": list_factors,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()

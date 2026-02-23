#!/usr/bin/env python3
"""OC-0059: Clerk User Admin - Ban/unban users, manage sessions and roles."""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://api.clerk.com/v1"


def get_headers():
    key = os.environ.get("CLERK_SECRET_KEY")
    if not key:
        print(f"{RED}Error: CLERK_SECRET_KEY environment variable is not set.{RESET}")
        sys.exit(1)
    return {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}


def handle_response(resp, success_msg):
    if resp.ok:
        print(f"{GREEN}{success_msg}{RESET}")
        print(json.dumps(resp.json(), indent=2))
    else:
        print(f"{RED}Error {resp.status_code}: {resp.text}{RESET}")
        sys.exit(1)


def list_users(args):
    params = {"limit": args.limit, "offset": args.offset}
    resp = requests.get(f"{BASE_URL}/users", headers=get_headers(), params=params)
    handle_response(resp, f"Listing users (limit={args.limit}):")


def get_user(args):
    resp = requests.get(f"{BASE_URL}/users/{args.user_id}", headers=get_headers())
    handle_response(resp, f"User details for {args.user_id}:")


def ban_user(args):
    resp = requests.post(f"{BASE_URL}/users/{args.user_id}/ban", headers=get_headers())
    handle_response(resp, f"User {args.user_id} has been banned.")


def unban_user(args):
    resp = requests.post(f"{BASE_URL}/users/{args.user_id}/unban", headers=get_headers())
    handle_response(resp, f"User {args.user_id} has been unbanned.")


def delete_user(args):
    print(f"{YELLOW}Warning: This will permanently delete user {args.user_id}.{RESET}")
    resp = requests.delete(f"{BASE_URL}/users/{args.user_id}", headers=get_headers())
    handle_response(resp, f"User {args.user_id} has been deleted.")


def list_sessions(args):
    params = {"user_id": args.user_id, "status": "active"}
    resp = requests.get(f"{BASE_URL}/sessions", headers=get_headers(), params=params)
    handle_response(resp, f"Active sessions for user {args.user_id}:")


def update_role(args):
    payload = {"role": args.role}
    url = f"{BASE_URL}/organizations/{args.org_id}/memberships/{args.user_id}"
    resp = requests.patch(url, headers=get_headers(), json=payload)
    handle_response(resp, f"Role for {args.user_id} updated to '{args.role}'.")


def main():
    parser = argparse.ArgumentParser(description="Clerk User Admin (OC-0059)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list-users", help="List all users")
    p_list.add_argument("--limit", type=int, default=20)
    p_list.add_argument("--offset", type=int, default=0)

    p_get = sub.add_parser("get-user", help="Get user details")
    p_get.add_argument("--user-id", required=True)

    p_ban = sub.add_parser("ban", help="Ban a user")
    p_ban.add_argument("--user-id", required=True)

    p_unban = sub.add_parser("unban", help="Unban a user")
    p_unban.add_argument("--user-id", required=True)

    p_del = sub.add_parser("delete-user", help="Delete a user")
    p_del.add_argument("--user-id", required=True)

    p_sess = sub.add_parser("list-sessions", help="List sessions for a user")
    p_sess.add_argument("--user-id", required=True)

    p_role = sub.add_parser("update-role", help="Update user role in an org")
    p_role.add_argument("--user-id", required=True)
    p_role.add_argument("--org-id", required=True)
    p_role.add_argument("--role", required=True)

    args = parser.parse_args()
    commands = {
        "list-users": list_users,
        "get-user": get_user,
        "ban": ban_user,
        "unban": unban_user,
        "delete-user": delete_user,
        "list-sessions": list_sessions,
        "update-role": update_role,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()

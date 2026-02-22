#!/usr/bin/env python3
"""OC-0063: Firebase Auth Manager - Disable accounts, revoke tokens."""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def get_access_token():
    """Obtain an access token via gcloud or GOOGLE_ACCESS_TOKEN env var."""
    token = os.environ.get("GOOGLE_ACCESS_TOKEN")
    if token:
        return token
    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path:
        print(f"{RED}Error: Set GOOGLE_ACCESS_TOKEN or GOOGLE_APPLICATION_CREDENTIALS.{RESET}")
        sys.exit(1)
    # Use gcloud to generate an access token from the service account
    import subprocess

    result = subprocess.run(
        ["gcloud", "auth", "print-access-token"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"{RED}Error obtaining access token: {result.stderr}{RESET}")
        sys.exit(1)
    return result.stdout.strip()


def get_config():
    project_id = os.environ.get("FIREBASE_PROJECT_ID")
    if not project_id:
        print(f"{RED}Error: FIREBASE_PROJECT_ID is not set.{RESET}")
        sys.exit(1)
    token = get_access_token()
    base_url = f"https://identitytoolkit.googleapis.com/v1/projects/{project_id}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
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
    params = {"maxResults": args.limit}
    if args.page_token:
        params["nextPageToken"] = args.page_token
    resp = requests.get(f"{base_url}/accounts:batchGet", headers=headers, params=params)
    handle_response(resp, f"Users (limit={args.limit}):")


def get_user(args):
    base_url, headers = get_config()
    payload = {"localId": [args.uid]}
    resp = requests.post(f"{base_url}/accounts:lookup", headers=headers, json=payload)
    handle_response(resp, f"User details for {args.uid}:")


def create_user(args):
    base_url, headers = get_config()
    payload = {"email": args.email, "password": args.password, "emailVerified": False}
    resp = requests.post(f"{base_url}/accounts", headers=headers, json=payload)
    handle_response(resp, f"User created with email {args.email}.")


def disable_user(args):
    base_url, headers = get_config()
    payload = {"localId": args.uid, "disableUser": True}
    resp = requests.post(f"{base_url}/accounts:update", headers=headers, json=payload)
    handle_response(resp, f"{YELLOW}User {args.uid} has been disabled.{RESET}")


def delete_user(args):
    base_url, headers = get_config()
    print(f"{YELLOW}Warning: This will permanently delete user {args.uid}.{RESET}")
    payload = {"localId": args.uid}
    resp = requests.post(f"{base_url}/accounts:delete", headers=headers, json=payload)
    handle_response(resp, f"User {args.uid} has been deleted.")


def set_claims(args):
    base_url, headers = get_config()
    try:
        claims = json.loads(args.claims)
    except json.JSONDecodeError as exc:
        print(f"{RED}Error: Invalid JSON for claims: {exc}{RESET}")
        sys.exit(1)
    payload = {"localId": args.uid, "customAttributes": json.dumps(claims)}
    resp = requests.post(f"{base_url}/accounts:update", headers=headers, json=payload)
    handle_response(resp, f"Custom claims set for user {args.uid}.")


def main():
    parser = argparse.ArgumentParser(description="Firebase Auth Manager (OC-0063)")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list-users", help="List all users")
    p_list.add_argument("--limit", type=int, default=20)
    p_list.add_argument("--page-token", default=None)

    p_get = sub.add_parser("get-user", help="Get user details")
    p_get.add_argument("--uid", required=True)

    p_create = sub.add_parser("create-user", help="Create a new user")
    p_create.add_argument("--email", required=True)
    p_create.add_argument("--password", required=True)

    p_disable = sub.add_parser("disable-user", help="Disable a user account")
    p_disable.add_argument("--uid", required=True)

    p_del = sub.add_parser("delete-user", help="Delete a user")
    p_del.add_argument("--uid", required=True)

    p_claims = sub.add_parser("set-claims", help="Set custom claims on a user")
    p_claims.add_argument("--uid", required=True)
    p_claims.add_argument("--claims", required=True, help="JSON string of claims")

    args = parser.parse_args()
    commands = {
        "list-users": list_users,
        "get-user": get_user,
        "create-user": create_user,
        "disable-user": disable_user,
        "delete-user": delete_user,
        "set-claims": set_claims,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()

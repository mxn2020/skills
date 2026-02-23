#!/usr/bin/env python3
"""LogRocket Session Finder – OC-0053"""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://api.logrocket.com/v1"


def _config():
    app_id = os.environ.get("LOGROCKET_APP_ID")
    api_key = os.environ.get("LOGROCKET_API_KEY")
    if not app_id or not api_key:
        print(f"{RED}Error: LOGROCKET_APP_ID and LOGROCKET_API_KEY must be set{RESET}")
        sys.exit(1)
    return app_id, api_key


def _request(method, path, **kwargs):
    app_id, api_key = _config()
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    resp = getattr(requests, method)(f"{BASE_URL}/orgs/{app_id}{path}", headers=headers, **kwargs)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.content else {}


def list_sessions(args):
    params = {"per_page": args.limit}
    data = _request("get", "/sessions", params=params)
    for s in data.get("sessions", []):
        has_errors = s.get("hasErrors", False)
        color = RED if has_errors else GREEN
        print(f"{color}{s['id']}{RESET}  user={s.get('userEmail', 'anonymous')}  duration={s.get('duration', 0)}s  errors={has_errors}")


def search(args):
    params = {"per_page": args.limit}
    if args.email:
        params["filter[user_email]"] = args.email
    if args.user_id:
        params["filter[user_id]"] = args.user_id
    data = _request("get", "/sessions", params=params)
    for s in data.get("sessions", []):
        print(f"{GREEN}{s['id']}{RESET}  user={s.get('userEmail', 'anonymous')}  started={s.get('startedAt', 'n/a')}")


def get_session(args):
    data = _request("get", f"/sessions/{args.session_id}")
    s = data.get("session", data)
    print(f"{GREEN}Session {s.get('id', args.session_id)}{RESET}")
    print(f"  User:     {s.get('userEmail', 'anonymous')}")
    print(f"  OS:       {s.get('osName', 'n/a')} {s.get('osVersion', '')}")
    print(f"  Browser:  {s.get('browserName', 'n/a')} {s.get('browserVersion', '')}")
    print(f"  Duration: {s.get('duration', 0)}s")
    print(f"  Pages:    {s.get('pageCount', 'n/a')}")


def list_errors(args):
    data = _request("get", f"/sessions/{args.session_id}/errors")
    for err in data.get("errors", []):
        print(f"{RED}[{err.get('type', 'error')}]{RESET} {err.get('message', 'n/a')}  at={err.get('timestamp', 'n/a')}")


def get_url(args):
    app_id, _ = _config()
    url = f"https://app.logrocket.com/{app_id}/sessions/{args.session_id}"
    print(f"{GREEN}Replay URL:{RESET} {url}")


def main():
    parser = argparse.ArgumentParser(description="LogRocket Session Finder")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list-sessions", help="List recent sessions")
    p_list.add_argument("--limit", type=int, default=20)

    p_search = sub.add_parser("search", help="Search sessions")
    p_search.add_argument("--email", help="Filter by user email")
    p_search.add_argument("--user-id", help="Filter by user ID")
    p_search.add_argument("--limit", type=int, default=20)

    p_get = sub.add_parser("get-session", help="Get session details")
    p_get.add_argument("--session-id", required=True)

    p_errors = sub.add_parser("list-errors", help="List session errors")
    p_errors.add_argument("--session-id", required=True)

    p_url = sub.add_parser("get-url", help="Get replay URL")
    p_url.add_argument("--session-id", required=True)

    args = parser.parse_args()
    commands = {
        "list-sessions": list_sessions,
        "search": search,
        "get-session": get_session,
        "list-errors": list_errors,
        "get-url": get_url,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()

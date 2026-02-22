#!/usr/bin/env python3
"""Sentry Error Triage – OC-0050"""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://sentry.io/api/0"


def _headers():
    token = os.environ.get("SENTRY_AUTH_TOKEN")
    if not token:
        print(f"{RED}Error: SENTRY_AUTH_TOKEN is not set{RESET}")
        sys.exit(1)
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _org():
    org = os.environ.get("SENTRY_ORG")
    if not org:
        print(f"{RED}Error: SENTRY_ORG is not set{RESET}")
        sys.exit(1)
    return org


def _project():
    project = os.environ.get("SENTRY_PROJECT")
    if not project:
        print(f"{RED}Error: SENTRY_PROJECT is not set{RESET}")
        sys.exit(1)
    return project


def _request(method, path, **kwargs):
    resp = getattr(requests, method)(f"{BASE_URL}{path}", headers=_headers(), **kwargs)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.content else {}


def list_issues(args):
    params = {"limit": args.limit, "query": "is:unresolved"}
    data = _request("get", f"/projects/{_org()}/{_project()}/issues/", params=params)
    for issue in data:
        level = issue.get("level", "unknown")
        color = RED if level == "error" else YELLOW
        print(f"{color}[{level}]{RESET} {issue['id']}  {issue['title']}  count={issue.get('count', 0)}")


def get_issue(args):
    data = _request("get", f"/issues/{args.issue_id}/")
    print(f"{GREEN}Issue {data['id']}{RESET}: {data['title']}")
    print(f"  Level:    {data.get('level', 'n/a')}")
    print(f"  Status:   {data.get('status', 'n/a')}")
    print(f"  Events:   {data.get('count', 0)}")
    print(f"  Users:    {data.get('userCount', 0)}")
    print(f"  First:    {data.get('firstSeen', 'n/a')}")
    print(f"  Last:     {data.get('lastSeen', 'n/a')}")


def assign(args):
    payload = {"assignedTo": args.user}
    _request("put", f"/issues/{args.issue_id}/", json=payload)
    print(f"{GREEN}Assigned issue {args.issue_id} to {args.user}{RESET}")


def resolve(args):
    payload = {"status": "resolved"}
    _request("put", f"/issues/{args.issue_id}/", json=payload)
    print(f"{GREEN}Resolved issue {args.issue_id}{RESET}")


def list_events(args):
    data = _request("get", f"/issues/{args.issue_id}/events/")
    for event in data:
        print(f"{YELLOW}{event.get('dateCreated', 'n/a')}{RESET}  id={event['eventID']}  {event.get('title', '')}")


def main():
    parser = argparse.ArgumentParser(description="Sentry Error Triage")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list-issues", help="List recent unresolved issues")
    p_list.add_argument("--limit", type=int, default=25)

    p_get = sub.add_parser("get-issue", help="Get issue details")
    p_get.add_argument("--issue-id", required=True)

    p_assign = sub.add_parser("assign", help="Assign issue to a developer")
    p_assign.add_argument("--issue-id", required=True)
    p_assign.add_argument("--user", required=True, help="Email or user identifier")

    p_resolve = sub.add_parser("resolve", help="Resolve an issue")
    p_resolve.add_argument("--issue-id", required=True)

    p_events = sub.add_parser("list-events", help="List events for an issue")
    p_events.add_argument("--issue-id", required=True)

    args = parser.parse_args()
    commands = {
        "list-issues": list_issues,
        "get-issue": get_issue,
        "assign": assign,
        "resolve": resolve,
        "list-events": list_events,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()

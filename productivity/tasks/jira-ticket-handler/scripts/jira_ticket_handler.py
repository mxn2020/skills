#!/usr/bin/env python3
"""
Jira Ticket Handler — OC-0128
Manage Jira tickets, sprints, and workflow transitions via REST API v3.
"""

import os
import sys
import argparse
import requests
from requests.auth import HTTPBasicAuth

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def get_config() -> tuple[str, HTTPBasicAuth]:
    base_url = os.environ.get("JIRA_BASE_URL", "").rstrip("/")
    email    = os.environ.get("JIRA_EMAIL", "")
    token    = os.environ.get("JIRA_API_TOKEN", "")
    if not base_url:
        _die("JIRA_BASE_URL environment variable is not set.")
    if not email or not token:
        _die("JIRA_EMAIL and JIRA_API_TOKEN environment variables must be set.")
    return base_url, HTTPBasicAuth(email, token)


def _request(method: str, path: str, **kwargs) -> dict | list:
    base_url, auth = get_config()
    url = f"{base_url}/rest/api/3/{path.lstrip('/')}"
    resp = requests.request(method, url, auth=auth,
                            headers={"Content-Type": "application/json"},
                            timeout=30, **kwargs)
    if resp.status_code == 204:
        return {}
    if not resp.ok:
        _die(f"HTTP {resp.status_code}: {resp.text[:300]}")
    return resp.json()


def list_issues(project_key: str, jql: str = None):
    jql_str = jql or f"project = {project_key} ORDER BY updated DESC"
    data = _request("GET", "search", params={"jql": jql_str, "maxResults": 50,
                    "fields": "summary,status,assignee,issuetype,priority"})
    issues = data.get("issues", [])
    if not issues:
        print(f"{YELLOW}No issues found.{RESET}")
        return
    print(f"{GREEN}Found {data.get('total', len(issues))} issue(s) (showing {len(issues)}):{RESET}")
    for issue in issues:
        fields = issue["fields"]
        assignee = (fields.get("assignee") or {}).get("displayName", "Unassigned")
        status   = fields.get("status", {}).get("name", "Unknown")
        itype    = fields.get("issuetype", {}).get("name", "")
        print(f"  {CYAN}{issue['key']}{RESET}  [{itype}] {fields['summary']}")
        print(f"    Status: {status}  Assignee: {assignee}")


def create_ticket(project_key: str, summary: str, description: str = "",
                  issue_type: str = "Task"):
    body = {
        "fields": {
            "project":   {"key": project_key},
            "summary":   summary,
            "issuetype": {"name": issue_type},
        }
    }
    if description:
        body["fields"]["description"] = {
            "type": "doc", "version": 1,
            "content": [{"type": "paragraph", "content":
                         [{"type": "text", "text": description}]}]
        }
    data = _request("POST", "issue", json=body)
    print(f"{GREEN}Created: {data['key']} — {summary}{RESET}")
    base_url, _ = get_config()
    print(f"  URL: {base_url}/browse/{data['key']}")


def update_ticket(key: str, status: str = None, assignee: str = None):
    if status:
        transitions = _request("GET", f"issue/{key}/transitions")
        match = next((t for t in transitions["transitions"]
                      if t["name"].lower() == status.lower()), None)
        if not match:
            available = [t["name"] for t in transitions["transitions"]]
            _die(f"Transition '{status}' not found. Available: {available}")
        _request("POST", f"issue/{key}/transitions",
                 json={"transition": {"id": match["id"]}})
        print(f"{GREEN}Transitioned {key} to '{status}'{RESET}")
    if assignee:
        _request("PUT", f"issue/{key}/assignee",
                 json={"accountId": assignee})
        print(f"{GREEN}Assigned {key} to account {assignee}{RESET}")
    if not status and not assignee:
        _die("Provide at least --status or --assignee.")


def list_sprints(board_id: int):
    base_url, auth = get_config()
    url = f"{base_url}/rest/agile/1.0/board/{board_id}/sprint"
    resp = requests.get(url, auth=auth, timeout=30)
    if not resp.ok:
        _die(f"HTTP {resp.status_code}: {resp.text[:300]}")
    sprints = resp.json().get("values", [])
    if not sprints:
        print(f"{YELLOW}No sprints found.{RESET}")
        return
    print(f"{GREEN}Found {len(sprints)} sprint(s):{RESET}")
    for s in sprints:
        print(f"  {CYAN}ID {s['id']}{RESET}  {s.get('name', 'N/A')}  [{s.get('state', 'unknown')}]")
        if s.get("startDate"):
            print(f"    {s.get('startDate', '')} → {s.get('endDate', '')}")


def move_to_sprint(ticket_key: str, sprint_id: int):
    base_url, auth = get_config()
    url  = f"{base_url}/rest/agile/1.0/sprint/{sprint_id}/issue"
    resp = requests.post(url, auth=auth, json={"issues": [ticket_key]}, timeout=30)
    if resp.status_code not in (200, 204):
        _die(f"HTTP {resp.status_code}: {resp.text[:300]}")
    print(f"{GREEN}Moved {ticket_key} to sprint {sprint_id}{RESET}")


def main():
    parser = argparse.ArgumentParser(prog="jira_ticket_handler.py",
                                     description="Jira Ticket Handler — OC-0128")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list-issues", help="List project issues")
    p.add_argument("--project-key", required=True)
    p.add_argument("--jql", default=None)

    p = sub.add_parser("create-ticket", help="Create a new ticket")
    p.add_argument("--project-key", required=True)
    p.add_argument("--summary", required=True)
    p.add_argument("--description", default="")
    p.add_argument("--issue-type", default="Task", dest="issue_type")

    p = sub.add_parser("update-ticket", help="Update ticket status or assignee")
    p.add_argument("--key", required=True)
    p.add_argument("--status", default=None)
    p.add_argument("--assignee", default=None, help="Atlassian account ID")

    p = sub.add_parser("list-sprints", help="List sprints on a board")
    p.add_argument("--board-id", required=True, type=int)

    p = sub.add_parser("move-to-sprint", help="Move ticket to a sprint")
    p.add_argument("--ticket-key", required=True)
    p.add_argument("--sprint-id", required=True, type=int)

    args = parser.parse_args()
    dispatch = {
        "list-issues":   lambda: list_issues(args.project_key, args.jql),
        "create-ticket": lambda: create_ticket(args.project_key, args.summary,
                                               args.description, args.issue_type),
        "update-ticket": lambda: update_ticket(args.key, args.status, args.assignee),
        "list-sprints":  lambda: list_sprints(args.board_id),
        "move-to-sprint": lambda: move_to_sprint(args.ticket_key, args.sprint_id),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()

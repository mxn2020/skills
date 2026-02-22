#!/usr/bin/env python3
"""
Linear Issue Manager — OC-0127
Manage Linear issues, cycles, and assignments via GraphQL API.
"""

import os
import sys
import json
import argparse
import requests

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"

API_URL = "https://api.linear.app/graphql"


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _headers() -> dict:
    key = os.environ.get("LINEAR_API_KEY", "")
    if not key:
        _die("LINEAR_API_KEY environment variable is not set.")
    return {"Authorization": key, "Content-Type": "application/json"}


def _request(query: str, variables: dict = None) -> dict:
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    resp = requests.post(API_URL, headers=_headers(), json=payload, timeout=30)
    if resp.status_code != 200:
        _die(f"HTTP {resp.status_code}: {resp.text}")
    data = resp.json()
    if "errors" in data:
        _die(f"GraphQL error: {data['errors'][0]['message']}")
    return data["data"]


def list_issues(team_id: str, state: str = "active"):
    query = """
    query($teamId: String!, $filter: IssueFilter) {
      team(id: $teamId) {
        issues(filter: $filter, first: 50) {
          nodes { id identifier title state { name } priority assignee { name } }
        }
      }
    }"""
    variables = {"teamId": team_id}
    if state and state != "all":
        variables["filter"] = {"state": {"name": {"containsIgnoreCase": state}}}
    data = _request(query, variables)
    issues = data["team"]["issues"]["nodes"]
    if not issues:
        print(f"{YELLOW}No issues found.{RESET}")
        return
    print(f"{GREEN}Found {len(issues)} issue(s):{RESET}")
    for issue in issues:
        assignee = issue.get("assignee", {})
        assignee_name = assignee.get("name", "Unassigned") if assignee else "Unassigned"
        prio = issue.get("priority", 0)
        state_name = issue.get("state", {}).get("name", "Unknown")
        print(f"  {CYAN}{issue['identifier']}{RESET}  {issue['title']}")
        print(f"    State: {state_name}  Priority: {prio}  Assignee: {assignee_name}")


def create_issue(team_id: str, title: str, description: str = "", priority: int = 0):
    mutation = """
    mutation($input: IssueCreateInput!) {
      issueCreate(input: $input) {
        issue { id identifier title url }
      }
    }"""
    variables = {"input": {"teamId": team_id, "title": title,
                            "description": description, "priority": priority}}
    data = _request(mutation, variables)
    issue = data["issueCreate"]["issue"]
    print(f"{GREEN}Created issue: {issue['identifier']} — {issue['title']}{RESET}")
    print(f"  URL: {issue['url']}")


def update_issue(issue_id: str, state_id: str = None, priority: int = None):
    query = """
    query($id: String!) { issue(id: $id) { id identifier title } }"""
    issue_data = _request(query, {"id": issue_id})
    issue = issue_data["issue"]

    mutation = """
    mutation($id: String!, $input: IssueUpdateInput!) {
      issueUpdate(id: $id, input: $input) {
        issue { id identifier title state { name } priority }
      }
    }"""
    update_input = {}
    if state_id:
        update_input["stateId"] = state_id
    if priority is not None:
        update_input["priority"] = priority
    if not update_input:
        _die("Provide at least --state or --priority to update.")
    data = _request(mutation, {"id": issue_id, "input": update_input})
    updated = data["issueUpdate"]["issue"]
    print(f"{GREEN}Updated {updated['identifier']}: {updated['title']}{RESET}")
    print(f"  State: {updated['state']['name']}  Priority: {updated['priority']}")


def list_cycles(team_id: str):
    query = """
    query($teamId: String!) {
      team(id: $teamId) {
        cycles(first: 20) {
          nodes { id number name startsAt endsAt completedAt }
        }
      }
    }"""
    data = _request(query, {"teamId": team_id})
    cycles = data["team"]["cycles"]["nodes"]
    if not cycles:
        print(f"{YELLOW}No cycles found for team.{RESET}")
        return
    print(f"{GREEN}Found {len(cycles)} cycle(s):{RESET}")
    for cycle in cycles:
        status = "Completed" if cycle.get("completedAt") else "Active"
        name = cycle.get("name") or f"Cycle {cycle['number']}"
        print(f"  {CYAN}{cycle['id']}{RESET}  {name}  [{status}]")
        print(f"    Start: {cycle.get('startsAt', 'N/A')}  End: {cycle.get('endsAt', 'N/A')}")


def assign_issue(issue_id: str, assignee_id: str):
    mutation = """
    mutation($id: String!, $input: IssueUpdateInput!) {
      issueUpdate(id: $id, input: $input) {
        issue { id identifier title assignee { name email } }
      }
    }"""
    data = _request(mutation, {"id": issue_id, "input": {"assigneeId": assignee_id}})
    issue = data["issueUpdate"]["issue"]
    assignee = issue.get("assignee") or {}
    print(f"{GREEN}Assigned {issue['identifier']} to {assignee.get('name', assignee_id)}{RESET}")


def main():
    parser = argparse.ArgumentParser(prog="linear_issue_manager.py",
                                     description="Linear Issue Manager — OC-0127")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list-issues", help="List team issues")
    p.add_argument("--team-id", required=True)
    p.add_argument("--state", default="active")

    p = sub.add_parser("create-issue", help="Create a new issue")
    p.add_argument("--team-id", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--description", default="")
    p.add_argument("--priority", type=int, default=0, choices=range(5))

    p = sub.add_parser("update-issue", help="Update issue state or priority")
    p.add_argument("--id", required=True)
    p.add_argument("--state", dest="state_id", default=None,
                   help="State ID (use list-issues to find IDs)")
    p.add_argument("--priority", type=int, default=None)

    p = sub.add_parser("list-cycles", help="List cycles for a team")
    p.add_argument("--team-id", required=True)

    p = sub.add_parser("assign-issue", help="Assign issue to a team member")
    p.add_argument("--id", required=True)
    p.add_argument("--assignee-id", required=True)

    args = parser.parse_args()
    dispatch = {
        "list-issues":  lambda: list_issues(args.team_id, args.state),
        "create-issue": lambda: create_issue(args.team_id, args.title,
                                              args.description, args.priority),
        "update-issue": lambda: update_issue(args.id, args.state_id, args.priority),
        "list-cycles":  lambda: list_cycles(args.team_id),
        "assign-issue": lambda: assign_issue(args.id, args.assignee_id),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()

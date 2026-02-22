#!/usr/bin/env python3
"""
ClickUp Manager — OC-0132
Manage ClickUp tasks, spaces, and lists via REST API v2.
"""

import os
import sys
import argparse
import requests

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
RESET  = "\033[0m"

BASE_URL = "https://api.clickup.com/api/v2"


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _headers() -> dict:
    token = os.environ.get("CLICKUP_API_TOKEN", "")
    if not token:
        _die("CLICKUP_API_TOKEN environment variable is not set.")
    return {"Authorization": token, "Content-Type": "application/json"}


def _request(method: str, path: str, **kwargs) -> dict | list:
    resp = requests.request(method, f"{BASE_URL}/{path.lstrip('/')}",
                            headers=_headers(), timeout=30, **kwargs)
    if not resp.ok:
        _die(f"HTTP {resp.status_code}: {resp.text[:300]}")
    return resp.json()


def list_spaces():
    workspace_id = os.environ.get("CLICKUP_WORKSPACE_ID", "")
    if not workspace_id:
        _die("CLICKUP_WORKSPACE_ID environment variable is not set.")
    data = _request("GET", f"team/{workspace_id}/space", params={"archived": "false"})
    spaces = data.get("spaces", [])
    if not spaces:
        print(f"{YELLOW}No spaces found.{RESET}")
        return
    print(f"{GREEN}Found {len(spaces)} space(s):{RESET}")
    for space in spaces:
        print(f"  {CYAN}{space['id']}{RESET}  {space['name']}")


def list_lists(space_id: str):
    data = _request("GET", f"space/{space_id}/list", params={"archived": "false"})
    lists = data.get("lists", [])
    if not lists:
        print(f"{YELLOW}No lists found.{RESET}")
        return
    print(f"{GREEN}Found {len(lists)} list(s):{RESET}")
    for lst in lists:
        task_count = lst.get("task_count", "?")
        print(f"  {CYAN}{lst['id']}{RESET}  {lst['name']}  ({task_count} tasks)")


def list_tasks(list_id: str, status_filter: str = None):
    params = {"archived": "false"}
    if status_filter:
        params["statuses[]"] = status_filter
    data = _request("GET", f"list/{list_id}/task", params=params)
    tasks = data.get("tasks", [])
    if not tasks:
        print(f"{YELLOW}No tasks found.{RESET}")
        return
    print(f"{GREEN}Found {len(tasks)} task(s):{RESET}")
    for task in tasks:
        status   = task.get("status", {}).get("status", "unknown")
        priority = (task.get("priority") or {}).get("priority", "none")
        assignees = ", ".join(a.get("username", "") for a in task.get("assignees", []))
        print(f"  {CYAN}{task['id']}{RESET}  {task['name']}")
        print(f"    Status: {status}  Priority: {priority}  Assignees: {assignees or 'None'}")


def create_task(list_id: str, name: str, description: str = "", priority: int = None):
    body = {"name": name}
    if description:
        body["description"] = description
    if priority is not None:
        body["priority"] = priority
    task = _request("POST", f"list/{list_id}/task", json=body)
    print(f"{GREEN}Created task: {task['id']} — {task['name']}{RESET}")
    print(f"  URL: {task.get('url', 'N/A')}")


def update_task(task_id: str, status: str = None, priority: int = None):
    body = {}
    if status:
        body["status"] = status
    if priority is not None:
        body["priority"] = priority
    if not body:
        _die("Provide at least --status or --priority.")
    task = _request("PUT", f"task/{task_id}", json=body)
    print(f"{GREEN}Updated task: {task['id']} — {task['name']}{RESET}")


def main():
    parser = argparse.ArgumentParser(prog="clickup_manager.py",
                                     description="ClickUp Manager — OC-0132")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list-spaces", help="List workspace spaces")

    p = sub.add_parser("list-lists", help="List lists in a space")
    p.add_argument("--space-id", required=True)

    p = sub.add_parser("list-tasks", help="List tasks in a list")
    p.add_argument("--list-id", required=True)
    p.add_argument("--status-filter", default=None)

    p = sub.add_parser("create-task", help="Create a new task")
    p.add_argument("--list-id", required=True)
    p.add_argument("--name", required=True)
    p.add_argument("--description", default="")
    p.add_argument("--priority", type=int, default=None, choices=[1, 2, 3, 4])

    p = sub.add_parser("update-task", help="Update task status or priority")
    p.add_argument("--task-id", required=True)
    p.add_argument("--status", default=None)
    p.add_argument("--priority", type=int, default=None)

    args = parser.parse_args()
    dispatch = {
        "list-spaces": lambda: list_spaces(),
        "list-lists":  lambda: list_lists(args.space_id),
        "list-tasks":  lambda: list_tasks(args.list_id,
                                           getattr(args, "status_filter", None)),
        "create-task": lambda: create_task(args.list_id, args.name,
                                           args.description, args.priority),
        "update-task": lambda: update_task(args.task_id, args.status, args.priority),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()

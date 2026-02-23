#!/usr/bin/env python3
"""
Todoist Sync — OC-0129
Manage Todoist tasks and projects via REST API v2.
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

BASE_URL = "https://api.todoist.com/rest/v2"


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _headers() -> dict:
    token = os.environ.get("TODOIST_API_TOKEN", "")
    if not token:
        _die("TODOIST_API_TOKEN environment variable is not set.")
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _request(method: str, path: str, **kwargs) -> dict | list:
    resp = requests.request(method, f"{BASE_URL}/{path.lstrip('/')}",
                            headers=_headers(), timeout=30, **kwargs)
    if resp.status_code == 204:
        return {}
    if not resp.ok:
        _die(f"HTTP {resp.status_code}: {resp.text[:300]}")
    return resp.json()


def list_tasks(project_id: str = None, filter_str: str = None):
    params = {}
    if project_id:
        params["project_id"] = project_id
    if filter_str and filter_str != "all":
        params["filter"] = filter_str
    tasks = _request("GET", "tasks", params=params)
    if not tasks:
        print(f"{YELLOW}No tasks found.{RESET}")
        return
    print(f"{GREEN}Found {len(tasks)} task(s):{RESET}")
    for task in tasks:
        due = task.get("due", {})
        due_str = due.get("string", "No due date") if due else "No due date"
        prio = task.get("priority", 1)
        print(f"  {CYAN}{task['id']}{RESET}  [P{prio}] {task['content']}")
        print(f"    Due: {due_str}  Project: {task.get('project_id', 'inbox')}")


def add_task(content: str, project_id: str = None, due_string: str = None,
             priority: int = 1):
    body = {"content": content, "priority": priority}
    if project_id:
        body["project_id"] = project_id
    if due_string:
        body["due_string"] = due_string
    task = _request("POST", "tasks", json=body)
    print(f"{GREEN}Added task: {task['id']} — {task['content']}{RESET}")
    if task.get("due"):
        print(f"  Due: {task['due'].get('string', 'N/A')}")


def complete_task(task_id: str):
    _request("POST", f"tasks/{task_id}/close")
    print(f"{GREEN}Task {task_id} marked as complete.{RESET}")


def list_projects():
    projects = _request("GET", "projects")
    if not projects:
        print(f"{YELLOW}No projects found.{RESET}")
        return
    print(f"{GREEN}Found {len(projects)} project(s):{RESET}")
    for proj in projects:
        inbox = " [Inbox]" if proj.get("is_inbox_project") else ""
        fav   = " [Fav]"  if proj.get("is_favorite")      else ""
        print(f"  {CYAN}{proj['id']}{RESET}  {proj['name']}{inbox}{fav}")


def move_task(task_id: str, project_id: str):
    _request("POST", f"tasks/{task_id}", json={"project_id": project_id})
    print(f"{GREEN}Moved task {task_id} to project {project_id}{RESET}")


def main():
    parser = argparse.ArgumentParser(prog="todoist_sync.py",
                                     description="Todoist Sync — OC-0129")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list-tasks", help="List tasks")
    p.add_argument("--project-id", default=None)
    p.add_argument("--filter", default="all", dest="filter_str")

    p = sub.add_parser("add-task", help="Add a new task")
    p.add_argument("--content", required=True)
    p.add_argument("--project-id", default=None)
    p.add_argument("--due-string", default=None)
    p.add_argument("--priority", type=int, default=1, choices=[1, 2, 3, 4])

    p = sub.add_parser("complete-task", help="Mark task as complete")
    p.add_argument("--id", required=True)

    sub.add_parser("list-projects", help="List all projects")

    p = sub.add_parser("move-task", help="Move task to another project")
    p.add_argument("--id", required=True)
    p.add_argument("--project-id", required=True)

    args = parser.parse_args()
    dispatch = {
        "list-tasks":     lambda: list_tasks(
                              getattr(args, "project_id", None),
                              getattr(args, "filter_str", None)),
        "add-task":       lambda: add_task(args.content, args.project_id,
                                           args.due_string, args.priority),
        "complete-task":  lambda: complete_task(args.id),
        "list-projects":  lambda: list_projects(),
        "move-task":      lambda: move_task(args.id, args.project_id),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()

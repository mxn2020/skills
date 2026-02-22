#!/usr/bin/env python3
"""
Google Tasks — OC-0131
Manage Google Tasks lists and tasks via REST API.
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

BASE_URL = "https://tasks.googleapis.com/tasks/v1"


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _headers() -> dict:
    token = os.environ.get("GOOGLE_TASKS_TOKEN", "")
    if not token:
        _die("GOOGLE_TASKS_TOKEN environment variable is not set.")
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _request(method: str, path: str, **kwargs) -> dict | list:
    resp = requests.request(method, f"{BASE_URL}/{path.lstrip('/')}",
                            headers=_headers(), timeout=30, **kwargs)
    if resp.status_code == 204:
        return {}
    if not resp.ok:
        _die(f"HTTP {resp.status_code}: {resp.text[:300]}")
    return resp.json()


def list_lists():
    data = _request("GET", "users/@me/lists")
    lists = data.get("items", [])
    if not lists:
        print(f"{YELLOW}No task lists found.{RESET}")
        return
    print(f"{GREEN}Found {len(lists)} task list(s):{RESET}")
    for lst in lists:
        print(f"  {CYAN}{lst['id']}{RESET}  {lst['title']}")


def list_tasks(list_id: str, show_completed: bool = False):
    params = {"showCompleted": "true" if show_completed else "false",
              "showHidden": "true" if show_completed else "false",
              "maxResults": 100}
    data = _request("GET", f"lists/{list_id}/tasks", params=params)
    tasks = data.get("items", [])
    if not tasks:
        print(f"{YELLOW}No tasks found.{RESET}")
        return
    print(f"{GREEN}Found {len(tasks)} task(s):{RESET}")
    for task in tasks:
        status = task.get("status", "needsAction")
        done   = "[x]" if status == "completed" else "[ ]"
        due    = task.get("due", "No due date")
        notes  = task.get("notes", "")
        print(f"  {done} {CYAN}{task['id']}{RESET}  {task['title']}")
        if due != "No due date":
            print(f"      Due: {due[:10]}")
        if notes:
            print(f"      {notes[:80]}")


def add_task(list_id: str, title: str, notes: str = None, due: str = None):
    body = {"title": title, "status": "needsAction"}
    if notes:
        body["notes"] = notes
    if due:
        body["due"] = due
    task = _request("POST", f"lists/{list_id}/tasks", json=body)
    print(f"{GREEN}Added task: {task['id']} — {task['title']}{RESET}")


def complete_task(list_id: str, task_id: str):
    task = _request("GET", f"lists/{list_id}/tasks/{task_id}")
    task["status"] = "completed"
    updated = _request("PUT", f"lists/{list_id}/tasks/{task_id}", json=task)
    print(f"{GREEN}Completed: {updated.get('title', task_id)}{RESET}")


def delete_task(list_id: str, task_id: str):
    _request("DELETE", f"lists/{list_id}/tasks/{task_id}")
    print(f"{GREEN}Deleted task {task_id}{RESET}")


def main():
    parser = argparse.ArgumentParser(prog="google_tasks.py",
                                     description="Google Tasks — OC-0131")
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("list-lists", help="List all task lists")

    p = sub.add_parser("list-tasks", help="List tasks in a list")
    p.add_argument("--list-id", default="@default")
    p.add_argument("--show-completed", action="store_true")

    p = sub.add_parser("add-task", help="Add a new task")
    p.add_argument("--list-id", default="@default")
    p.add_argument("--title", required=True)
    p.add_argument("--notes", default=None)
    p.add_argument("--due", default=None, help="RFC 3339 datetime")

    p = sub.add_parser("complete-task", help="Mark task as completed")
    p.add_argument("--list-id", default="@default")
    p.add_argument("--task-id", required=True)

    p = sub.add_parser("delete-task", help="Delete a task")
    p.add_argument("--list-id", default="@default")
    p.add_argument("--task-id", required=True)

    args = parser.parse_args()
    dispatch = {
        "list-lists":    lambda: list_lists(),
        "list-tasks":    lambda: list_tasks(args.list_id, args.show_completed),
        "add-task":      lambda: add_task(args.list_id, args.title,
                                          args.notes, args.due),
        "complete-task": lambda: complete_task(args.list_id, args.task_id),
        "delete-task":   lambda: delete_task(args.list_id, args.task_id),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()

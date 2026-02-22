#!/usr/bin/env python3
"""
Notion Task Manager — OC-0130
Manage tasks in a Notion database via REST API.
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

BASE_URL = "https://api.notion.com/v1"


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _headers() -> dict:
    key = os.environ.get("NOTION_API_KEY", "")
    if not key:
        _die("NOTION_API_KEY environment variable is not set.")
    return {"Authorization": f"Bearer {key}", "Notion-Version": "2022-06-28",
            "Content-Type": "application/json"}


def _db_id() -> str:
    db = os.environ.get("NOTION_DATABASE_ID", "")
    if not db:
        _die("NOTION_DATABASE_ID environment variable is not set.")
    return db


def _request(method: str, path: str, **kwargs) -> dict:
    resp = requests.request(method, f"{BASE_URL}/{path.lstrip('/')}",
                            headers=_headers(), timeout=30, **kwargs)
    if not resp.ok:
        _die(f"HTTP {resp.status_code}: {resp.text[:300]}")
    return resp.json()


def _title_from_page(page: dict) -> str:
    for prop in page.get("properties", {}).values():
        if prop.get("type") == "title":
            items = prop.get("title", [])
            return items[0]["plain_text"] if items else "(untitled)"
    return "(untitled)"


def _status_from_page(page: dict) -> str:
    for prop in page.get("properties", {}).values():
        if prop.get("type") in ("select", "status"):
            val = prop.get(prop["type"]) or {}
            return val.get("name", "")
    return ""


def list_tasks(status_filter: str = None):
    body = {"page_size": 50}
    if status_filter:
        body["filter"] = {
            "or": [
                {"property": "Status", "status":  {"equals": status_filter}},
                {"property": "Status", "select":  {"equals": status_filter}},
            ]
        }
    data = _request("POST", f"databases/{_db_id()}/query", json=body)
    pages = data.get("results", [])
    if not pages:
        print(f"{YELLOW}No tasks found.{RESET}")
        return
    print(f"{GREEN}Found {len(pages)} task(s):{RESET}")
    for page in pages:
        title  = _title_from_page(page)
        status = _status_from_page(page)
        print(f"  {CYAN}{page['id']}{RESET}  {title}")
        if status:
            print(f"    Status: {status}")


def create_task(title: str, status: str = "Todo", due_date: str = None):
    properties = {
        "Name":   {"title": [{"text": {"content": title}}]},
        "Status": {"status": {"name": status}},
    }
    if due_date:
        properties["Due Date"] = {"date": {"start": due_date}}
    data = _request("POST", "pages", json={"parent": {"database_id": _db_id()},
                                           "properties": properties})
    print(f"{GREEN}Created task: {data['id']}{RESET}")
    print(f"  Title: {title}  Status: {status}")


def update_task(page_id: str, status: str = None, title: str = None):
    properties = {}
    if status:
        properties["Status"] = {"status": {"name": status}}
    if title:
        properties["Name"] = {"title": [{"text": {"content": title}}]}
    if not properties:
        _die("Provide at least --status or --title.")
    _request("PATCH", f"pages/{page_id}", json={"properties": properties})
    print(f"{GREEN}Updated task {page_id}{RESET}")


def filter_tasks(prop: str, value: str):
    body = {"page_size": 50, "filter": {
        "or": [
            {"property": prop, "select":        {"equals": value}},
            {"property": prop, "rich_text":     {"contains": value}},
            {"property": prop, "status":        {"equals": value}},
        ]
    }}
    data = _request("POST", f"databases/{_db_id()}/query", json=body)
    pages = data.get("results", [])
    if not pages:
        print(f"{YELLOW}No tasks matched '{prop}' = '{value}'.{RESET}")
        return
    print(f"{GREEN}Found {len(pages)} matching task(s):{RESET}")
    for page in pages:
        print(f"  {CYAN}{page['id']}{RESET}  {_title_from_page(page)}")


def archive_task(page_id: str):
    _request("PATCH", f"pages/{page_id}", json={"archived": True})
    print(f"{GREEN}Archived task {page_id}{RESET}")


def main():
    parser = argparse.ArgumentParser(prog="notion_task_manager.py",
                                     description="Notion Task Manager — OC-0130")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list-tasks", help="List tasks")
    p.add_argument("--status-filter", default=None)

    p = sub.add_parser("create-task", help="Create a new task")
    p.add_argument("--title", required=True)
    p.add_argument("--status", default="Todo")
    p.add_argument("--due-date", default=None)

    p = sub.add_parser("update-task", help="Update a task")
    p.add_argument("--page-id", required=True)
    p.add_argument("--status", default=None)
    p.add_argument("--title", default=None)

    p = sub.add_parser("filter-tasks", help="Filter tasks by property")
    p.add_argument("--property", required=True)
    p.add_argument("--value", required=True)

    p = sub.add_parser("archive-task", help="Archive a task")
    p.add_argument("--page-id", required=True)

    args = parser.parse_args()
    dispatch = {
        "list-tasks":   lambda: list_tasks(getattr(args, "status_filter", None)),
        "create-task":  lambda: create_task(args.title, args.status, args.due_date),
        "update-task":  lambda: update_task(args.page_id, args.status, args.title),
        "filter-tasks": lambda: filter_tasks(args.property, args.value),
        "archive-task": lambda: archive_task(args.page_id),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()

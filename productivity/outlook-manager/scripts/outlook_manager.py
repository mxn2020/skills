#!/usr/bin/env python3
"""
Outlook Mail Manager — OC-0138
Manage emails and calendar within Microsoft 365 via Graph API.
"""

import os
import sys
import argparse
import requests

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

BASE_URL = "https://graph.microsoft.com/v1.0/me"


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _headers() -> dict:
    token = os.environ.get("OUTLOOK_TOKEN", "")
    if not token:
        _die("OUTLOOK_TOKEN is not set.")
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _request(method: str, path: str, **kwargs) -> dict:
    resp = requests.request(
        method, f"{BASE_URL}/{path.lstrip('/')}",
        headers=_headers(), timeout=30, **kwargs
    )
    if resp.status_code == 204:
        return {}
    if not resp.ok:
        _die(f"Graph API {resp.status_code}: {resp.text[:300]}")
    return resp.json()


def list_unread(top: int = 20):
    data = _request("GET", "mailFolders/inbox/messages", params={
        "$filter": "isRead eq false",
        "$top": top,
        "$select": "id,subject,from,receivedDateTime,bodyPreview",
        "$orderby": "receivedDateTime desc",
    })
    messages = data.get("value", [])
    if not messages:
        print(f"{GREEN}No unread emails.{RESET}")
        return
    print(f"{GREEN}Found {len(messages)} unread email(s):{RESET}\n")
    for msg in messages:
        mid  = msg.get("id", "")
        subj = msg.get("subject", "(no subject)")
        frm  = (msg.get("from") or {}).get("emailAddress", {}).get("address", "")
        date = msg.get("receivedDateTime", "")[:16]
        prev = msg.get("bodyPreview", "")[:80]
        print(f"  {CYAN}{mid[:24]}...{RESET}")
        print(f"    {BOLD}From:{RESET} {frm}")
        print(f"    {BOLD}Subject:{RESET} {subj}")
        print(f"    {BOLD}Date:{RESET} {date}  |  {prev}")
        print()


def send_email(to: str, subject: str, body: str, cc: str = ""):
    message = {
        "subject": subject,
        "body": {"contentType": "Text", "content": body},
        "toRecipients": [{"emailAddress": {"address": e.strip()}} for e in to.split(",")],
    }
    if cc:
        message["ccRecipients"] = [
            {"emailAddress": {"address": e.strip()}} for e in cc.split(",")
        ]
    _request("POST", "sendMail", json={"message": message, "saveToSentItems": True})
    print(f"{GREEN}Email sent to: {to}{RESET}")


def reply(message_id: str, body: str):
    _request("POST", f"messages/{message_id}/reply",
             json={"message": {}, "comment": body})
    print(f"{GREEN}Reply sent for message {message_id[:24]}...{RESET}")


def move_to_folder(message_id: str, folder_name: str):
    # Get folder ID by name
    folders_data = _request("GET", "mailFolders",
                             params={"$filter": f"displayName eq '{folder_name}'"})
    folders = folders_data.get("value", [])
    if not folders:
        _die(f"Folder '{folder_name}' not found. Use list-folders to see available folders.")
    folder_id = folders[0]["id"]
    _request("POST", f"messages/{message_id}/move",
             json={"destinationId": folder_id})
    print(f"{GREEN}Message moved to '{folder_name}'.{RESET}")


def list_folders():
    data = _request("GET", "mailFolders",
                    params={"$select": "id,displayName,unreadItemCount,totalItemCount"})
    folders = data.get("value", [])
    if not folders:
        print(f"{YELLOW}No folders found.{RESET}")
        return
    print(f"{GREEN}Mail Folders:{RESET}\n")
    for folder in folders:
        name    = folder.get("displayName", "")
        unread  = folder.get("unreadItemCount", 0)
        total   = folder.get("totalItemCount", 0)
        color   = YELLOW if unread > 0 else CYAN
        print(f"  {color}{name}{RESET}  ({unread} unread / {total} total)")
    print()


def search(query: str, top: int = 10):
    data = _request("GET", "messages", params={
        "$search": f'"{query}"',
        "$top": top,
        "$select": "id,subject,from,receivedDateTime,bodyPreview",
    })
    messages = data.get("value", [])
    if not messages:
        print(f"{YELLOW}No messages found for '{query}'.{RESET}")
        return
    print(f"{GREEN}Found {len(messages)} message(s) matching '{query}':{RESET}\n")
    for msg in messages:
        mid  = msg.get("id", "")
        subj = msg.get("subject", "(no subject)")
        frm  = (msg.get("from") or {}).get("emailAddress", {}).get("address", "")
        date = msg.get("receivedDateTime", "")[:16]
        prev = msg.get("bodyPreview", "")[:80]
        print(f"  {CYAN}{mid[:24]}...{RESET}")
        print(f"    {BOLD}From:{RESET} {frm}  |  {date}")
        print(f"    {BOLD}Subject:{RESET} {subj}")
        print(f"    {prev}")
        print()


def main():
    parser = argparse.ArgumentParser(
        prog="outlook_manager.py",
        description="Outlook Mail Manager — OC-0138"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list-unread", help="List unread emails")
    p.add_argument("--top", type=int, default=20)

    p = sub.add_parser("send-email", help="Send a new email")
    p.add_argument("--to", required=True, help="Recipient(s), comma-separated")
    p.add_argument("--subject", required=True)
    p.add_argument("--body", required=True)
    p.add_argument("--cc", default="", help="CC recipients, comma-separated")

    p = sub.add_parser("reply", help="Reply to a message")
    p.add_argument("--message-id", required=True)
    p.add_argument("--body", required=True, help="Reply body text")

    p = sub.add_parser("move-to-folder", help="Move message to folder")
    p.add_argument("--message-id", required=True)
    p.add_argument("--folder", required=True, help="Destination folder name")

    sub.add_parser("list-folders", help="List all mail folders")

    p = sub.add_parser("search", help="Search emails by keyword")
    p.add_argument("--query", required=True)
    p.add_argument("--top", type=int, default=10)

    args = parser.parse_args()
    dispatch = {
        "list-unread":    lambda: list_unread(args.top),
        "send-email":     lambda: send_email(args.to, args.subject, args.body,
                                              getattr(args, "cc", "")),
        "reply":          lambda: reply(args.message_id, args.body),
        "move-to-folder": lambda: move_to_folder(args.message_id, args.folder),
        "list-folders":   lambda: list_folders(),
        "search":         lambda: search(args.query, args.top),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()

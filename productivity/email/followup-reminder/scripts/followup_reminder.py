#!/usr/bin/env python3
"""
Follow-up Reminder — OC-0140
Track sent emails and flag those awaiting a response.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone, timedelta
import requests

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

BASE_URL   = "https://gmail.googleapis.com/gmail/v1/users/me"
TRACKER_FILE = os.path.expanduser("~/.followup_tracker.json")


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _headers() -> dict:
    token = os.environ.get("GMAIL_TOKEN", "")
    if not token:
        _die("GMAIL_TOKEN is not set.")
    return {"Authorization": f"Bearer {token}"}


def _request(method: str, path: str, **kwargs) -> dict:
    resp = requests.request(
        method, f"{BASE_URL}/{path.lstrip('/')}",
        headers=_headers(), timeout=30, **kwargs
    )
    if not resp.ok:
        _die(f"Gmail API {resp.status_code}: {resp.text[:300]}")
    return resp.json()


def _load_tracker() -> dict:
    if os.path.exists(TRACKER_FILE):
        try:
            with open(TRACKER_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {"pending": [], "resolved": []}


def _save_tracker(data: dict):
    with open(TRACKER_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _get_header(headers: list, name: str) -> str:
    for h in headers:
        if h.get("name", "").lower() == name.lower():
            return h.get("value", "")
    return ""


def scan(days: int = 3, max_results: int = 50):
    cutoff = datetime.now(timezone.utc) - timedelta(days=days)
    cutoff_epoch = int(cutoff.timestamp())

    print(f"{YELLOW}Scanning sent emails older than {days} day(s) for no-reply threads...{RESET}")

    data = _request("GET", "messages", params={
        "q": f"in:sent before:{int(datetime.now(timezone.utc).timestamp())} after:{cutoff_epoch - 86400*30}",
        "maxResults": max_results,
        "labelIds": "SENT",
    })
    messages = data.get("messages", [])
    if not messages:
        print(f"{GREEN}No sent messages found to check.{RESET}")
        return

    pending = []
    for msg in messages:
        detail = _request("GET", f"messages/{msg['id']}", params={
            "format": "metadata",
            "metadataHeaders": "Subject,To,Date",
        })
        headers = detail.get("payload", {}).get("headers", [])
        subject   = _get_header(headers, "Subject")
        to_addr   = _get_header(headers, "To")
        date_str  = _get_header(headers, "Date")
        thread_id = detail.get("threadId", "")

        # Check if date is older than cutoff
        try:
            internal_date = int(detail.get("internalDate", 0)) / 1000
            sent_dt = datetime.fromtimestamp(internal_date, tz=timezone.utc)
            if sent_dt > cutoff:
                continue
        except (ValueError, OSError):
            continue

        # Check if anyone replied in this thread
        thread_data = _request("GET", f"threads/{thread_id}", params={"format": "minimal"})
        thread_messages = thread_data.get("messages", [])
        if len(thread_messages) == 1:
            # Only our sent message, no reply yet
            pending.append({
                "thread_id": thread_id,
                "subject": subject,
                "to": to_addr,
                "sent_date": sent_dt.strftime("%Y-%m-%d"),
                "days_ago": (datetime.now(timezone.utc) - sent_dt).days,
            })

    if not pending:
        print(f"{GREEN}All sent emails have received replies!{RESET}")
        return

    print(f"\n{RED}Found {len(pending)} email(s) awaiting reply:{RESET}\n")
    for item in pending:
        age_color = RED if item["days_ago"] > 7 else YELLOW
        print(f"  {CYAN}{item['thread_id'][:16]}...{RESET}  {BOLD}{item['subject'][:50]}{RESET}")
        print(f"    To: {item['to'][:60]}  |  Sent: {item['sent_date']}  "
              f"({age_color}{item['days_ago']} days ago{RESET})")
        print()

    # Save to tracker
    tracker = _load_tracker()
    existing_ids = {p["thread_id"] for p in tracker["pending"]}
    resolved_ids = set(tracker["resolved"])
    added = 0
    for item in pending:
        if item["thread_id"] not in existing_ids and item["thread_id"] not in resolved_ids:
            tracker["pending"].append(item)
            added += 1
    _save_tracker(tracker)
    if added:
        print(f"{YELLOW}Added {added} new item(s) to local tracker ({TRACKER_FILE}).{RESET}")


def list_pending():
    tracker = _load_tracker()
    pending = tracker.get("pending", [])
    resolved_ids = set(tracker.get("resolved", []))
    active = [p for p in pending if p["thread_id"] not in resolved_ids]

    if not active:
        print(f"{GREEN}No pending follow-ups.{RESET}")
        return

    print(f"\n{BOLD}Pending Follow-ups ({len(active)}):{RESET}\n")
    for item in sorted(active, key=lambda x: x.get("days_ago", 0), reverse=True):
        age_color = RED if item.get("days_ago", 0) > 7 else YELLOW
        print(f"  {CYAN}{item.get('thread_id', '')[:16]}...{RESET}  "
              f"{BOLD}{item.get('subject', '')[:50]}{RESET}")
        print(f"    To: {item.get('to', '')[:60]}  |  Sent: {item.get('sent_date', '')}  "
              f"({age_color}{item.get('days_ago', '?')} days ago{RESET})")
        print()


def mark_resolved(thread_id: str):
    tracker = _load_tracker()
    if thread_id not in tracker.get("resolved", []):
        tracker.setdefault("resolved", []).append(thread_id)
        _save_tracker(tracker)
        print(f"{GREEN}Thread {thread_id[:16]}... marked as resolved.{RESET}")
    else:
        print(f"{YELLOW}Thread already marked as resolved.{RESET}")


def add_manual(subject: str, recipient: str, days: int):
    tracker = _load_tracker()
    entry = {
        "thread_id": f"manual_{int(datetime.now(timezone.utc).timestamp())}",
        "subject": subject,
        "to": recipient,
        "sent_date": (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d"),
        "days_ago": days,
        "manual": True,
    }
    tracker.setdefault("pending", []).append(entry)
    _save_tracker(tracker)
    print(f"{GREEN}Follow-up reminder added: '{subject}' → {recipient} (due in {days} days){RESET}")


def main():
    parser = argparse.ArgumentParser(
        prog="followup_reminder.py",
        description="Follow-up Reminder — OC-0140"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("scan", help="Scan sent emails for unanswered threads")
    p.add_argument("--days", type=int, default=3, help="Days without reply (default: 3)")
    p.add_argument("--max-results", type=int, default=50)

    sub.add_parser("list-pending", help="List pending follow-ups")

    p = sub.add_parser("mark-resolved", help="Mark a thread as resolved")
    p.add_argument("--thread-id", required=True)

    p = sub.add_parser("add-manual", help="Add a manual follow-up reminder")
    p.add_argument("--subject", required=True)
    p.add_argument("--recipient", required=True)
    p.add_argument("--days", type=int, default=3, help="Days since sent (default: 3)")

    args = parser.parse_args()
    dispatch = {
        "scan":          lambda: scan(args.days, args.max_results),
        "list-pending":  lambda: list_pending(),
        "mark-resolved": lambda: mark_resolved(args.thread_id),
        "add-manual":    lambda: add_manual(args.subject, args.recipient, args.days),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()

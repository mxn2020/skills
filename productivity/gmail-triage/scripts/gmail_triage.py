#!/usr/bin/env python3
"""
Gmail Inbox Triage — OC-0137
Summarize, label, and draft replies to unread emails via Gmail API.
"""

import os
import sys
import base64
import argparse
import requests

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

BASE_URL = "https://gmail.googleapis.com/gmail/v1/users/me"
OPENAI_URL = "https://api.openai.com/v1/chat/completions"


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _headers() -> dict:
    token = os.environ.get("GMAIL_TOKEN", "")
    if not token:
        _die("GMAIL_TOKEN is not set.")
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _request(method: str, path: str, **kwargs) -> dict:
    resp = requests.request(
        method, f"{BASE_URL}/{path.lstrip('/')}",
        headers=_headers(), timeout=30, **kwargs
    )
    if not resp.ok:
        _die(f"Gmail API {resp.status_code}: {resp.text[:300]}")
    return resp.json()


def _decode_body(payload: dict) -> str:
    """Extract plain text body from a Gmail message payload."""
    mime = payload.get("mimeType", "")
    if mime == "text/plain":
        data = (payload.get("body") or {}).get("data", "")
        if data:
            return base64.urlsafe_b64decode(data + "==").decode("utf-8", errors="replace")
    for part in payload.get("parts", []):
        result = _decode_body(part)
        if result:
            return result
    return ""


def _get_header(headers: list, name: str) -> str:
    for h in headers:
        if h.get("name", "").lower() == name.lower():
            return h.get("value", "")
    return ""


def _ai_complete(prompt: str) -> str:
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        return "(Set OPENAI_API_KEY for AI-generated content)"
    resp = requests.post(
        OPENAI_URL,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 400,
        },
        timeout=60,
    )
    if not resp.ok:
        return f"(AI unavailable: {resp.status_code})"
    return resp.json()["choices"][0]["message"]["content"].strip()


def list_unread(max_results: int = 20):
    data = _request("GET", "messages", params={
        "q": "is:unread in:inbox",
        "maxResults": max_results,
    })
    messages = data.get("messages", [])
    if not messages:
        print(f"{GREEN}Inbox is clear — no unread messages.{RESET}")
        return
    print(f"{GREEN}Found {len(messages)} unread message(s):{RESET}\n")
    for msg in messages:
        mid = msg["id"]
        detail = _request("GET", f"messages/{mid}", params={"format": "metadata",
            "metadataHeaders": "Subject,From,Date"})
        headers = detail.get("payload", {}).get("headers", [])
        subject = _get_header(headers, "Subject") or "(no subject)"
        sender  = _get_header(headers, "From") or "unknown"
        date    = _get_header(headers, "Date") or ""
        snippet = detail.get("snippet", "")[:80]
        print(f"  {CYAN}{mid}{RESET}")
        print(f"    {BOLD}From:{RESET} {sender[:60]}")
        print(f"    {BOLD}Subject:{RESET} {subject}")
        print(f"    {BOLD}Date:{RESET} {date[:30]}")
        print(f"    {snippet}...")
        print()


def summarize(message_id: str):
    msg = _request("GET", f"messages/{message_id}", params={"format": "full"})
    headers = msg.get("payload", {}).get("headers", [])
    subject = _get_header(headers, "Subject")
    sender  = _get_header(headers, "From")
    date    = _get_header(headers, "Date")
    body    = _decode_body(msg.get("payload", {}))[:2000]

    print(f"\n{BOLD}Email:{RESET} {subject}")
    print(f"{BOLD}From:{RESET}  {sender}")
    print(f"{BOLD}Date:{RESET}  {date}\n")

    if body:
        prompt = (
            f"Email Subject: {subject}\nFrom: {sender}\n\n"
            f"Body:\n{body}\n\n"
            "Provide a 3-bullet summary of this email and any required action items."
        )
        print(f"{BOLD}AI Summary:{RESET}")
        summary = _ai_complete(prompt)
        for line in summary.split("\n"):
            print(f"  {line}")
    else:
        print(f"{YELLOW}No plain text body found.{RESET}")
    print()


def label(message_id: str, label_name: str):
    # First, find or create the label
    labels_data = _request("GET", "labels")
    label_id = None
    for lbl in labels_data.get("labels", []):
        if lbl.get("name", "").lower() == label_name.lower():
            label_id = lbl["id"]
            break

    if not label_id:
        print(f"{YELLOW}Label '{label_name}' not found. Creating...{RESET}")
        new_label = _request("POST", "labels", json={"name": label_name})
        label_id = new_label["id"]
        print(f"{GREEN}Created label: {label_name} (ID: {label_id}){RESET}")

    _request("POST", f"messages/{message_id}/modify",
             json={"addLabelIds": [label_id]})
    print(f"{GREEN}Label '{label_name}' added to message {message_id}.{RESET}")


def archive(message_id: str):
    _request("POST", f"messages/{message_id}/modify",
             json={"removeLabelIds": ["INBOX"]})
    print(f"{GREEN}Message {message_id} archived.{RESET}")


def draft_reply(message_id: str, tone: str = "professional"):
    msg = _request("GET", f"messages/{message_id}", params={"format": "full"})
    headers = msg.get("payload", {}).get("headers", [])
    subject = _get_header(headers, "Subject")
    sender  = _get_header(headers, "From")
    body    = _decode_body(msg.get("payload", {}))[:1500]
    thread_id = msg.get("threadId", message_id)

    prompt = (
        f"Write a {tone} email reply to the following message.\n"
        f"From: {sender}\nSubject: {subject}\n\nOriginal:\n{body}\n\n"
        "Draft a concise and helpful reply. Start with a greeting, address the key points, "
        "and close professionally."
    )
    print(f"{YELLOW}Generating {tone} draft reply...{RESET}")
    reply_text = _ai_complete(prompt)

    # Encode and save as draft
    raw_email = (
        f"To: {sender}\n"
        f"Subject: Re: {subject}\n"
        f"Content-Type: text/plain\n\n"
        f"{reply_text}"
    )
    encoded = base64.urlsafe_b64encode(raw_email.encode()).decode()
    draft_data = _request("POST", "drafts", json={
        "message": {"raw": encoded, "threadId": thread_id}
    })
    draft_id = draft_data.get("id", "unknown")
    print(f"\n{GREEN}Draft saved (ID: {draft_id}):{RESET}\n")
    print(reply_text)
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="gmail_triage.py",
        description="Gmail Inbox Triage — OC-0137"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list-unread", help="List unread inbox messages")
    p.add_argument("--max-results", type=int, default=20)

    p = sub.add_parser("summarize", help="Summarize an email thread")
    p.add_argument("--message-id", required=True)

    p = sub.add_parser("label", help="Add a label to a message")
    p.add_argument("--message-id", required=True)
    p.add_argument("--label-name", required=True)

    p = sub.add_parser("archive", help="Archive a message")
    p.add_argument("--message-id", required=True)

    p = sub.add_parser("draft-reply", help="Generate a draft reply")
    p.add_argument("--message-id", required=True)
    p.add_argument("--tone", default="professional",
                   choices=["professional", "friendly", "concise", "formal"])

    args = parser.parse_args()
    dispatch = {
        "list-unread":  lambda: list_unread(args.max_results),
        "summarize":    lambda: summarize(args.message_id),
        "label":        lambda: label(args.message_id, args.label_name),
        "archive":      lambda: archive(args.message_id),
        "draft-reply":  lambda: draft_reply(args.message_id, args.tone),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()

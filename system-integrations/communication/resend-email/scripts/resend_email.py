#!/usr/bin/env python3
"""Resend Email Sender – OC-0075"""

import argparse
import json
import os
import sys
import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://api.resend.com"


def _headers():
    token = os.environ.get("RESEND_API_KEY")
    if not token:
        print(f"{RED}Error: RESEND_API_KEY is not set{RESET}")
        sys.exit(1)
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _request(method, path, **kwargs):
    resp = getattr(requests, method)(f"{BASE_URL}{path}", headers=_headers(), **kwargs)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.content else {}


def send_email(args):
    if not args.html and not args.text:
        print(f"{RED}Error: at least one of --html or --text is required{RESET}")
        sys.exit(1)
    payload = {
        "from": args.sender,
        "to": [args.to],
        "subject": args.subject,
    }
    if args.html:
        payload["html"] = args.html
    if args.text:
        payload["text"] = args.text
    data = _request("post", "/emails", json=payload)
    print(f"{GREEN}Email sent:{RESET} id={data.get('id')}")


def list_emails(args):
    data = _request("get", "/emails")
    for email in data.get("data", []):
        status = email.get("last_event", "unknown")
        color = GREEN if status == "delivered" else YELLOW
        print(f"{color}{status}{RESET}  {email['id']}  to={email.get('to', 'n/a')}  subject={email.get('subject', '')}")


def get_email(args):
    data = _request("get", f"/emails/{args.email_id}")
    print(f"{GREEN}Email {data.get('id')}{RESET}")
    print(f"  From:    {data.get('from', 'n/a')}")
    print(f"  To:      {data.get('to', 'n/a')}")
    print(f"  Subject: {data.get('subject', 'n/a')}")
    print(f"  Status:  {data.get('last_event', 'n/a')}")
    print(f"  Created: {data.get('created_at', 'n/a')}")


def list_domains(args):
    data = _request("get", "/domains")
    for d in data.get("data", []):
        status = d.get("status", "unknown")
        color = GREEN if status == "verified" else YELLOW
        print(f"{color}{status}{RESET}  {d['id']}  {d.get('name', 'n/a')}")


def list_api_keys(args):
    data = _request("get", "/api-keys")
    for key in data.get("data", []):
        print(f"{GREEN}{key.get('name', 'n/a')}{RESET}  id={key['id']}  created={key.get('created_at', 'n/a')}")


def main():
    parser = argparse.ArgumentParser(description="Resend Email Sender")
    sub = parser.add_subparsers(dest="command", required=True)

    p_send = sub.add_parser("send", help="Send a transactional email")
    p_send.add_argument("--from", dest="sender", required=True, help="Sender email address")
    p_send.add_argument("--to", required=True, help="Recipient email address")
    p_send.add_argument("--subject", required=True)
    p_send.add_argument("--html", default=None, help="HTML body")
    p_send.add_argument("--text", default=None, help="Plain text body")

    sub.add_parser("list-emails", help="List recently sent emails")

    p_get = sub.add_parser("get-email", help="Get email details")
    p_get.add_argument("--email-id", required=True)

    sub.add_parser("list-domains", help="List verified sending domains")

    sub.add_parser("list-api-keys", help="List API keys")

    args = parser.parse_args()
    commands = {
        "send": send_email,
        "list-emails": list_emails,
        "get-email": get_email,
        "list-domains": list_domains,
        "list-api-keys": list_api_keys,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()

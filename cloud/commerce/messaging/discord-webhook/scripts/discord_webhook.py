#!/usr/bin/env python3
"""Discord Webhook Notifier – OC-0078"""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def _headers():
    return {"Content-Type": "application/json"}


def _webhook_url():
    url = os.environ.get("DISCORD_WEBHOOK_URL")
    if not url:
        print(f"{RED}Error: DISCORD_WEBHOOK_URL is not set{RESET}")
        sys.exit(1)
    return url


def _request(method, url, **kwargs):
    resp = getattr(requests, method)(url, headers=_headers(), **kwargs)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    if resp.status_code == 204:
        return None
    return resp.json()


def send(args):
    url = f"{_webhook_url()}?wait=true"
    payload = {"content": args.content}
    data = _request("post", url, json=payload)
    print(f"{GREEN}Message sent:{RESET} id={data['id']}")


def send_embed(args):
    url = f"{_webhook_url()}?wait=true"
    embed = {
        "title": args.title,
        "description": args.description,
    }
    if args.color:
        embed["color"] = int(args.color, 16)
    if args.field:
        fields = []
        for f in args.field:
            name, value = f.split(":", 1)
            fields.append({"name": name, "value": value, "inline": True})
        embed["fields"] = fields
    payload = {"embeds": [embed]}
    data = _request("post", url, json=payload)
    print(f"{GREEN}Embed sent:{RESET} id={data['id']}")


def get_message(args):
    url = f"{_webhook_url()}/messages/{args.message_id}"
    data = _request("get", url)
    content = data.get("content") or "(embed)"
    timestamp = data.get("timestamp", "unknown")
    print(f"{GREEN}ID:{RESET} {data['id']}")
    print(f"{GREEN}Content:{RESET} {content}")
    print(f"{GREEN}Timestamp:{RESET} {timestamp}")
    if data.get("embeds"):
        for i, embed in enumerate(data["embeds"]):
            print(f"{YELLOW}Embed {i + 1}:{RESET} {embed.get('title', 'untitled')}")


def edit_message(args):
    url = f"{_webhook_url()}/messages/{args.message_id}"
    payload = {"content": args.content}
    data = _request("patch", url, json=payload)
    print(f"{GREEN}Message edited:{RESET} id={data['id']}")


def delete_message(args):
    url = f"{_webhook_url()}/messages/{args.message_id}"
    _request("delete", url)
    print(f"{GREEN}Message deleted:{RESET} id={args.message_id}")


def main():
    parser = argparse.ArgumentParser(description="Discord Webhook Notifier")
    sub = parser.add_subparsers(dest="command", required=True)

    p_send = sub.add_parser("send", help="Send a plain text message")
    p_send.add_argument("--content", required=True)

    p_embed = sub.add_parser("send-embed", help="Send a rich embed message")
    p_embed.add_argument("--title", required=True)
    p_embed.add_argument("--description", required=True)
    p_embed.add_argument("--color", default=None, help="Hex color (e.g. ff0000)")
    p_embed.add_argument("--field", action="append", help="Field as name:value")

    p_get = sub.add_parser("get-message", help="Retrieve a webhook message by ID")
    p_get.add_argument("--message-id", required=True)

    p_edit = sub.add_parser("edit-message", help="Edit a webhook message")
    p_edit.add_argument("--message-id", required=True)
    p_edit.add_argument("--content", required=True)

    p_del = sub.add_parser("delete-message", help="Delete a webhook message")
    p_del.add_argument("--message-id", required=True)

    args = parser.parse_args()
    commands = {
        "send": send,
        "send-embed": send_embed,
        "get-message": get_message,
        "edit-message": edit_message,
        "delete-message": delete_message,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()

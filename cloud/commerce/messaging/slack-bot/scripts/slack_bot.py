#!/usr/bin/env python3
"""Slack Bot Publisher – OC-0077"""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://slack.com/api"


def _headers():
    token = os.environ.get("SLACK_BOT_TOKEN")
    if not token:
        print(f"{RED}Error: SLACK_BOT_TOKEN is not set{RESET}")
        sys.exit(1)
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _request(method, path, **kwargs):
    resp = getattr(requests, method)(f"{BASE_URL}{path}", headers=_headers(), **kwargs)
    if not resp.ok:
        print(f"{RED}HTTP error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    data = resp.json()
    # Slack API returns 200 even on errors; check the "ok" field
    if not data.get("ok"):
        print(f"{RED}Slack API error: {data.get('error', 'unknown')}{RESET}")
        sys.exit(1)
    return data


def post_message(args):
    payload = {"channel": args.channel, "text": args.text}
    data = _request("post", "/chat.postMessage", json=payload)
    print(f"{GREEN}Message posted:{RESET} ts={data.get('ts')} channel={data.get('channel')}")


def list_channels(args):
    params = {"limit": args.limit}
    data = _request("get", "/conversations.list", params=params)
    for ch in data.get("channels", []):
        print(f"{GREEN}{ch['name']}{RESET}  id={ch['id']}")


def list_members(args):
    params = {"channel": args.channel}
    data = _request("get", "/conversations.members", params=params)
    for member_id in data.get("members", []):
        print(f"{GREEN}{member_id}{RESET}")


def upload_file(args):
    if not args.content and not args.file:
        print(f"{RED}Error: --content or --file is required{RESET}")
        sys.exit(1)
    payload = {"channels": args.channels}
    if args.content:
        payload["content"] = args.content
    if args.title:
        payload["title"] = args.title
    if args.file:
        with open(args.file, "rb") as fh:
            # File uploads use multipart form data, not JSON
            resp = requests.post(
                f"{BASE_URL}/files.upload",
                headers={"Authorization": _headers()["Authorization"]},
                data={"channels": args.channels, "title": args.title or ""},
                files={"file": fh},
            )
            if not resp.ok:
                print(f"{RED}HTTP error ({resp.status_code}): {resp.text}{RESET}")
                sys.exit(1)
            data = resp.json()
            if not data.get("ok"):
                print(f"{RED}Slack API error: {data.get('error', 'unknown')}{RESET}")
                sys.exit(1)
    else:
        data = _request("post", "/files.upload", json=payload)
    f = data.get("file", {})
    print(f"{GREEN}File uploaded:{RESET} id={f.get('id')}  name={f.get('name')}")


def set_topic(args):
    payload = {"channel": args.channel, "topic": args.topic}
    data = _request("post", "/conversations.setTopic", json=payload)
    print(f"{GREEN}Topic set:{RESET} {data.get('topic', {}).get('value', args.topic)}")


def main():
    parser = argparse.ArgumentParser(description="Slack Bot Publisher")
    sub = parser.add_subparsers(dest="command", required=True)

    p_post = sub.add_parser("post-message", help="Post a message to a channel")
    p_post.add_argument("--channel", required=True)
    p_post.add_argument("--text", required=True)

    p_channels = sub.add_parser("list-channels", help="List available channels")
    p_channels.add_argument("--limit", type=int, default=100)

    p_members = sub.add_parser("list-members", help="List members of a channel")
    p_members.add_argument("--channel", required=True)

    p_upload = sub.add_parser("upload-file", help="Upload a file to a channel")
    p_upload.add_argument("--channels", required=True)
    p_upload.add_argument("--content", default=None, help="Text content to upload")
    p_upload.add_argument("--file", default=None, help="Path to a file to upload")
    p_upload.add_argument("--title", default=None)

    p_topic = sub.add_parser("set-topic", help="Set the topic of a channel")
    p_topic.add_argument("--channel", required=True)
    p_topic.add_argument("--topic", required=True)

    args = parser.parse_args()
    commands = {
        "post-message": post_message,
        "list-channels": list_channels,
        "list-members": list_members,
        "upload-file": upload_file,
        "set-topic": set_topic,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()

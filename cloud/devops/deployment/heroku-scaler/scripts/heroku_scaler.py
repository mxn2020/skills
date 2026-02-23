#!/usr/bin/env python3
"""Heroku Dyno Scaler – OC-0020"""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://api.heroku.com"


def _headers():
    key = os.environ.get("HEROKU_API_KEY")
    if not key:
        print(f"{RED}Error: HEROKU_API_KEY is not set{RESET}")
        sys.exit(1)
    return {
        "Authorization": f"Bearer {key}",
        "Accept": "application/vnd.heroku+json; version=3",
        "Content-Type": "application/json",
    }


def _request(method, path, **kwargs):
    resp = getattr(requests, method)(f"{BASE_URL}{path}", headers=_headers(), **kwargs)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.content else {}


def list_apps(args):
    data = _request("get", "/apps")
    for app in data:
        print(f"{GREEN}{app['name']}{RESET}  region={app.get('region', {}).get('name', 'n/a')}  stack={app.get('build_stack', {}).get('name', 'n/a')}")


def scale(args):
    payload = {"quantity": args.qty, "size": args.size}
    _request("patch", f"/apps/{args.app}/formation/{args.type}", json=payload)
    print(f"{GREEN}Scaled {args.app} {args.type} to {args.qty} x {args.size}{RESET}")


def restart(args):
    _request("delete", f"/apps/{args.app}/dynos")
    print(f"{GREEN}Restarted all dynos for {args.app}{RESET}")


def get_logs(args):
    payload = {"lines": args.lines, "tail": False}
    data = _request("post", f"/apps/{args.app}/log-sessions", json=payload)
    log_url = data.get("logplex_url")
    if not log_url:
        print(f"{RED}Could not create log session{RESET}")
        sys.exit(1)
    resp = requests.get(log_url, stream=True)
    for line in resp.iter_lines(decode_unicode=True):
        if line:
            print(line)


def list_dynos(args):
    data = _request("get", f"/apps/{args.app}/dynos")
    for d in data:
        state = d.get("state", "unknown")
        color = GREEN if state == "up" else YELLOW
        print(f"{color}{state}{RESET}  {d.get('type')}  {d.get('name')}  size={d.get('size')}")


def main():
    parser = argparse.ArgumentParser(description="Heroku Dyno Scaler")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-apps", help="List apps")

    p_scale = sub.add_parser("scale", help="Scale dynos")
    p_scale.add_argument("--app", required=True)
    p_scale.add_argument("--type", required=True, help="Dyno type (web, worker, etc.)")
    p_scale.add_argument("--qty", type=int, required=True)
    p_scale.add_argument("--size", default="standard-1x")

    p_restart = sub.add_parser("restart", help="Restart dynos")
    p_restart.add_argument("--app", required=True)

    p_logs = sub.add_parser("get-logs", help="Get logs")
    p_logs.add_argument("--app", required=True)
    p_logs.add_argument("--lines", type=int, default=100)

    p_dynos = sub.add_parser("list-dynos", help="List dynos")
    p_dynos.add_argument("--app", required=True)

    args = parser.parse_args()
    commands = {
        "list-apps": list_apps,
        "scale": scale,
        "restart": restart,
        "get-logs": get_logs,
        "list-dynos": list_dynos,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()

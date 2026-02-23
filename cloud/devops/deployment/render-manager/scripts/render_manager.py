#!/usr/bin/env python3
"""Render Service Manager – OC-0012"""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://api.render.com/v1"


def _headers():
    key = os.environ.get("RENDER_API_KEY")
    if not key:
        print(f"{RED}Error: RENDER_API_KEY is not set{RESET}")
        sys.exit(1)
    return {"Authorization": f"Bearer {key}", "Accept": "application/json"}


def _request(method, path, **kwargs):
    resp = getattr(requests, method)(f"{BASE_URL}{path}", headers=_headers(), **kwargs)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.content else {}


def list_services(args):
    data = _request("get", "/services", params={"limit": args.limit})
    for item in data:
        svc = item.get("service", item)
        print(f"{GREEN}{svc['name']}{RESET}  id={svc['id']}  type={svc.get('type', 'n/a')}")


def get_service(args):
    data = _request("get", f"/services/{args.service_id}")
    svc = data.get("service", data)
    print(f"{GREEN}{svc['name']}{RESET}")
    print(f"  ID:     {svc['id']}")
    print(f"  Type:   {svc.get('type', 'n/a')}")
    print(f"  Status: {svc.get('suspended', 'active')}")
    print(f"  URL:    {svc.get('serviceDetails', {}).get('url', 'n/a')}")


def scale(args):
    payload = {"numInstances": args.num_instances}
    _request("patch", f"/services/{args.service_id}/scale", json=payload)
    print(f"{GREEN}Scaled {args.service_id} to {args.num_instances} instance(s){RESET}")


def restart(args):
    _request("post", f"/services/{args.service_id}/restart")
    print(f"{GREEN}Restart triggered for {args.service_id}{RESET}")


def get_deploys(args):
    data = _request("get", f"/services/{args.service_id}/deploys", params={"limit": args.limit})
    for item in data:
        d = item.get("deploy", item)
        status = d.get("status", "unknown")
        color = GREEN if status == "live" else YELLOW
        print(f"{color}{status}{RESET}  {d.get('id', 'n/a')}  commit={d.get('commit', {}).get('message', 'n/a')[:50]}")


def main():
    parser = argparse.ArgumentParser(description="Render Service Manager")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list-services", help="List services")
    p_list.add_argument("--limit", type=int, default=20)

    p_get = sub.add_parser("get-service", help="Get service details")
    p_get.add_argument("--service-id", required=True)

    p_scale = sub.add_parser("scale", help="Scale service")
    p_scale.add_argument("--service-id", required=True)
    p_scale.add_argument("--num-instances", type=int, required=True)

    p_restart = sub.add_parser("restart", help="Restart service")
    p_restart.add_argument("--service-id", required=True)

    p_deploys = sub.add_parser("get-deploys", help="List deploys")
    p_deploys.add_argument("--service-id", required=True)
    p_deploys.add_argument("--limit", type=int, default=10)

    args = parser.parse_args()
    commands = {
        "list-services": list_services,
        "get-service": get_service,
        "scale": scale,
        "restart": restart,
        "get-deploys": get_deploys,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()

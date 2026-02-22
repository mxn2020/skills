#!/usr/bin/env python3
"""Vercel Deployment Manager – OC-0009"""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://api.vercel.com"


def _headers():
    token = os.environ.get("VERCEL_TOKEN")
    if not token:
        print(f"{RED}Error: VERCEL_TOKEN is not set{RESET}")
        sys.exit(1)
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _request(method, path, **kwargs):
    resp = getattr(requests, method)(f"{BASE_URL}{path}", headers=_headers(), **kwargs)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json()


def list_projects(args):
    data = _request("get", "/v9/projects")
    for p in data.get("projects", []):
        print(f"{GREEN}{p['name']}{RESET}  id={p['id']}")


def deploy(args):
    payload = {"name": args.project, "target": args.target}
    if args.git_ref:
        payload["gitSource"] = {"ref": args.git_ref, "type": "github"}
    data = _request("post", "/v13/deployments", json=payload)
    print(f"{GREEN}Deployment created:{RESET} {data.get('id')} -> {data.get('url')}")


def list_deployments(args):
    params = {"limit": args.limit}
    if args.project:
        params["projectId"] = args.project
    data = _request("get", "/v6/deployments", params=params)
    for d in data.get("deployments", []):
        state = d.get("readyState", d.get("state", "unknown"))
        color = GREEN if state == "READY" else YELLOW
        print(f"{color}{state}{RESET}  {d['uid']}  {d.get('url', 'n/a')}")


def set_env(args):
    payload = {
        "key": args.key,
        "value": args.value,
        "type": "encrypted",
        "target": [args.target],
    }
    data = _request("post", f"/v10/projects/{args.project}/env", json=payload)
    print(f"{GREEN}Env var set:{RESET} {data.get('key')} on {args.target}")


def alias_domain(args):
    payload = {"alias": args.domain}
    data = _request("post", f"/v2/deployments/{args.deployment_id}/aliases", json=payload)
    print(f"{GREEN}Alias assigned:{RESET} {data.get('alias')}")


def main():
    parser = argparse.ArgumentParser(description="Vercel Deployment Manager")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-projects", help="List all projects")

    p_deploy = sub.add_parser("deploy", help="Trigger a deployment")
    p_deploy.add_argument("--project", required=True)
    p_deploy.add_argument("--target", default="production")
    p_deploy.add_argument("--git-ref", default=None)

    p_list = sub.add_parser("list-deployments", help="List deployments")
    p_list.add_argument("--project", default=None)
    p_list.add_argument("--limit", type=int, default=10)

    p_env = sub.add_parser("set-env", help="Set environment variable")
    p_env.add_argument("--project", required=True)
    p_env.add_argument("--key", required=True)
    p_env.add_argument("--value", required=True)
    p_env.add_argument("--target", default="production")

    p_alias = sub.add_parser("alias-domain", help="Alias a domain")
    p_alias.add_argument("--deployment-id", required=True)
    p_alias.add_argument("--domain", required=True)

    args = parser.parse_args()
    commands = {
        "list-projects": list_projects,
        "deploy": deploy,
        "list-deployments": list_deployments,
        "set-env": set_env,
        "alias-domain": alias_domain,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()

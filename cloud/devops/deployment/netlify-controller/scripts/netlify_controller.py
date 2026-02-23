#!/usr/bin/env python3
"""Netlify Site Controller – OC-0010"""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://api.netlify.com/api/v1"


def _headers():
    token = os.environ.get("NETLIFY_TOKEN")
    if not token:
        print(f"{RED}Error: NETLIFY_TOKEN is not set{RESET}")
        sys.exit(1)
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _request(method, path, **kwargs):
    resp = getattr(requests, method)(f"{BASE_URL}{path}", headers=_headers(), **kwargs)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json()


def list_sites(args):
    data = _request("get", "/sites")
    for s in data:
        print(f"{GREEN}{s['name']}{RESET}  url={s.get('ssl_url', s.get('url', 'n/a'))}")


def deploy(args):
    payload = {}
    if args.clear:
        payload["clear"] = True
    data = _request("post", f"/sites/{args.site_id}/deploys", json=payload)
    print(f"{GREEN}Deploy triggered:{RESET} {data.get('id')}  state={data.get('state')}")


def get_site(args):
    data = _request("get", f"/sites/{args.site_id}")
    print(f"{GREEN}{data['name']}{RESET}")
    print(f"  URL:    {data.get('ssl_url', data.get('url'))}")
    print(f"  Repo:   {data.get('build_settings', {}).get('repo_url', 'n/a')}")
    print(f"  Branch: {data.get('build_settings', {}).get('repo_branch', 'n/a')}")


def list_forms(args):
    data = _request("get", f"/sites/{args.site_id}/forms")
    for f in data:
        print(f"{GREEN}{f['name']}{RESET}  id={f['id']}  submissions={f.get('submission_count', 0)}")


def list_submissions(args):
    data = _request("get", f"/forms/{args.form_id}/submissions")
    for s in data:
        print(f"{YELLOW}{s['id']}{RESET}  created={s.get('created_at', 'n/a')}")
        for k, v in s.get("data", {}).items():
            print(f"    {k}: {v}")


def main():
    parser = argparse.ArgumentParser(description="Netlify Site Controller")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-sites", help="List all sites")

    p_deploy = sub.add_parser("deploy", help="Trigger deploy")
    p_deploy.add_argument("--site-id", required=True)
    p_deploy.add_argument("--clear", action="store_true", help="Clear cache")

    p_get = sub.add_parser("get-site", help="Get site details")
    p_get.add_argument("--site-id", required=True)

    p_forms = sub.add_parser("list-forms", help="List site forms")
    p_forms.add_argument("--site-id", required=True)

    p_sub = sub.add_parser("list-submissions", help="List form submissions")
    p_sub.add_argument("--form-id", required=True)

    args = parser.parse_args()
    commands = {
        "list-sites": list_sites,
        "deploy": deploy,
        "get-site": get_site,
        "list-forms": list_forms,
        "list-submissions": list_submissions,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()

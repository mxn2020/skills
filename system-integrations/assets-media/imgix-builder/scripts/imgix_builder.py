#!/usr/bin/env python3
"""Imgix URL Builder – OC-0067"""

import argparse
import json
import os
import sys
from urllib.parse import urlencode

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

API_BASE = "https://api.imgix.com/api/v1"


def _api_key():
    key = os.environ.get("IMGIX_API_KEY")
    if not key:
        print(f"{RED}Error: IMGIX_API_KEY is not set{RESET}")
        sys.exit(1)
    return key


def _domain():
    domain = os.environ.get("IMGIX_DOMAIN")
    if not domain:
        print(f"{RED}Error: IMGIX_DOMAIN is not set{RESET}")
        sys.exit(1)
    return domain


def _headers():
    return {
        "Authorization": f"Bearer {_api_key()}",
        "Content-Type": "application/vnd.api+json",
    }


def _request(method, path, **kwargs):
    resp = getattr(requests, method)(f"{API_BASE}{path}", headers=_headers(), **kwargs)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.content else {}


def build_url(args):
    domain = args.domain or _domain()
    params = {}
    if args.width:
        params["w"] = args.width
    if args.height:
        params["h"] = args.height
    if args.fit:
        params["fit"] = args.fit
    if args.auto:
        params["auto"] = args.auto
    if args.quality:
        params["q"] = args.quality
    if args.format:
        params["fm"] = args.format

    path = args.path.lstrip("/")
    qs = f"?{urlencode(params)}" if params else ""
    url = f"https://{domain}/{path}{qs}"
    print(f"{GREEN}Generated URL:{RESET}")
    print(f"  {url}")


def list_sources(args):
    data = _request("get", "/sources")
    sources = data.get("data", [])
    print(f"{GREEN}Found {len(sources)} source(s){RESET}")
    for src in sources:
        attrs = src.get("attributes", {})
        name = attrs.get("name", "n/a")
        domain = attrs.get("domain", "n/a")
        enabled = attrs.get("enabled", False)
        color = GREEN if enabled else YELLOW
        print(f"  {color}{src['id']}{RESET}  {name}  domain={domain}  enabled={enabled}")


def purge(args):
    payload = {
        "data": {
            "type": "purges",
            "attributes": {"url": args.url},
        }
    }
    _request("post", "/purges", json=payload)
    print(f"{GREEN}Purge requested for {args.url}{RESET}")


def get_source(args):
    data = _request("get", f"/sources/{args.source_id}")
    src = data.get("data", {})
    attrs = src.get("attributes", {})
    print(f"{GREEN}Source {src.get('id', 'n/a')}{RESET}")
    print(f"  Name:       {attrs.get('name', 'n/a')}")
    print(f"  Domain:     {attrs.get('domain', 'n/a')}")
    print(f"  Enabled:    {attrs.get('enabled', 'n/a')}")
    print(f"  Type:       {attrs.get('deployment_status', 'n/a')}")
    print(f"  Created:    {attrs.get('date_deployed', 'n/a')}")


def main():
    parser = argparse.ArgumentParser(description="Imgix URL Builder")
    sub = parser.add_subparsers(dest="command", required=True)

    p_build = sub.add_parser("build-url", help="Build a transformation URL")
    p_build.add_argument("--path", required=True, help="Image path on the source")
    p_build.add_argument("--domain", help="Override default Imgix domain")
    p_build.add_argument("--width", type=int, help="Output width")
    p_build.add_argument("--height", type=int, help="Output height")
    p_build.add_argument("--fit", choices=["crop", "clip", "fill", "max", "min", "scale"])
    p_build.add_argument("--auto", help="Auto params (e.g. compress,format)")
    p_build.add_argument("--quality", type=int, help="Quality 0-100")
    p_build.add_argument("--format", choices=["jpg", "png", "webp", "avif"])

    sub.add_parser("list-sources", help="List Imgix sources")

    p_purge = sub.add_parser("purge", help="Purge a cached image")
    p_purge.add_argument("--url", required=True, help="Full image URL to purge")

    p_src = sub.add_parser("get-source", help="Get source details")
    p_src.add_argument("--source-id", required=True)

    args = parser.parse_args()
    commands = {
        "build-url": build_url,
        "list-sources": list_sources,
        "purge": purge,
        "get-source": get_source,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()

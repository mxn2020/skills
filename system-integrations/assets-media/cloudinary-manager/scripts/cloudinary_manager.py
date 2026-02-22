#!/usr/bin/env python3
"""Cloudinary Asset Manager – OC-0065"""

import argparse
import json
import os
import re
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def _config():
    url = os.environ.get("CLOUDINARY_URL")
    if url:
        m = re.match(r"cloudinary://([^:]+):([^@]+)@(.+)", url)
        if not m:
            print(f"{RED}Error: invalid CLOUDINARY_URL format{RESET}")
            sys.exit(1)
        return m.group(3), m.group(1), m.group(2)
    cloud = os.environ.get("CLOUDINARY_CLOUD_NAME")
    key = os.environ.get("CLOUDINARY_API_KEY")
    secret = os.environ.get("CLOUDINARY_API_SECRET")
    if not all([cloud, key, secret]):
        print(f"{RED}Error: set CLOUDINARY_URL or CLOUDINARY_CLOUD_NAME/API_KEY/API_SECRET{RESET}")
        sys.exit(1)
    return cloud, key, secret


def _api(method, path, **kwargs):
    cloud, key, secret = _config()
    url = f"https://api.cloudinary.com/v1_1/{cloud}{path}"
    resp = getattr(requests, method)(url, auth=(key, secret), **kwargs)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.content else {}


def upload(args):
    payload = {"file": args.url, "public_id": args.public_id}
    if args.folder:
        payload["folder"] = args.folder
    data = _api("post", "/image/upload", data=payload)
    print(f"{GREEN}Uploaded {data.get('public_id', 'n/a')}{RESET}")
    print(f"  URL:    {data.get('secure_url', 'n/a')}")
    print(f"  Format: {data.get('format', 'n/a')}  Size: {data.get('bytes', 0)} bytes")


def list_resources(args):
    params = {"max_results": args.max_results}
    if args.resource_type:
        params["resource_type"] = args.resource_type
    data = _api("get", "/resources/image", params=params)
    resources = data.get("resources", [])
    print(f"{GREEN}Found {len(resources)} resource(s){RESET}")
    for r in resources:
        print(f"  {YELLOW}{r.get('public_id', 'n/a')}{RESET}  {r.get('format', '?')}  {r.get('bytes', 0)} bytes")


def get_resource(args):
    data = _api("get", f"/resources/image/upload/{args.public_id}")
    print(f"{GREEN}Resource {data.get('public_id', 'n/a')}{RESET}")
    print(f"  Format:  {data.get('format', 'n/a')}")
    print(f"  Size:    {data.get('bytes', 0)} bytes")
    print(f"  Width:   {data.get('width', 0)}")
    print(f"  Height:  {data.get('height', 0)}")
    print(f"  URL:     {data.get('secure_url', 'n/a')}")
    print(f"  Created: {data.get('created_at', 'n/a')}")


def transform(args):
    cloud, _, _ = _config()
    parts = []
    if args.width:
        parts.append(f"w_{args.width}")
    if args.height:
        parts.append(f"h_{args.height}")
    if args.crop:
        parts.append(f"c_{args.crop}")
    if args.quality:
        parts.append(f"q_{args.quality}")
    transform_str = ",".join(parts) if parts else "q_auto"
    url = f"https://res.cloudinary.com/{cloud}/image/upload/{transform_str}/{args.public_id}"
    print(f"{GREEN}Transformation URL:{RESET}")
    print(f"  {url}")


def delete(args):
    data = _api("post", "/resources/image/upload/destroy", data={"public_id": args.public_id})
    result = data.get("result", "unknown")
    if result == "ok":
        print(f"{GREEN}Deleted {args.public_id}{RESET}")
    else:
        print(f"{YELLOW}Result: {result}{RESET}")


def search(args):
    payload = {"expression": args.expression, "max_results": args.max_results}
    data = _api("post", "/resources/search", json=payload)
    resources = data.get("resources", [])
    total = data.get("total_count", len(resources))
    print(f"{GREEN}Search returned {total} result(s){RESET}")
    for r in resources:
        print(f"  {YELLOW}{r.get('public_id', 'n/a')}{RESET}  {r.get('format', '?')}  {r.get('bytes', 0)} bytes")


def main():
    parser = argparse.ArgumentParser(description="Cloudinary Asset Manager")
    sub = parser.add_subparsers(dest="command", required=True)

    p_up = sub.add_parser("upload", help="Upload an image")
    p_up.add_argument("--url", required=True, help="Image URL or local path")
    p_up.add_argument("--public-id", required=True, help="Public ID for the asset")
    p_up.add_argument("--folder", help="Destination folder")

    p_list = sub.add_parser("list", help="List resources")
    p_list.add_argument("--max-results", type=int, default=10)
    p_list.add_argument("--resource-type", default="image")

    p_get = sub.add_parser("get", help="Get resource details")
    p_get.add_argument("--public-id", required=True)

    p_tx = sub.add_parser("transform", help="Generate transformation URL")
    p_tx.add_argument("--public-id", required=True)
    p_tx.add_argument("--width", type=int)
    p_tx.add_argument("--height", type=int)
    p_tx.add_argument("--crop", choices=["fill", "fit", "scale", "crop", "thumb"])
    p_tx.add_argument("--quality", help="Quality (e.g. auto, 80)")

    p_del = sub.add_parser("delete", help="Delete a resource")
    p_del.add_argument("--public-id", required=True)

    p_search = sub.add_parser("search", help="Search assets")
    p_search.add_argument("--expression", required=True, help="Search expression")
    p_search.add_argument("--max-results", type=int, default=10)

    args = parser.parse_args()
    commands = {
        "upload": upload,
        "list": list_resources,
        "get": get_resource,
        "transform": transform,
        "delete": delete,
        "search": search,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()

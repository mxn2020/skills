#!/usr/bin/env python3
"""Unsplash Photo Search – OC-0064"""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://api.unsplash.com"


def _headers():
    key = os.environ.get("UNSPLASH_ACCESS_KEY")
    if not key:
        print(f"{RED}Error: UNSPLASH_ACCESS_KEY is not set{RESET}")
        sys.exit(1)
    return {"Authorization": f"Client-ID {key}", "Accept-Version": "v1"}


def _request(method, path, **kwargs):
    resp = getattr(requests, method)(f"{BASE_URL}{path}", headers=_headers(), **kwargs)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.content else {}


def search(args):
    params = {"query": args.query, "per_page": args.per_page, "page": args.page}
    if args.orientation:
        params["orientation"] = args.orientation
    data = _request("get", "/search/photos", params=params)
    total = data.get("total", 0)
    print(f"{GREEN}Found {total} results for '{args.query}'{RESET}")
    for photo in data.get("results", []):
        user = photo.get("user", {}).get("name", "unknown")
        print(f"  {YELLOW}{photo['id']}{RESET}  {photo.get('description') or photo.get('alt_description') or 'No description'}  by {user}")


def get_photo(args):
    data = _request("get", f"/photos/{args.photo_id}")
    print(f"{GREEN}Photo {data['id']}{RESET}")
    print(f"  Description: {data.get('description') or data.get('alt_description') or 'n/a'}")
    print(f"  Size:        {data.get('width', 0)}x{data.get('height', 0)}")
    print(f"  Likes:       {data.get('likes', 0)}")
    print(f"  Downloads:   {data.get('downloads', 0)}")
    print(f"  Author:      {data.get('user', {}).get('name', 'n/a')}")
    urls = data.get("urls", {})
    print(f"  URL (full):  {urls.get('full', 'n/a')}")


def download(args):
    data = _request("get", f"/photos/{args.photo_id}")
    dl_link = data.get("links", {}).get("download_location")
    if not dl_link:
        print(f"{RED}Error: no download link found{RESET}")
        sys.exit(1)
    _request("get", dl_link.replace(BASE_URL, ""))
    url = data.get("urls", {}).get("full", "n/a")
    print(f"{GREEN}Download triggered for photo {args.photo_id}{RESET}")
    print(f"  URL: {url}")


def random(args):
    params = {"count": args.count}
    data = _request("get", "/photos/random", params=params)
    if isinstance(data, dict):
        data = [data]
    print(f"{GREEN}Fetched {len(data)} random photo(s){RESET}")
    for photo in data:
        user = photo.get("user", {}).get("name", "unknown")
        print(f"  {YELLOW}{photo['id']}{RESET}  {photo.get('alt_description') or 'No description'}  by {user}")


def list_collections(args):
    params = {"per_page": args.per_page, "page": args.page}
    data = _request("get", "/collections", params=params)
    print(f"{GREEN}Collections (page {args.page}){RESET}")
    for col in data:
        print(f"  {YELLOW}{col['id']}{RESET}  {col.get('title', 'Untitled')}  ({col.get('total_photos', 0)} photos)")


def main():
    parser = argparse.ArgumentParser(description="Unsplash Photo Search")
    sub = parser.add_subparsers(dest="command", required=True)

    p_search = sub.add_parser("search", help="Search photos by keyword")
    p_search.add_argument("--query", required=True, help="Search keyword")
    p_search.add_argument("--per-page", type=int, default=10)
    p_search.add_argument("--page", type=int, default=1)
    p_search.add_argument("--orientation", choices=["landscape", "portrait", "squarish"])

    p_get = sub.add_parser("get-photo", help="Get photo details")
    p_get.add_argument("--photo-id", required=True)

    p_dl = sub.add_parser("download", help="Trigger a download for a photo")
    p_dl.add_argument("--photo-id", required=True)

    p_rand = sub.add_parser("random", help="Fetch random photos")
    p_rand.add_argument("--count", type=int, default=1)

    p_cols = sub.add_parser("list-collections", help="List featured collections")
    p_cols.add_argument("--per-page", type=int, default=10)
    p_cols.add_argument("--page", type=int, default=1)

    args = parser.parse_args()
    commands = {
        "search": search,
        "get-photo": get_photo,
        "download": download,
        "random": random,
        "list-collections": list_collections,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()

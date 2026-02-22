#!/usr/bin/env python3
"""Pexels/Pixabay Search – OC-0068"""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

PEXELS_BASE = "https://api.pexels.com/v1"
PIXABAY_BASE = "https://pixabay.com/api"


def _pexels_headers():
    key = os.environ.get("PEXELS_API_KEY")
    if not key:
        print(f"{RED}Error: PEXELS_API_KEY is not set{RESET}")
        sys.exit(1)
    return {"Authorization": key}


def _pixabay_key():
    key = os.environ.get("PIXABAY_API_KEY")
    if not key:
        print(f"{RED}Error: PIXABAY_API_KEY is not set{RESET}")
        sys.exit(1)
    return key


def _pexels_request(path, params=None):
    resp = requests.get(f"{PEXELS_BASE}{path}", headers=_pexels_headers(), params=params)
    if not resp.ok:
        print(f"{RED}Pexels API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json()


def _pixabay_request(params=None):
    params = params or {}
    params["key"] = _pixabay_key()
    resp = requests.get(f"{PIXABAY_BASE}/", params=params)
    if not resp.ok:
        print(f"{RED}Pixabay API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json()


def search_pexels(args):
    params = {"query": args.query, "per_page": args.per_page, "page": args.page}
    if args.orientation:
        params["orientation"] = args.orientation
    data = _pexels_request("/search", params=params)
    total = data.get("total_results", 0)
    print(f"{GREEN}Pexels: {total} results for '{args.query}'{RESET}")
    for photo in data.get("photos", []):
        print(f"  {YELLOW}{photo['id']}{RESET}  {photo.get('alt', 'No description')}  by {photo.get('photographer', 'unknown')}")
        print(f"    {photo.get('src', {}).get('medium', 'n/a')}")


def search_pixabay(args):
    params = {
        "q": args.query,
        "per_page": args.per_page,
        "page": args.page,
        "image_type": args.image_type,
    }
    data = _pixabay_request(params=params)
    total = data.get("totalHits", 0)
    print(f"{GREEN}Pixabay: {total} results for '{args.query}'{RESET}")
    for hit in data.get("hits", []):
        tags = hit.get("tags", "")
        print(f"  {YELLOW}{hit['id']}{RESET}  {tags}  by {hit.get('user', 'unknown')}")
        print(f"    {hit.get('webformatURL', 'n/a')}")


def download(args):
    print(f"{YELLOW}Downloading {args.url}...{RESET}")
    resp = requests.get(args.url, stream=True)
    if not resp.ok:
        print(f"{RED}Download failed ({resp.status_code}){RESET}")
        sys.exit(1)
    output = args.output or "download.jpg"
    with open(output, "wb") as f:
        for chunk in resp.iter_content(chunk_size=8192):
            f.write(chunk)
    size = os.path.getsize(output)
    print(f"{GREEN}Saved to {output} ({size} bytes){RESET}")


def curated(args):
    params = {"per_page": args.per_page, "page": args.page}
    data = _pexels_request("/curated", params=params)
    photos = data.get("photos", [])
    print(f"{GREEN}Pexels curated photos (page {args.page}){RESET}")
    for photo in photos:
        print(f"  {YELLOW}{photo['id']}{RESET}  {photo.get('alt', 'No description')}  by {photo.get('photographer', 'unknown')}")


def popular(args):
    params = {
        "per_page": args.per_page,
        "page": args.page,
        "order": "popular",
        "editors_choice": "true",
    }
    data = _pixabay_request(params=params)
    hits = data.get("hits", [])
    print(f"{GREEN}Pixabay popular images (page {args.page}){RESET}")
    for hit in hits:
        tags = hit.get("tags", "")
        print(f"  {YELLOW}{hit['id']}{RESET}  {tags}  likes={hit.get('likes', 0)}  downloads={hit.get('downloads', 0)}")


def main():
    parser = argparse.ArgumentParser(description="Pexels/Pixabay Stock Photo Search")
    sub = parser.add_subparsers(dest="command", required=True)

    p_pex = sub.add_parser("search-pexels", help="Search Pexels photos")
    p_pex.add_argument("--query", required=True)
    p_pex.add_argument("--per-page", type=int, default=10)
    p_pex.add_argument("--page", type=int, default=1)
    p_pex.add_argument("--orientation", choices=["landscape", "portrait", "square"])

    p_pix = sub.add_parser("search-pixabay", help="Search Pixabay photos")
    p_pix.add_argument("--query", required=True)
    p_pix.add_argument("--per-page", type=int, default=10)
    p_pix.add_argument("--page", type=int, default=1)
    p_pix.add_argument("--image-type", default="photo", choices=["all", "photo", "illustration", "vector"])

    p_dl = sub.add_parser("download", help="Download a photo by URL")
    p_dl.add_argument("--url", required=True, help="Direct image URL")
    p_dl.add_argument("--output", help="Output file path")

    p_cur = sub.add_parser("curated", help="Fetch curated Pexels photos")
    p_cur.add_argument("--per-page", type=int, default=10)
    p_cur.add_argument("--page", type=int, default=1)

    p_pop = sub.add_parser("popular", help="Fetch popular Pixabay images")
    p_pop.add_argument("--per-page", type=int, default=10)
    p_pop.add_argument("--page", type=int, default=1)

    args = parser.parse_args()
    commands = {
        "search-pexels": search_pexels,
        "search-pixabay": search_pixabay,
        "download": download,
        "curated": curated,
        "popular": popular,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()

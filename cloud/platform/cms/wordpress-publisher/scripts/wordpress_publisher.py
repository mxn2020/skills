#!/usr/bin/env python3
"""WordPress Post Publisher - Draft and publish blog posts via REST API."""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

WP_URL = os.environ.get("WORDPRESS_URL", "").rstrip("/")
WP_USER = os.environ.get("WORDPRESS_USERNAME", "")
WP_PASS = os.environ.get("WORDPRESS_APP_PASSWORD", "")
API_BASE = f"{WP_URL}/wp-json/wp/v2"


def auth():
    return (WP_USER, WP_PASS)


def fail(msg):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def success(msg):
    print(f"{GREEN}{msg}{RESET}")


def warn(msg):
    print(f"{YELLOW}{msg}{RESET}")


def list_posts(args):
    params = {"per_page": args.per_page}
    if args.status:
        params["status"] = args.status
    resp = requests.get(f"{API_BASE}/posts", auth=auth(), params=params)
    resp.raise_for_status()
    posts = resp.json()
    if not posts:
        warn("No posts found.")
        return
    for p in posts:
        title = p["title"]["rendered"]
        print(f"  {GREEN}{p['id']}{RESET}  [{p['status']}] {title}")


def get_post(args):
    resp = requests.get(f"{API_BASE}/posts/{args.id}", auth=auth())
    resp.raise_for_status()
    print(json.dumps(resp.json(), indent=2))


def create_post(args):
    data = {"title": args.title, "content": args.content, "status": args.status}
    resp = requests.post(f"{API_BASE}/posts", auth=auth(), json=data)
    resp.raise_for_status()
    post = resp.json()
    success(f"Post created: id={post['id']}  status={post['status']}")


def update_post(args):
    data = {}
    if args.title:
        data["title"] = args.title
    if args.content:
        data["content"] = args.content
    if args.status:
        data["status"] = args.status
    if not data:
        fail("Provide at least one of --title, --content, or --status.")
    resp = requests.post(f"{API_BASE}/posts/{args.id}", auth=auth(), json=data)
    resp.raise_for_status()
    success(f"Post '{args.id}' updated.")


def delete_post(args):
    resp = requests.delete(f"{API_BASE}/posts/{args.id}", auth=auth())
    resp.raise_for_status()
    success(f"Post '{args.id}' moved to trash.")


def list_categories(args):
    resp = requests.get(f"{API_BASE}/categories", auth=auth(), params={"per_page": 100})
    resp.raise_for_status()
    cats = resp.json()
    if not cats:
        warn("No categories found.")
        return
    for c in cats:
        print(f"  {GREEN}{c['id']}{RESET}  {c['name']}  (count={c['count']})")


def main():
    if not WP_URL or not WP_USER or not WP_PASS:
        fail("WORDPRESS_URL, WORDPRESS_USERNAME, and WORDPRESS_APP_PASSWORD are required.")

    parser = argparse.ArgumentParser(description="WordPress Post Publisher")
    sub = parser.add_subparsers(dest="command")

    p_list = sub.add_parser("list-posts", help="List posts")
    p_list.add_argument("--status", default=None, choices=["publish", "draft", "pending", "private"])
    p_list.add_argument("--per-page", type=int, default=25)

    p_get = sub.add_parser("get-post", help="Get a post")
    p_get.add_argument("--id", required=True)

    p_create = sub.add_parser("create-post", help="Create a post")
    p_create.add_argument("--title", required=True)
    p_create.add_argument("--content", required=True)
    p_create.add_argument("--status", default="draft", choices=["draft", "publish", "pending", "private"])

    p_update = sub.add_parser("update-post", help="Update a post")
    p_update.add_argument("--id", required=True)
    p_update.add_argument("--title", default=None)
    p_update.add_argument("--content", default=None)
    p_update.add_argument("--status", default=None, choices=["draft", "publish", "pending", "private"])

    p_del = sub.add_parser("delete-post", help="Delete a post")
    p_del.add_argument("--id", required=True)

    sub.add_parser("list-categories", help="List categories")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        {"list-posts": list_posts,
         "get-post": get_post,
         "create-post": create_post,
         "update-post": update_post,
         "delete-post": delete_post,
         "list-categories": list_categories}[args.command](args)
    except requests.HTTPError as e:
        fail(f"API request failed: {e.response.status_code} {e.response.text}")
    except Exception as e:
        fail(str(e))


if __name__ == "__main__":
    main()

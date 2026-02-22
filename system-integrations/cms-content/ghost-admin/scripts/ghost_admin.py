#!/usr/bin/env python3
"""Ghost Admin - Manage membership tiers and posts."""

import argparse
import json
import os
import sys
import time

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

GHOST_URL = os.environ.get("GHOST_URL", "").rstrip("/")
GHOST_ADMIN_KEY = os.environ.get("GHOST_ADMIN_KEY", "")


def make_token():
    try:
        import jwt
    except ImportError:
        fail("PyJWT is required: pip install PyJWT")
    key_id, secret = GHOST_ADMIN_KEY.split(":")
    iat = int(time.time())
    payload = {"iat": iat, "exp": iat + 300, "aud": "/admin/"}
    return jwt.encode(payload, bytes.fromhex(secret), algorithm="HS256",
                      headers={"alg": "HS256", "typ": "JWT", "kid": key_id})


def headers():
    return {"Authorization": f"Ghost {make_token()}", "Content-Type": "application/json"}


def fail(msg):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def success(msg):
    print(f"{GREEN}{msg}{RESET}")


def warn(msg):
    print(f"{YELLOW}{msg}{RESET}")


def api(path):
    return f"{GHOST_URL}/ghost/api/admin{path}"


def list_posts(args):
    resp = requests.get(api("/posts/?limit=25"), headers=headers())
    resp.raise_for_status()
    posts = resp.json().get("posts", [])
    if not posts:
        warn("No posts found.")
        return
    for p in posts:
        print(f"  {GREEN}{p['id']}{RESET}  [{p['status']}] {p['title']}")


def create_post(args):
    post = {"title": args.title, "html": args.html, "status": args.status}
    resp = requests.post(api("/posts/"), headers=headers(), json={"posts": [post]})
    resp.raise_for_status()
    created = resp.json()["posts"][0]
    success(f"Post created: id={created['id']}  status={created['status']}")


def update_post(args):
    resp = requests.get(api(f"/posts/{args.id}/"), headers=headers())
    resp.raise_for_status()
    current = resp.json()["posts"][0]
    post = {"updated_at": current["updated_at"]}
    if args.title:
        post["title"] = args.title
    if args.html:
        post["html"] = args.html
    if args.status:
        post["status"] = args.status
    resp = requests.put(api(f"/posts/{args.id}/"), headers=headers(), json={"posts": [post]})
    resp.raise_for_status()
    success(f"Post '{args.id}' updated.")


def delete_post(args):
    resp = requests.delete(api(f"/posts/{args.id}/"), headers=headers())
    resp.raise_for_status()
    success(f"Post '{args.id}' deleted.")


def list_tiers(args):
    resp = requests.get(api("/tiers/?limit=all"), headers=headers())
    resp.raise_for_status()
    tiers = resp.json().get("tiers", [])
    if not tiers:
        warn("No tiers found.")
        return
    for t in tiers:
        print(f"  {GREEN}{t['id']}{RESET}  {t['name']}  active={t.get('active', False)}")


def list_members(args):
    resp = requests.get(api("/members/?limit=25"), headers=headers())
    resp.raise_for_status()
    members = resp.json().get("members", [])
    if not members:
        warn("No members found.")
        return
    for m in members:
        print(f"  {GREEN}{m['id']}{RESET}  {m.get('email', 'N/A')}  status={m.get('status', 'N/A')}")


def main():
    if not GHOST_URL or not GHOST_ADMIN_KEY:
        fail("GHOST_URL and GHOST_ADMIN_KEY environment variables are required.")

    parser = argparse.ArgumentParser(description="Ghost Admin")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list-posts", help="List posts")

    p_create = sub.add_parser("create-post", help="Create a post")
    p_create.add_argument("--title", required=True)
    p_create.add_argument("--html", required=True)
    p_create.add_argument("--status", default="draft", choices=["draft", "published", "scheduled"])

    p_update = sub.add_parser("update-post", help="Update a post")
    p_update.add_argument("--id", required=True)
    p_update.add_argument("--title", default=None)
    p_update.add_argument("--html", default=None)
    p_update.add_argument("--status", default=None, choices=["draft", "published", "scheduled"])

    p_del = sub.add_parser("delete-post", help="Delete a post")
    p_del.add_argument("--id", required=True)

    sub.add_parser("list-tiers", help="List membership tiers")
    sub.add_parser("list-members", help="List members")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        {"list-posts": list_posts,
         "create-post": create_post,
         "update-post": update_post,
         "delete-post": delete_post,
         "list-tiers": list_tiers,
         "list-members": list_members}[args.command](args)
    except requests.HTTPError as e:
        fail(f"API request failed: {e.response.status_code} {e.response.text}")
    except Exception as e:
        fail(str(e))


if __name__ == "__main__":
    main()

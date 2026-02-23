#!/usr/bin/env python3
"""Weaviate Schema Manager - Manage class definitions and objects."""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

WEAVIATE_URL = os.environ.get("WEAVIATE_URL", "http://localhost:8080")
API_KEY = os.environ.get("WEAVIATE_API_KEY", "")


def headers():
    h = {"Content-Type": "application/json"}
    if API_KEY:
        h["Authorization"] = f"Bearer {API_KEY}"
    return h


def fail(msg):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def success(msg):
    print(f"{GREEN}{msg}{RESET}")


def warn(msg):
    print(f"{YELLOW}{msg}{RESET}")


def get_schema():
    resp = requests.get(f"{WEAVIATE_URL}/v1/schema", headers=headers())
    resp.raise_for_status()
    data = resp.json()
    classes = data.get("classes", [])
    if not classes:
        warn("No classes defined.")
        return
    for cls in classes:
        props = [p["name"] for p in cls.get("properties", [])]
        print(f"  {GREEN}{cls['class']}{RESET}  properties={props}")


def create_class(args):
    properties = json.loads(args.properties) if args.properties else []
    body = {"class": args.name, "properties": properties}
    resp = requests.post(f"{WEAVIATE_URL}/v1/schema", headers=headers(), json=body)
    resp.raise_for_status()
    success(f"Class '{args.name}' created.")


def delete_class(args):
    resp = requests.delete(f"{WEAVIATE_URL}/v1/schema/{args.name}", headers=headers())
    resp.raise_for_status()
    success(f"Class '{args.name}' deleted.")


def list_objects(args):
    params = {"class": args.class_name, "limit": args.limit}
    resp = requests.get(f"{WEAVIATE_URL}/v1/objects", headers=headers(), params=params)
    resp.raise_for_status()
    objects = resp.json().get("objects", [])
    if not objects:
        warn("No objects found.")
        return
    for obj in objects:
        print(f"  id={obj['id']}  class={obj.get('class', 'N/A')}")
        for k, v in obj.get("properties", {}).items():
            print(f"    {k}: {v}")


def query(args):
    gql = {
        "query": (
            f'{{ Get {{ {args.class_name}'
            f'(nearText: {{concepts: ["{args.query}"]}}, limit: {args.limit})'
            f' {{ _additional {{ id distance }} }} }} }}'
        )
    }
    resp = requests.post(f"{WEAVIATE_URL}/v1/graphql", headers=headers(), json=gql)
    resp.raise_for_status()
    results = resp.json().get("data", {}).get("Get", {}).get(args.class_name, [])
    if not results:
        warn("No results found.")
        return
    for r in results:
        extra = r.get("_additional", {})
        print(f"  id={extra.get('id', 'N/A')}  distance={extra.get('distance', 'N/A')}")


def main():
    parser = argparse.ArgumentParser(description="Weaviate Schema Manager")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("get-schema", help="Get full schema")

    p_create = sub.add_parser("create-class", help="Create a class")
    p_create.add_argument("--name", required=True)
    p_create.add_argument("--properties", default="[]", help="JSON array of property definitions")

    p_del = sub.add_parser("delete-class", help="Delete a class")
    p_del.add_argument("--name", required=True)

    p_list = sub.add_parser("list-objects", help="List objects")
    p_list.add_argument("--class-name", required=True)
    p_list.add_argument("--limit", type=int, default=10)

    p_q = sub.add_parser("query", help="Semantic search")
    p_q.add_argument("--class-name", required=True)
    p_q.add_argument("--query", required=True)
    p_q.add_argument("--limit", type=int, default=5)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        {"get-schema": lambda a: get_schema(),
         "create-class": create_class,
         "delete-class": delete_class,
         "list-objects": list_objects,
         "query": query}[args.command](args)
    except requests.HTTPError as e:
        fail(f"API request failed: {e.response.status_code} {e.response.text}")
    except Exception as e:
        fail(str(e))


if __name__ == "__main__":
    main()

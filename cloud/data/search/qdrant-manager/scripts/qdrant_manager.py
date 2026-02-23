#!/usr/bin/env python3
"""Qdrant Collection Manager - Manage collections and similarity queries."""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

QDRANT_URL = os.environ.get("QDRANT_URL", "http://localhost:6333")
API_KEY = os.environ.get("QDRANT_API_KEY", "")


def headers():
    h = {"Content-Type": "application/json"}
    if API_KEY:
        h["api-key"] = API_KEY
    return h


def fail(msg):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def success(msg):
    print(f"{GREEN}{msg}{RESET}")


def warn(msg):
    print(f"{YELLOW}{msg}{RESET}")


def list_collections():
    resp = requests.get(f"{QDRANT_URL}/collections", headers=headers())
    resp.raise_for_status()
    collections = resp.json().get("result", {}).get("collections", [])
    if not collections:
        warn("No collections found.")
        return
    for c in collections:
        print(f"  {GREEN}{c['name']}{RESET}")


def create_collection(args):
    distance_map = {"cosine": "Cosine", "euclid": "Euclid", "dot": "Dot"}
    dist = distance_map.get(args.distance, "Cosine")
    body = {"vectors": {"size": args.size, "distance": dist}}
    resp = requests.put(f"{QDRANT_URL}/collections/{args.name}", headers=headers(), json=body)
    resp.raise_for_status()
    success(f"Collection '{args.name}' created (size={args.size}, distance={dist}).")


def delete_collection(args):
    resp = requests.delete(f"{QDRANT_URL}/collections/{args.name}", headers=headers())
    resp.raise_for_status()
    success(f"Collection '{args.name}' deleted.")


def upsert(args):
    points = json.loads(args.points)
    body = {"points": points}
    resp = requests.put(f"{QDRANT_URL}/collections/{args.name}/points", headers=headers(), json=body)
    resp.raise_for_status()
    success(f"Upserted {len(points)} point(s) into '{args.name}'.")


def search(args):
    vector = json.loads(args.vector)
    body = {"vector": vector, "limit": args.limit, "with_payload": True}
    resp = requests.post(f"{QDRANT_URL}/collections/{args.name}/points/search", headers=headers(), json=body)
    resp.raise_for_status()
    results = resp.json().get("result", [])
    if not results:
        warn("No results found.")
        return
    for r in results:
        print(f"  id={r['id']}  score={r.get('score', 'N/A')}")
        payload = r.get("payload", {})
        if payload:
            print(f"    payload={json.dumps(payload, default=str)[:120]}")


def get_info(args):
    resp = requests.get(f"{QDRANT_URL}/collections/{args.name}", headers=headers())
    resp.raise_for_status()
    info = resp.json().get("result", {})
    print(json.dumps(info, indent=2))


def main():
    parser = argparse.ArgumentParser(description="Qdrant Collection Manager")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list-collections", help="List all collections")

    p_create = sub.add_parser("create-collection", help="Create a collection")
    p_create.add_argument("--name", required=True)
    p_create.add_argument("--size", type=int, required=True, help="Vector dimension size")
    p_create.add_argument("--distance", default="cosine", choices=["cosine", "euclid", "dot"])

    p_del = sub.add_parser("delete-collection", help="Delete a collection")
    p_del.add_argument("--name", required=True)

    p_up = sub.add_parser("upsert", help="Upsert points")
    p_up.add_argument("--name", required=True)
    p_up.add_argument("--points", required=True, help="JSON array of points")

    p_s = sub.add_parser("search", help="Similarity search")
    p_s.add_argument("--name", required=True)
    p_s.add_argument("--vector", required=True, help="JSON array for query vector")
    p_s.add_argument("--limit", type=int, default=5)

    p_info = sub.add_parser("get-info", help="Get collection info")
    p_info.add_argument("--name", required=True)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        {"list-collections": lambda a: list_collections(),
         "create-collection": create_collection,
         "delete-collection": delete_collection,
         "upsert": upsert,
         "search": search,
         "get-info": get_info}[args.command](args)
    except requests.HTTPError as e:
        fail(f"API request failed: {e.response.status_code} {e.response.text}")
    except Exception as e:
        fail(str(e))


if __name__ == "__main__":
    main()

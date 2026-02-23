#!/usr/bin/env python3
"""Chroma DB Manager - Manage vector stores for RAG pipelines."""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

CHROMA_URL = os.environ.get("CHROMA_URL", "http://localhost:8000")


def headers():
    return {"Content-Type": "application/json"}


def fail(msg):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def success(msg):
    print(f"{GREEN}{msg}{RESET}")


def warn(msg):
    print(f"{YELLOW}{msg}{RESET}")


def _get_collection_id(name):
    resp = requests.get(f"{CHROMA_URL}/api/v1/collections/{name}", headers=headers())
    resp.raise_for_status()
    return resp.json()["id"]


def list_collections():
    resp = requests.get(f"{CHROMA_URL}/api/v1/collections", headers=headers())
    resp.raise_for_status()
    collections = resp.json()
    if not collections:
        warn("No collections found.")
        return
    for c in collections:
        print(f"  {GREEN}{c['name']}{RESET}  id={c['id']}")


def create_collection(args):
    body = {"name": args.name, "get_or_create": False}
    resp = requests.post(f"{CHROMA_URL}/api/v1/collections", headers=headers(), json=body)
    resp.raise_for_status()
    success(f"Collection '{args.name}' created.")


def delete_collection(args):
    resp = requests.delete(f"{CHROMA_URL}/api/v1/collections/{args.name}", headers=headers())
    resp.raise_for_status()
    success(f"Collection '{args.name}' deleted.")


def add(args):
    col_id = _get_collection_id(args.name)
    documents = json.loads(args.documents)
    ids = json.loads(args.ids)
    body = {"documents": documents, "ids": ids}
    resp = requests.post(f"{CHROMA_URL}/api/v1/collections/{col_id}/add", headers=headers(), json=body)
    resp.raise_for_status()
    success(f"Added {len(ids)} document(s) to '{args.name}'.")


def query(args):
    col_id = _get_collection_id(args.name)
    texts = json.loads(args.texts)
    body = {"query_texts": texts, "n_results": args.n_results}
    resp = requests.post(f"{CHROMA_URL}/api/v1/collections/{col_id}/query", headers=headers(), json=body)
    resp.raise_for_status()
    data = resp.json()
    ids = data.get("ids", [[]])[0]
    distances = data.get("distances", [[]])[0]
    documents = data.get("documents", [[]])[0]
    if not ids:
        warn("No results found.")
        return
    for i, doc_id in enumerate(ids):
        dist = distances[i] if i < len(distances) else "N/A"
        doc = documents[i] if i < len(documents) else ""
        print(f"  {GREEN}{doc_id}{RESET}  distance={dist}")
        if doc:
            print(f"    {doc[:120]}")


def count(args):
    col_id = _get_collection_id(args.name)
    resp = requests.get(f"{CHROMA_URL}/api/v1/collections/{col_id}/count", headers=headers())
    resp.raise_for_status()
    print(f"  Collection '{args.name}': {GREEN}{resp.json()}{RESET} document(s)")


def main():
    parser = argparse.ArgumentParser(description="Chroma DB Manager")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list-collections", help="List all collections")

    p_create = sub.add_parser("create-collection", help="Create a collection")
    p_create.add_argument("--name", required=True)

    p_del = sub.add_parser("delete-collection", help="Delete a collection")
    p_del.add_argument("--name", required=True)

    p_add = sub.add_parser("add", help="Add documents")
    p_add.add_argument("--name", required=True)
    p_add.add_argument("--documents", required=True, help="JSON array of document strings")
    p_add.add_argument("--ids", required=True, help="JSON array of document IDs")

    p_q = sub.add_parser("query", help="Query by text similarity")
    p_q.add_argument("--name", required=True)
    p_q.add_argument("--texts", required=True, help="JSON array of query texts")
    p_q.add_argument("--n-results", type=int, default=5)

    p_count = sub.add_parser("count", help="Get document count")
    p_count.add_argument("--name", required=True)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        {"list-collections": lambda a: list_collections(),
         "create-collection": create_collection,
         "delete-collection": delete_collection,
         "add": add,
         "query": query,
         "count": count}[args.command](args)
    except requests.HTTPError as e:
        fail(f"API request failed: {e.response.status_code} {e.response.text}")
    except Exception as e:
        fail(str(e))


if __name__ == "__main__":
    main()

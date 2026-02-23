#!/usr/bin/env python3
"""Pinecone Index Manager - Manage vector indexes for RAG applications."""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

API_KEY = os.environ.get("PINECONE_API_KEY", "")
BASE_URL = "https://api.pinecone.io"


def headers():
    return {"Api-Key": API_KEY, "Content-Type": "application/json"}


def fail(msg):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def success(msg):
    print(f"{GREEN}{msg}{RESET}")


def warn(msg):
    print(f"{YELLOW}{msg}{RESET}")


def list_indexes():
    resp = requests.get(f"{BASE_URL}/indexes", headers=headers())
    resp.raise_for_status()
    data = resp.json()
    indexes = data.get("indexes", [])
    if not indexes:
        warn("No indexes found.")
        return
    for idx in indexes:
        print(f"  {GREEN}{idx['name']}{RESET}  dimension={idx.get('dimension')}  metric={idx.get('metric')}")


def create_index(args):
    body = {
        "name": args.name,
        "dimension": args.dimension,
        "metric": args.metric,
        "spec": {"serverless": {"cloud": "aws", "region": "us-east-1"}},
    }
    resp = requests.post(f"{BASE_URL}/indexes", headers=headers(), json=body)
    resp.raise_for_status()
    success(f"Index '{args.name}' created (dimension={args.dimension}, metric={args.metric}).")


def delete_index(args):
    resp = requests.delete(f"{BASE_URL}/indexes/{args.name}", headers=headers())
    resp.raise_for_status()
    success(f"Index '{args.name}' deleted.")


def describe_index(args):
    resp = requests.get(f"{BASE_URL}/indexes/{args.name}", headers=headers())
    resp.raise_for_status()
    data = resp.json()
    print(json.dumps(data, indent=2))


def upsert(args):
    vectors = json.loads(args.vectors)
    host = _get_host(args.name)
    body = {"vectors": vectors}
    resp = requests.post(f"https://{host}/vectors/upsert", headers=headers(), json=body)
    resp.raise_for_status()
    success(f"Upserted {len(vectors)} vector(s) into '{args.name}'.")


def query(args):
    vector = json.loads(args.vector)
    host = _get_host(args.name)
    body = {"vector": vector, "topK": args.top_k, "includeMetadata": True}
    resp = requests.post(f"https://{host}/query", headers=headers(), json=body)
    resp.raise_for_status()
    matches = resp.json().get("matches", [])
    if not matches:
        warn("No matches found.")
        return
    for m in matches:
        print(f"  id={m['id']}  score={m.get('score', 'N/A')}")


def _get_host(name):
    resp = requests.get(f"{BASE_URL}/indexes/{name}", headers=headers())
    resp.raise_for_status()
    return resp.json()["host"]


def main():
    if not API_KEY:
        fail("PINECONE_API_KEY environment variable is required.")

    parser = argparse.ArgumentParser(description="Pinecone Index Manager")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("list-indexes", help="List all indexes")

    p_create = sub.add_parser("create-index", help="Create a new index")
    p_create.add_argument("--name", required=True)
    p_create.add_argument("--dimension", type=int, required=True)
    p_create.add_argument("--metric", default="cosine", choices=["cosine", "euclidean", "dotproduct"])

    p_del = sub.add_parser("delete-index", help="Delete an index")
    p_del.add_argument("--name", required=True)

    p_desc = sub.add_parser("describe-index", help="Describe an index")
    p_desc.add_argument("--name", required=True)

    p_up = sub.add_parser("upsert", help="Upsert vectors")
    p_up.add_argument("--name", required=True)
    p_up.add_argument("--vectors", required=True, help="JSON array of vectors")

    p_q = sub.add_parser("query", help="Query vectors")
    p_q.add_argument("--name", required=True)
    p_q.add_argument("--vector", required=True, help="JSON array for query vector")
    p_q.add_argument("--top-k", type=int, default=5)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    try:
        {"list-indexes": lambda a: list_indexes(),
         "create-index": create_index,
         "delete-index": delete_index,
         "describe-index": describe_index,
         "upsert": upsert,
         "query": query}[args.command](args)
    except requests.HTTPError as e:
        fail(f"API request failed: {e.response.status_code} {e.response.text}")
    except Exception as e:
        fail(str(e))


if __name__ == "__main__":
    main()

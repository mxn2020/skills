#!/usr/bin/env python3
"""RAG Manager – OC-0118"""

import argparse
import json
import math
import os
import sys
import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

OPENAI_BASE = "https://api.openai.com/v1"
STORE_DIR = os.path.expanduser("~/.openclaw/rag")


def _key():
    k = os.environ.get("OPENAI_API_KEY")
    if not k:
        print(f"{RED}Error: OPENAI_API_KEY not set{RESET}")
        sys.exit(1)
    return k


def _embed(texts):
    resp = requests.post(
        f"{OPENAI_BASE}/embeddings",
        headers={"Authorization": f"Bearer {_key()}", "Content-Type": "application/json"},
        json={"model": "text-embedding-3-small", "input": texts},
    )
    if not resp.ok:
        print(f"{RED}Embedding error: {resp.text}{RESET}")
        sys.exit(1)
    return [d["embedding"] for d in resp.json()["data"]]


def _chunk(text, size=500):
    words = text.split()
    return [" ".join(words[i:i+size]) for i in range(0, len(words), size)]


def _store_path(collection):
    return os.path.join(STORE_DIR, f"{collection}.json")


def _load_store(collection):
    path = _store_path(collection)
    if os.path.exists(path):
        with open(path) as f:
            return json.load(f)
    return {"chunks": [], "embeddings": []}


def _save_store(collection, data):
    os.makedirs(STORE_DIR, exist_ok=True)
    with open(_store_path(collection), "w") as f:
        json.dump(data, f)


def _cosine_sim(a, b):
    dot = sum(x*y for x,y in zip(a,b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(x*x for x in b))
    return dot / (na * nb + 1e-10)


def ingest(args):
    with open(args.file) as f:
        text = f.read()
    chunks = _chunk(text, args.chunk_size)
    print(f"{YELLOW}Embedding {len(chunks)} chunks ...{RESET}")
    embeddings = _embed(chunks)
    store = _load_store(args.collection)
    store["chunks"].extend(chunks)
    store["embeddings"].extend(embeddings)
    _save_store(args.collection, store)
    print(f"{GREEN}Ingested {len(chunks)} chunks into collection '{args.collection}'{RESET}")


def query(args):
    store = _load_store(args.collection)
    if not store["chunks"]:
        print(f"{YELLOW}Collection '{args.collection}' is empty.{RESET}")
        return
    q_emb = _embed([args.text])[0]
    scored = [(i, _cosine_sim(q_emb, e)) for i, e in enumerate(store["embeddings"])]
    top = sorted(scored, key=lambda x: x[1], reverse=True)[:args.top_k]
    print(f"{GREEN}Top {args.top_k} results for: '{args.text}'{RESET}")
    for rank, (idx, score) in enumerate(top, 1):
        print(f"\n{YELLOW}[{rank}] score={score:.4f}{RESET}")
        print(store["chunks"][idx][:400])


def list_collections(args):
    os.makedirs(STORE_DIR, exist_ok=True)
    files = [f for f in os.listdir(STORE_DIR) if f.endswith(".json")]
    if not files:
        print(f"{YELLOW}No collections found.{RESET}")
        return
    print(f"{GREEN}Collections:{RESET}")
    for f in files:
        name = f[:-5]
        data = _load_store(name)
        print(f"  {name}  ({len(data['chunks'])} chunks)")


def delete_collection(args):
    path = _store_path(args.collection)
    if os.path.exists(path):
        os.remove(path)
        print(f"{GREEN}Deleted collection '{args.collection}'{RESET}")
    else:
        print(f"{YELLOW}Collection '{args.collection}' not found{RESET}")


def main():
    parser = argparse.ArgumentParser(description="RAG Manager")
    sub = parser.add_subparsers(dest="command", required=True)

    p_i = sub.add_parser("ingest")
    p_i.add_argument("--file", required=True)
    p_i.add_argument("--collection", default="default")
    p_i.add_argument("--chunk-size", type=int, default=500)

    p_q = sub.add_parser("query")
    p_q.add_argument("--text", required=True)
    p_q.add_argument("--collection", default="default")
    p_q.add_argument("--top-k", type=int, default=5)

    sub.add_parser("list-collections")

    p_d = sub.add_parser("delete-collection")
    p_d.add_argument("--collection", required=True)

    args = parser.parse_args()
    dispatch = {
        "ingest": ingest, "query": query,
        "list-collections": list_collections,
        "delete-collection": delete_collection,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()

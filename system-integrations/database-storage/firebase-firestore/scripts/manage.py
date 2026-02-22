#!/usr/bin/env python3
"""
Firebase Firestore Admin - Read/Write Firestore documents.
Uses Firestore REST API via requests with service account auth.
"""

import sys
import os
import json
import argparse
import subprocess

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://firestore.googleapis.com/v1"


def get_access_token():
    """Get access token using gcloud or service account."""
    creds_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not creds_path:
        print(f"{RED}Error: GOOGLE_APPLICATION_CREDENTIALS environment variable not set.{RESET}")
        sys.exit(1)

    try:
        result = subprocess.run(
            ["gcloud", "auth", "application-default", "print-access-token"],
            capture_output=True, text=True, timeout=15
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip()
    except FileNotFoundError:
        pass

    # Fallback: use the service account JSON directly with requests
    print(f"{YELLOW}Using service account from {creds_path}{RESET}")
    try:
        import requests
        with open(creds_path) as f:
            sa = json.load(f)

        import time
        import base64
        import hashlib
        import hmac

        # Simple JWT for Google OAuth
        header = base64.urlsafe_b64encode(json.dumps({"alg": "RS256", "typ": "JWT"}).encode()).decode().rstrip("=")
        now = int(time.time())
        claims = {
            "iss": sa["client_email"],
            "scope": "https://www.googleapis.com/auth/datastore",
            "aud": "https://oauth2.googleapis.com/token",
            "iat": now, "exp": now + 3600
        }
        payload = base64.urlsafe_b64encode(json.dumps(claims).encode()).decode().rstrip("=")

        # Sign with private key
        from hashlib import sha256
        try:
            import jwt as pyjwt
            token = pyjwt.encode(claims, sa["private_key"], algorithm="RS256",
                                 headers={"alg": "RS256", "typ": "JWT"})
        except ImportError:
            print(f"{RED}Error: Install PyJWT: pip install PyJWT{RESET}")
            sys.exit(1)

        resp = requests.post("https://oauth2.googleapis.com/token", data={
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": token
        }, timeout=15)
        return resp.json()["access_token"]
    except Exception as e:
        print(f"{RED}Error getting access token: {e}{RESET}")
        sys.exit(1)


def api_request(method, url, token, json_data=None):
    try:
        import requests
    except ImportError:
        print(f"{RED}Error: 'requests' library not installed. Run: pip install requests{RESET}")
        sys.exit(1)

    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    resp = requests.request(method, url, headers=headers, json=json_data, timeout=30)
    if resp.status_code >= 400:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.text else None


def to_firestore_value(val):
    """Convert a Python value to Firestore value format."""
    if isinstance(val, bool):
        return {"booleanValue": val}
    elif isinstance(val, int):
        return {"integerValue": str(val)}
    elif isinstance(val, float):
        return {"doubleValue": val}
    elif isinstance(val, str):
        return {"stringValue": val}
    elif isinstance(val, list):
        return {"arrayValue": {"values": [to_firestore_value(v) for v in val]}}
    elif isinstance(val, dict):
        return {"mapValue": {"fields": {k: to_firestore_value(v) for k, v in val.items()}}}
    return {"nullValue": None}


def from_firestore_fields(fields):
    """Convert Firestore fields to simple dict."""
    result = {}
    for k, v in fields.items():
        if "stringValue" in v:
            result[k] = v["stringValue"]
        elif "integerValue" in v:
            result[k] = int(v["integerValue"])
        elif "doubleValue" in v:
            result[k] = v["doubleValue"]
        elif "booleanValue" in v:
            result[k] = v["booleanValue"]
        elif "mapValue" in v:
            result[k] = from_firestore_fields(v["mapValue"].get("fields", {}))
        else:
            result[k] = str(v)
    return result


def list_collections(project):
    token = get_access_token()
    print(f"{YELLOW}Listing collections for '{project}'...{RESET}")
    url = f"{BASE_URL}/projects/{project}/databases/(default)/documents:listCollectionIds"
    data = api_request("POST", url, token, json_data={})
    ids = data.get("collectionIds", [])
    print(f"{GREEN}Found {len(ids)} collections:{RESET}")
    for cid in ids:
        print(f"  {cid}")


def get_doc(project, collection, doc):
    token = get_access_token()
    print(f"{YELLOW}Getting {collection}/{doc}...{RESET}")
    url = f"{BASE_URL}/projects/{project}/databases/(default)/documents/{collection}/{doc}"
    data = api_request("GET", url, token)
    fields = data.get("fields", {})
    print(f"{GREEN}Document {collection}/{doc}:{RESET}")
    print(f"  {json.dumps(from_firestore_fields(fields), indent=2)}")


def set_doc(project, collection, doc, data_str):
    token = get_access_token()
    print(f"{YELLOW}Setting {collection}/{doc}...{RESET}")
    parsed = json.loads(data_str)
    fields = {k: to_firestore_value(v) for k, v in parsed.items()}
    url = f"{BASE_URL}/projects/{project}/databases/(default)/documents/{collection}/{doc}"
    api_request("PATCH", url, token, json_data={"fields": fields})
    print(f"{GREEN}Document {collection}/{doc} written.{RESET}")


def delete_doc(project, collection, doc):
    token = get_access_token()
    print(f"{YELLOW}Deleting {collection}/{doc}...{RESET}")
    url = f"{BASE_URL}/projects/{project}/databases/(default)/documents/{collection}/{doc}"
    api_request("DELETE", url, token)
    print(f"{GREEN}Document {collection}/{doc} deleted.{RESET}")


def query_collection(project, collection, field, op, value, limit=20):
    token = get_access_token()
    print(f"{YELLOW}Querying {collection} where {field} {op} {value}...{RESET}")
    url = f"{BASE_URL}/projects/{project}/databases/(default)/documents:runQuery"
    body = {
        "structuredQuery": {
            "from": [{"collectionId": collection}],
            "where": {
                "fieldFilter": {
                    "field": {"fieldPath": field},
                    "op": op,
                    "value": to_firestore_value(value)
                }
            },
            "limit": limit
        }
    }
    data = api_request("POST", url, token, json_data=body)
    results = data if isinstance(data, list) else []
    docs = [r for r in results if r.get("document")]
    print(f"{GREEN}Found {len(docs)} documents:{RESET}")
    for r in docs:
        doc = r["document"]
        name = doc.get("name", "").split("/")[-1]
        fields = from_firestore_fields(doc.get("fields", {}))
        print(f"  {name}: {json.dumps(fields, default=str)}")


def main():
    parser = argparse.ArgumentParser(description="Firebase Firestore Admin")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_list = subparsers.add_parser("list-collections", help="List collections")
    p_list.add_argument("--project", required=True, help="GCP project ID")

    p_get = subparsers.add_parser("get-doc", help="Get a document")
    p_get.add_argument("--project", required=True, help="GCP project ID")
    p_get.add_argument("--collection", required=True, help="Collection name")
    p_get.add_argument("--doc", required=True, help="Document ID")

    p_set = subparsers.add_parser("set-doc", help="Set a document")
    p_set.add_argument("--project", required=True, help="GCP project ID")
    p_set.add_argument("--collection", required=True, help="Collection name")
    p_set.add_argument("--doc", required=True, help="Document ID")
    p_set.add_argument("--data", required=True, help="JSON data")

    p_del = subparsers.add_parser("delete-doc", help="Delete a document")
    p_del.add_argument("--project", required=True, help="GCP project ID")
    p_del.add_argument("--collection", required=True, help="Collection name")
    p_del.add_argument("--doc", required=True, help="Document ID")

    p_query = subparsers.add_parser("query", help="Query a collection")
    p_query.add_argument("--project", required=True, help="GCP project ID")
    p_query.add_argument("--collection", required=True, help="Collection name")
    p_query.add_argument("--field", required=True, help="Field to filter")
    p_query.add_argument("--op", required=True, help="Operator (EQUAL, LESS_THAN, etc.)")
    p_query.add_argument("--value", required=True, help="Filter value")
    p_query.add_argument("--limit", type=int, default=20, help="Max results")

    args = parser.parse_args()

    if args.command == "list-collections":
        list_collections(args.project)
    elif args.command == "get-doc":
        get_doc(args.project, args.collection, args.doc)
    elif args.command == "set-doc":
        set_doc(args.project, args.collection, args.doc, args.data)
    elif args.command == "delete-doc":
        delete_doc(args.project, args.collection, args.doc)
    elif args.command == "query":
        query_collection(args.project, args.collection, args.field, args.op, args.value, args.limit)


if __name__ == "__main__":
    main()

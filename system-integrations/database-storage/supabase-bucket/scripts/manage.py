#!/usr/bin/env python3
"""
Supabase Bucket Manager - Manage heavy media assets in Supabase Storage.
Uses Supabase Storage REST API via requests.
"""

import sys
import os
import json
import argparse

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def get_config():
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")
    if not url:
        print(f"{RED}Error: SUPABASE_URL environment variable not set.{RESET}")
        sys.exit(1)
    if not key:
        print(f"{RED}Error: SUPABASE_SERVICE_KEY environment variable not set.{RESET}")
        sys.exit(1)
    return url.rstrip("/"), key


def api_request(method, endpoint, key, base_url, params=None, json_data=None, data=None, headers_extra=None):
    try:
        import requests
    except ImportError:
        print(f"{RED}Error: 'requests' library not installed. Run: pip install requests{RESET}")
        sys.exit(1)

    headers = {"Authorization": f"Bearer {key}", "apikey": key}
    if headers_extra:
        headers.update(headers_extra)
    url = f"{base_url}/storage/v1{endpoint}"

    resp = requests.request(method, url, headers=headers, params=params, json=json_data, data=data, timeout=60)
    if resp.status_code >= 400:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp


def list_buckets():
    base_url, key = get_config()
    print(f"{YELLOW}Listing buckets...{RESET}")

    resp = api_request("GET", "/bucket", key, base_url)
    buckets = resp.json()
    print(f"{GREEN}Found {len(buckets)} buckets:{RESET}")
    for b in buckets:
        visibility = "public" if b.get("public") else "private"
        print(f"  {b['name']} [{visibility}] created={b.get('created_at', 'N/A')}")


def create_bucket(name, public=False):
    base_url, key = get_config()
    print(f"{YELLOW}Creating bucket '{name}'...{RESET}")

    body = {"id": name, "name": name, "public": public}
    api_request("POST", "/bucket", key, base_url, json_data=body)
    print(f"{GREEN}Bucket '{name}' created ({'public' if public else 'private'}).{RESET}")


def list_files(bucket, prefix="", limit=100):
    base_url, key = get_config()
    print(f"{YELLOW}Listing files in '{bucket}'...{RESET}")

    body = {"prefix": prefix, "limit": limit}
    resp = api_request("POST", f"/object/list/{bucket}", key, base_url, json_data=body)
    files = resp.json()
    print(f"{GREEN}Found {len(files)} items:{RESET}")
    for f in files:
        name = f.get("name", "N/A")
        size = f.get("metadata", {}).get("size", "N/A") if f.get("metadata") else "dir"
        print(f"  {name}  size={size}")


def upload(bucket, file_path, dest_path):
    base_url, key = get_config()
    if not os.path.isfile(file_path):
        print(f"{RED}Error: File '{file_path}' not found.{RESET}")
        sys.exit(1)

    print(f"{YELLOW}Uploading '{file_path}' to '{bucket}/{dest_path}'...{RESET}")

    with open(file_path, "rb") as f:
        file_data = f.read()

    api_request("POST", f"/object/{bucket}/{dest_path}", key, base_url,
                data=file_data, headers_extra={"Content-Type": "application/octet-stream"})
    print(f"{GREEN}Uploaded successfully.{RESET}")


def download(bucket, path, output):
    base_url, key = get_config()
    print(f"{YELLOW}Downloading '{bucket}/{path}'...{RESET}")

    resp = api_request("GET", f"/object/{bucket}/{path}", key, base_url)
    with open(output, "wb") as f:
        f.write(resp.content)
    print(f"{GREEN}Downloaded to '{output}' ({len(resp.content)} bytes).{RESET}")


def delete_file(bucket, path):
    base_url, key = get_config()
    print(f"{YELLOW}Deleting '{bucket}/{path}'...{RESET}")

    api_request("DELETE", f"/object/{bucket}", key, base_url, json_data={"prefixes": [path]})
    print(f"{GREEN}Deleted '{path}' from '{bucket}'.{RESET}")


def main():
    parser = argparse.ArgumentParser(description="Supabase Bucket Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list-buckets", help="List all buckets")

    p_create = subparsers.add_parser("create-bucket", help="Create a bucket")
    p_create.add_argument("--name", required=True, help="Bucket name")
    p_create.add_argument("--public", action="store_true", help="Make bucket public")

    p_files = subparsers.add_parser("list-files", help="List files in a bucket")
    p_files.add_argument("--bucket", required=True, help="Bucket name")
    p_files.add_argument("--prefix", default="", help="Path prefix filter")
    p_files.add_argument("--limit", type=int, default=100, help="Max results")

    p_upload = subparsers.add_parser("upload", help="Upload a file")
    p_upload.add_argument("--bucket", required=True, help="Bucket name")
    p_upload.add_argument("--file", required=True, help="Local file path")
    p_upload.add_argument("--path", required=True, help="Destination path in bucket")

    p_download = subparsers.add_parser("download", help="Download a file")
    p_download.add_argument("--bucket", required=True, help="Bucket name")
    p_download.add_argument("--path", required=True, help="File path in bucket")
    p_download.add_argument("--output", required=True, help="Local output path")

    p_delete = subparsers.add_parser("delete-file", help="Delete a file")
    p_delete.add_argument("--bucket", required=True, help="Bucket name")
    p_delete.add_argument("--path", required=True, help="File path in bucket")

    args = parser.parse_args()

    if args.command == "list-buckets":
        list_buckets()
    elif args.command == "create-bucket":
        create_bucket(args.name, args.public)
    elif args.command == "list-files":
        list_files(args.bucket, args.prefix, args.limit)
    elif args.command == "upload":
        upload(args.bucket, args.file, args.path)
    elif args.command == "download":
        download(args.bucket, args.path, args.output)
    elif args.command == "delete-file":
        delete_file(args.bucket, args.path)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""AWS S3 Bucket Explorer – OC-0013"""

import argparse
import json
import os
import subprocess
import sys

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def _run(cmd):
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"{RED}Error: {result.stderr.strip()}{RESET}")
        sys.exit(1)
    return result.stdout.strip()


def list_buckets(args):
    out = _run(["aws", "s3api", "list-buckets", "--output", "json"])
    data = json.loads(out)
    for b in data.get("Buckets", []):
        print(f"{GREEN}{b['Name']}{RESET}  created={b.get('CreationDate', 'n/a')}")


def list_objects(args):
    cmd = ["aws", "s3api", "list-objects-v2", "--bucket", args.bucket, "--output", "json"]
    if args.prefix:
        cmd += ["--prefix", args.prefix]
    if args.max_keys:
        cmd += ["--max-keys", str(args.max_keys)]
    out = _run(cmd)
    data = json.loads(out)
    for obj in data.get("Contents", []):
        size_kb = obj.get("Size", 0) / 1024
        print(f"{GREEN}{obj['Key']}{RESET}  size={size_kb:.1f}KB  modified={obj.get('LastModified', 'n/a')}")


def upload(args):
    _run(["aws", "s3", "cp", args.file, f"s3://{args.bucket}/{args.key}"])
    print(f"{GREEN}Uploaded {args.file} -> s3://{args.bucket}/{args.key}{RESET}")


def download(args):
    dest = args.output or os.path.basename(args.key)
    _run(["aws", "s3", "cp", f"s3://{args.bucket}/{args.key}", dest])
    print(f"{GREEN}Downloaded s3://{args.bucket}/{args.key} -> {dest}{RESET}")


def presign(args):
    out = _run([
        "aws", "s3", "presign",
        f"s3://{args.bucket}/{args.key}",
        "--expires-in", str(args.expires),
    ])
    print(f"{GREEN}Presigned URL (expires in {args.expires}s):{RESET}")
    print(out)


def main():
    parser = argparse.ArgumentParser(description="AWS S3 Bucket Explorer")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-buckets", help="List all buckets")

    p_obj = sub.add_parser("list-objects", help="List objects in a bucket")
    p_obj.add_argument("--bucket", required=True)
    p_obj.add_argument("--prefix", default=None)
    p_obj.add_argument("--max-keys", type=int, default=100)

    p_up = sub.add_parser("upload", help="Upload a file")
    p_up.add_argument("--bucket", required=True)
    p_up.add_argument("--key", required=True)
    p_up.add_argument("--file", required=True)

    p_dl = sub.add_parser("download", help="Download a file")
    p_dl.add_argument("--bucket", required=True)
    p_dl.add_argument("--key", required=True)
    p_dl.add_argument("--output", default=None)

    p_pre = sub.add_parser("presign", help="Generate presigned URL")
    p_pre.add_argument("--bucket", required=True)
    p_pre.add_argument("--key", required=True)
    p_pre.add_argument("--expires", type=int, default=3600)

    args = parser.parse_args()
    commands = {
        "list-buckets": list_buckets,
        "list-objects": list_objects,
        "upload": upload,
        "download": download,
        "presign": presign,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()

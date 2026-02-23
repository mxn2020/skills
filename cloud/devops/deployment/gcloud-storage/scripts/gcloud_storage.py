#!/usr/bin/env python3
"""Google Cloud Storage Manager – OC-0017"""

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


def _project():
    proj = os.environ.get("GOOGLE_CLOUD_PROJECT")
    if not proj:
        print(f"{RED}Error: GOOGLE_CLOUD_PROJECT is not set{RESET}")
        sys.exit(1)
    return proj


def list_buckets(args):
    out = _run(["gcloud", "storage", "buckets", "list", "--project", _project(), "--format", "json"])
    data = json.loads(out) if out else []
    for b in data:
        name = b.get("name", b.get("id", "n/a"))
        location = b.get("location", "n/a")
        print(f"{GREEN}{name}{RESET}  location={location}")


def list_objects(args):
    cmd = ["gcloud", "storage", "ls", f"gs://{args.bucket}"]
    if args.prefix:
        cmd[-1] += f"/{args.prefix}"
    out = _run(cmd)
    for line in out.splitlines():
        print(f"{GREEN}{line}{RESET}")


def upload(args):
    dest = f"gs://{args.bucket}/{args.dest}" if args.dest else f"gs://{args.bucket}/"
    _run(["gcloud", "storage", "cp", args.file, dest])
    print(f"{GREEN}Uploaded {args.file} -> {dest}{RESET}")


def download(args):
    src = f"gs://{args.bucket}/{args.object_path}"
    output = args.output or os.path.basename(args.object_path)
    _run(["gcloud", "storage", "cp", src, output])
    print(f"{GREEN}Downloaded {src} -> {output}{RESET}")


def set_lifecycle(args):
    _run([
        "gcloud", "storage", "buckets", "update",
        f"gs://{args.bucket}",
        f"--lifecycle-file={args.rules}",
    ])
    print(f"{GREEN}Lifecycle rules updated for gs://{args.bucket}{RESET}")


def main():
    parser = argparse.ArgumentParser(description="Google Cloud Storage Manager")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-buckets", help="List buckets")

    p_obj = sub.add_parser("list-objects", help="List objects")
    p_obj.add_argument("--bucket", required=True)
    p_obj.add_argument("--prefix", default=None)

    p_up = sub.add_parser("upload", help="Upload a file")
    p_up.add_argument("--bucket", required=True)
    p_up.add_argument("--file", required=True)
    p_up.add_argument("--dest", default=None)

    p_dl = sub.add_parser("download", help="Download a file")
    p_dl.add_argument("--bucket", required=True)
    p_dl.add_argument("--object-path", required=True)
    p_dl.add_argument("--output", default=None)

    p_lc = sub.add_parser("set-lifecycle", help="Set lifecycle rules")
    p_lc.add_argument("--bucket", required=True)
    p_lc.add_argument("--rules", required=True, help="Path to lifecycle JSON file")

    args = parser.parse_args()
    commands = {
        "list-buckets": list_buckets,
        "list-objects": list_objects,
        "upload": upload,
        "download": download,
        "set-lifecycle": set_lifecycle,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()

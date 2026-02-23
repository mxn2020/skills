#!/usr/bin/env python3
"""Fly.io App Manager – OC-0023"""

import argparse
import json
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


def list_apps(args):
    out = _run(["flyctl", "apps", "list", "--json"])
    data = json.loads(out) if out else []
    for app in data:
        status = app.get("Status", "unknown")
        color = GREEN if status == "running" else YELLOW
        print(f"{color}{status}{RESET}  {app.get('Name', 'n/a')}  org={app.get('Organization', {}).get('Slug', 'n/a')}")


def deploy(args):
    cmd = ["flyctl", "deploy", "--app", args.app]
    if args.image:
        cmd += ["--image", args.image]
    if args.region:
        cmd += ["--region", args.region]
    cmd.append("--now")
    _run(cmd)
    print(f"{GREEN}Deployment complete for {args.app}{RESET}")


def scale(args):
    cmd = ["flyctl", "scale", "count", str(args.count), "--app", args.app]
    if args.region:
        cmd += ["--region", args.region]
    _run(cmd)
    print(f"{GREEN}Scaled {args.app} to {args.count} instance(s){RESET}")

    if args.vm_size:
        _run(["flyctl", "scale", "vm", args.vm_size, "--app", args.app])
        print(f"{GREEN}VM size set to {args.vm_size}{RESET}")


def get_status(args):
    out = _run(["flyctl", "status", "--app", args.app, "--json"])
    data = json.loads(out) if out else {}
    app_name = data.get("Name", args.app)
    print(f"{GREEN}{app_name}{RESET}")
    print(f"  Status:  {data.get('Status', 'n/a')}")
    print(f"  Version: {data.get('Version', 'n/a')}")
    print(f"  Hostname: {data.get('Hostname', 'n/a')}")
    for alloc in data.get("Allocations", []):
        region = alloc.get("Region", "n/a")
        status = alloc.get("Status", "unknown")
        color = GREEN if status == "running" else YELLOW
        print(f"  {color}{status}{RESET}  id={alloc.get('IDShort', 'n/a')}  region={region}")


def list_regions(args):
    out = _run(["flyctl", "platform", "regions", "--json"])
    data = json.loads(out) if out else []
    for r in data:
        print(f"{GREEN}{r.get('Code', 'n/a')}{RESET}  {r.get('Name', 'n/a')}")


def main():
    parser = argparse.ArgumentParser(description="Fly.io App Manager")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-apps", help="List apps")

    p_deploy = sub.add_parser("deploy", help="Deploy app")
    p_deploy.add_argument("--app", required=True)
    p_deploy.add_argument("--image", default=None)
    p_deploy.add_argument("--region", default=None)

    p_scale = sub.add_parser("scale", help="Scale app")
    p_scale.add_argument("--app", required=True)
    p_scale.add_argument("--count", type=int, required=True)
    p_scale.add_argument("--vm-size", default=None)
    p_scale.add_argument("--region", default=None)

    p_status = sub.add_parser("get-status", help="Get app status")
    p_status.add_argument("--app", required=True)

    sub.add_parser("list-regions", help="List regions")

    args = parser.parse_args()
    commands = {
        "list-apps": list_apps,
        "deploy": deploy,
        "scale": scale,
        "get-status": get_status,
        "list-regions": list_regions,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()

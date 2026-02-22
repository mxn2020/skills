#!/usr/bin/env python3
"""Azure Resource Manager – OC-0021"""

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


def _subscription():
    sub = os.environ.get("AZURE_SUBSCRIPTION_ID")
    if not sub:
        print(f"{RED}Error: AZURE_SUBSCRIPTION_ID is not set{RESET}")
        sys.exit(1)
    return sub


def list_groups(args):
    out = _run([
        "az", "group", "list",
        "--subscription", _subscription(),
        "--output", "json",
    ])
    data = json.loads(out)
    for g in data:
        print(f"{GREEN}{g['name']}{RESET}  location={g.get('location')}  state={g.get('properties', {}).get('provisioningState', 'n/a')}")


def list_resources(args):
    out = _run([
        "az", "resource", "list",
        "--resource-group", args.group,
        "--subscription", _subscription(),
        "--output", "json",
    ])
    data = json.loads(out)
    for r in data:
        print(f"{GREEN}{r['name']}{RESET}  type={r.get('type')}  location={r.get('location')}")


def get_resource(args):
    out = _run([
        "az", "resource", "show",
        "--ids", args.resource_id,
        "--output", "json",
    ])
    data = json.loads(out)
    print(f"{GREEN}{data.get('name')}{RESET}")
    print(f"  Type:     {data.get('type')}")
    print(f"  Location: {data.get('location')}")
    print(f"  Kind:     {data.get('kind', 'n/a')}")
    tags = data.get("tags", {})
    if tags:
        print(f"  Tags:")
        for k, v in tags.items():
            print(f"    {k}: {v}")


def list_tags(args):
    out = _run([
        "az", "group", "show",
        "--name", args.group,
        "--subscription", _subscription(),
        "--output", "json",
    ])
    data = json.loads(out)
    tags = data.get("tags", {})
    if not tags:
        print(f"{YELLOW}No tags on resource group '{args.group}'{RESET}")
        return
    for k, v in tags.items():
        print(f"{GREEN}{k}{RESET}: {v}")


def audit(args):
    out = _run([
        "az", "resource", "list",
        "--resource-group", args.group,
        "--subscription", _subscription(),
        "--output", "json",
    ])
    data = json.loads(out)
    untagged = [r for r in data if not r.get("tags")]
    if not untagged:
        print(f"{GREEN}All resources in '{args.group}' are tagged{RESET}")
        return
    print(f"{YELLOW}Found {len(untagged)} untagged resource(s) in '{args.group}':{RESET}")
    for r in untagged:
        print(f"  {RED}{r['name']}{RESET}  type={r.get('type')}")


def main():
    parser = argparse.ArgumentParser(description="Azure Resource Manager")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-groups", help="List resource groups")

    p_res = sub.add_parser("list-resources", help="List resources in a group")
    p_res.add_argument("--group", required=True)

    p_get = sub.add_parser("get-resource", help="Get resource details")
    p_get.add_argument("--resource-id", required=True)

    p_tags = sub.add_parser("list-tags", help="List tags on a group")
    p_tags.add_argument("--group", required=True)

    p_audit = sub.add_parser("audit", help="Audit untagged resources")
    p_audit.add_argument("--group", required=True)

    args = parser.parse_args()
    commands = {
        "list-groups": list_groups,
        "list-resources": list_resources,
        "get-resource": get_resource,
        "list-tags": list_tags,
        "audit": audit,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()

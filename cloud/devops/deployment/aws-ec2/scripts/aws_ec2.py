#!/usr/bin/env python3
"""AWS EC2 Instance Control – OC-0014"""

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


def _get_name(tags):
    for t in (tags or []):
        if t.get("Key") == "Name":
            return t.get("Value", "")
    return ""


def list_instances(args):
    out = _run(["aws", "ec2", "describe-instances", "--output", "json"])
    data = json.loads(out)
    for res in data.get("Reservations", []):
        for inst in res.get("Instances", []):
            state = inst.get("State", {}).get("Name", "unknown")
            name = _get_name(inst.get("Tags"))
            color = GREEN if state == "running" else YELLOW if state == "stopped" else RED
            print(f"{color}{state}{RESET}  {inst['InstanceId']}  {name}  type={inst.get('InstanceType')}")


def start(args):
    _run(["aws", "ec2", "start-instances", "--instance-ids", args.instance_id])
    print(f"{GREEN}Starting instance {args.instance_id}{RESET}")


def stop(args):
    _run(["aws", "ec2", "stop-instances", "--instance-ids", args.instance_id])
    print(f"{YELLOW}Stopping instance {args.instance_id}{RESET}")


def get_status(args):
    out = _run([
        "aws", "ec2", "describe-instance-status",
        "--instance-ids", args.instance_id, "--output", "json",
    ])
    data = json.loads(out)
    for s in data.get("InstanceStatuses", []):
        inst_status = s.get("InstanceStatus", {}).get("Status", "n/a")
        sys_status = s.get("SystemStatus", {}).get("Status", "n/a")
        print(f"{GREEN}{s['InstanceId']}{RESET}")
        print(f"  Instance status: {inst_status}")
        print(f"  System status:   {sys_status}")
        print(f"  State:           {s.get('InstanceState', {}).get('Name', 'n/a')}")


def describe(args):
    out = _run([
        "aws", "ec2", "describe-instances",
        "--instance-ids", args.instance_id, "--output", "json",
    ])
    data = json.loads(out)
    for res in data.get("Reservations", []):
        for inst in res.get("Instances", []):
            name = _get_name(inst.get("Tags"))
            print(f"{GREEN}{name or inst['InstanceId']}{RESET}")
            print(f"  ID:       {inst['InstanceId']}")
            print(f"  Type:     {inst.get('InstanceType')}")
            print(f"  State:    {inst.get('State', {}).get('Name')}")
            print(f"  AZ:       {inst.get('Placement', {}).get('AvailabilityZone')}")
            print(f"  Public:   {inst.get('PublicIpAddress', 'n/a')}")
            print(f"  Private:  {inst.get('PrivateIpAddress', 'n/a')}")
            print(f"  Key:      {inst.get('KeyName', 'n/a')}")


def main():
    parser = argparse.ArgumentParser(description="AWS EC2 Instance Control")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-instances", help="List instances")

    p_start = sub.add_parser("start", help="Start instance")
    p_start.add_argument("--instance-id", required=True)

    p_stop = sub.add_parser("stop", help="Stop instance")
    p_stop.add_argument("--instance-id", required=True)

    p_status = sub.add_parser("get-status", help="Get instance status")
    p_status.add_argument("--instance-id", required=True)

    p_desc = sub.add_parser("describe", help="Describe instance")
    p_desc.add_argument("--instance-id", required=True)

    args = parser.parse_args()
    commands = {
        "list-instances": list_instances,
        "start": start,
        "stop": stop,
        "get-status": get_status,
        "describe": describe,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()

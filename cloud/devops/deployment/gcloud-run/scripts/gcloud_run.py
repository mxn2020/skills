#!/usr/bin/env python3
"""Google Cloud Run Deployer – OC-0016"""

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


def list_services(args):
    out = _run([
        "gcloud", "run", "services", "list",
        "--project", _project(), "--region", args.region,
        "--format", "json",
    ])
    data = json.loads(out) if out else []
    for svc in data:
        meta = svc.get("metadata", {})
        status = svc.get("status", {})
        url = status.get("url", "n/a")
        print(f"{GREEN}{meta.get('name')}{RESET}  url={url}")


def deploy(args):
    cmd = [
        "gcloud", "run", "deploy", args.service,
        "--image", args.image,
        "--project", _project(),
        "--region", args.region,
        "--quiet",
    ]
    if args.allow_unauthenticated:
        cmd.append("--allow-unauthenticated")
    if args.port:
        cmd += ["--port", str(args.port)]
    _run(cmd)
    print(f"{GREEN}Deployed {args.service} with image {args.image}{RESET}")


def describe(args):
    out = _run([
        "gcloud", "run", "services", "describe", args.service,
        "--project", _project(), "--region", args.region,
        "--format", "json",
    ])
    data = json.loads(out)
    meta = data.get("metadata", {})
    status = data.get("status", {})
    print(f"{GREEN}{meta.get('name')}{RESET}")
    print(f"  URL:      {status.get('url', 'n/a')}")
    print(f"  Created:  {meta.get('creationTimestamp', 'n/a')}")
    conditions = status.get("conditions", [])
    for c in conditions:
        print(f"  {c.get('type')}: {c.get('status')}")


def set_env(args):
    env_str = ",".join(f"{k}={v}" for k, v in [e.split("=", 1) for e in args.env_vars])
    _run([
        "gcloud", "run", "services", "update", args.service,
        "--update-env-vars", env_str,
        "--project", _project(), "--region", args.region, "--quiet",
    ])
    print(f"{GREEN}Environment variables updated for {args.service}{RESET}")


def get_logs(args):
    cmd = [
        "gcloud", "logging", "read",
        f'resource.type="cloud_run_revision" AND resource.labels.service_name="{args.service}"',
        "--project", _project(),
        "--limit", str(args.limit),
        "--format", "json",
    ]
    out = _run(cmd)
    data = json.loads(out) if out else []
    for entry in data:
        ts = entry.get("timestamp", "")
        msg = entry.get("textPayload", entry.get("jsonPayload", {}).get("message", ""))
        print(f"{YELLOW}{ts}{RESET} {msg}")


def main():
    parser = argparse.ArgumentParser(description="Google Cloud Run Deployer")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list-services", help="List services")
    p_list.add_argument("--region", default="us-central1")

    p_deploy = sub.add_parser("deploy", help="Deploy service")
    p_deploy.add_argument("--service", required=True)
    p_deploy.add_argument("--image", required=True)
    p_deploy.add_argument("--region", default="us-central1")
    p_deploy.add_argument("--allow-unauthenticated", action="store_true")
    p_deploy.add_argument("--port", type=int, default=None)

    p_desc = sub.add_parser("describe", help="Describe service")
    p_desc.add_argument("--service", required=True)
    p_desc.add_argument("--region", default="us-central1")

    p_env = sub.add_parser("set-env", help="Set env vars")
    p_env.add_argument("--service", required=True)
    p_env.add_argument("--region", default="us-central1")
    p_env.add_argument("--env-vars", nargs="+", required=True, help="KEY=VALUE pairs")

    p_logs = sub.add_parser("get-logs", help="Get service logs")
    p_logs.add_argument("--service", required=True)
    p_logs.add_argument("--limit", type=int, default=50)

    args = parser.parse_args()
    commands = {
        "list-services": list_services,
        "deploy": deploy,
        "describe": describe,
        "set-env": set_env,
        "get-logs": get_logs,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()

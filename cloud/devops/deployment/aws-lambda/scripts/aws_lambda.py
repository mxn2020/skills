#!/usr/bin/env python3
"""AWS Lambda Invoker – OC-0015"""

import argparse
import json
import os
import subprocess
import sys
import tempfile

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


def list_functions(args):
    out = _run(["aws", "lambda", "list-functions", "--output", "json"])
    data = json.loads(out)
    for fn in data.get("Functions", []):
        runtime = fn.get("Runtime", "n/a")
        print(f"{GREEN}{fn['FunctionName']}{RESET}  runtime={runtime}  memory={fn.get('MemorySize')}MB")


def invoke(args):
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        cmd = [
            "aws", "lambda", "invoke",
            "--function-name", args.function_name,
            "--output", "json",
            tmp_path,
        ]
        if args.payload:
            cmd += ["--payload", args.payload]
        out = _run(cmd)
        meta = json.loads(out)
        with open(tmp_path) as f:
            response = f.read()
        status = meta.get("StatusCode", "n/a")
        color = GREEN if status == 200 else YELLOW
        print(f"{color}Status: {status}{RESET}")
        print(f"Response: {response}")
    finally:
        os.unlink(tmp_path)


def get_logs(args):
    log_group = f"/aws/lambda/{args.function_name}"
    out = _run([
        "aws", "logs", "describe-log-streams",
        "--log-group-name", log_group,
        "--order-by", "LastEventTime",
        "--descending", "--limit", "1", "--output", "json",
    ])
    data = json.loads(out)
    streams = data.get("logStreams", [])
    if not streams:
        print(f"{YELLOW}No log streams found{RESET}")
        return
    stream_name = streams[0]["logStreamName"]
    out = _run([
        "aws", "logs", "get-log-events",
        "--log-group-name", log_group,
        "--log-stream-name", stream_name,
        "--limit", str(args.limit), "--output", "json",
    ])
    events = json.loads(out).get("events", [])
    for ev in events:
        print(f"{YELLOW}{ev.get('timestamp', '')}{RESET} {ev.get('message', '').rstrip()}")


def get_function(args):
    out = _run(["aws", "lambda", "get-function", "--function-name", args.function_name, "--output", "json"])
    data = json.loads(out)
    cfg = data.get("Configuration", {})
    print(f"{GREEN}{cfg.get('FunctionName')}{RESET}")
    print(f"  Runtime:  {cfg.get('Runtime')}")
    print(f"  Handler:  {cfg.get('Handler')}")
    print(f"  Memory:   {cfg.get('MemorySize')}MB")
    print(f"  Timeout:  {cfg.get('Timeout')}s")
    print(f"  Modified: {cfg.get('LastModified')}")


def update_code(args):
    _run([
        "aws", "lambda", "update-function-code",
        "--function-name", args.function_name,
        "--zip-file", f"fileb://{args.zip_file}",
    ])
    print(f"{GREEN}Code updated for {args.function_name}{RESET}")


def main():
    parser = argparse.ArgumentParser(description="AWS Lambda Invoker")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("list-functions", help="List functions")

    p_invoke = sub.add_parser("invoke", help="Invoke function")
    p_invoke.add_argument("--function-name", required=True)
    p_invoke.add_argument("--payload", default=None)

    p_logs = sub.add_parser("get-logs", help="Get function logs")
    p_logs.add_argument("--function-name", required=True)
    p_logs.add_argument("--limit", type=int, default=50)

    p_get = sub.add_parser("get-function", help="Get function config")
    p_get.add_argument("--function-name", required=True)

    p_update = sub.add_parser("update-code", help="Update function code")
    p_update.add_argument("--function-name", required=True)
    p_update.add_argument("--zip-file", required=True)

    args = parser.parse_args()
    commands = {
        "list-functions": list_functions,
        "invoke": invoke,
        "get-logs": get_logs,
        "get-function": get_function,
        "update-code": update_code,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()

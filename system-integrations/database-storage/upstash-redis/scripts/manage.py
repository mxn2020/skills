#!/usr/bin/env python3
"""
Upstash Redis CLI - Use serverless Redis for key-value jobs.
Uses Upstash Redis REST API via requests.
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
    url = os.environ.get("UPSTASH_REDIS_URL")
    token = os.environ.get("UPSTASH_REDIS_TOKEN")
    if not url:
        print(f"{RED}Error: UPSTASH_REDIS_URL environment variable not set.{RESET}")
        sys.exit(1)
    if not token:
        print(f"{RED}Error: UPSTASH_REDIS_TOKEN environment variable not set.{RESET}")
        sys.exit(1)
    return url.rstrip("/"), token


def redis_command(cmd_parts):
    """Execute a Redis command via Upstash REST API."""
    try:
        import requests
    except ImportError:
        print(f"{RED}Error: 'requests' library not installed. Run: pip install requests{RESET}")
        sys.exit(1)

    url, token = get_config()
    headers = {"Authorization": f"Bearer {token}"}

    resp = requests.post(url, headers=headers, json=cmd_parts, timeout=15)
    if resp.status_code >= 400:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)

    data = resp.json()
    if data.get("error"):
        print(f"{RED}Redis error: {data['error']}{RESET}")
        sys.exit(1)
    return data.get("result")


def cmd_get(key):
    print(f"{YELLOW}GET {key}{RESET}")
    result = redis_command(["GET", key])
    if result is None:
        print(f"{YELLOW}(nil){RESET}")
    else:
        print(f"{GREEN}{result}{RESET}")


def cmd_set(key, value, ex=None):
    parts = ["SET", key, value]
    if ex:
        parts.extend(["EX", str(ex)])
    print(f"{YELLOW}SET {key}{RESET}")
    redis_command(parts)
    print(f"{GREEN}OK{RESET}")


def cmd_del(key):
    print(f"{YELLOW}DEL {key}{RESET}")
    result = redis_command(["DEL", key])
    print(f"{GREEN}Deleted {result} key(s).{RESET}")


def cmd_keys(pattern="*"):
    print(f"{YELLOW}KEYS {pattern}{RESET}")
    result = redis_command(["KEYS", pattern])
    if not result:
        print(f"{YELLOW}No keys found.{RESET}")
        return
    print(f"{GREEN}Found {len(result)} keys:{RESET}")
    for k in result:
        print(f"  {k}")


def cmd_info():
    print(f"{YELLOW}INFO{RESET}")
    result = redis_command(["INFO"])
    if result:
        print(f"{GREEN}{result}{RESET}")
    else:
        print(f"{YELLOW}No info returned.{RESET}")


def cmd_ttl(key):
    print(f"{YELLOW}TTL {key}{RESET}")
    result = redis_command(["TTL", key])
    if result == -1:
        print(f"{GREEN}Key has no expiration.{RESET}")
    elif result == -2:
        print(f"{RED}Key does not exist.{RESET}")
    else:
        print(f"{GREEN}{result} seconds remaining.{RESET}")


def cmd_expire(key, seconds):
    print(f"{YELLOW}EXPIRE {key} {seconds}{RESET}")
    result = redis_command(["EXPIRE", key, str(seconds)])
    if result == 1:
        print(f"{GREEN}Expiration set to {seconds}s.{RESET}")
    else:
        print(f"{RED}Key does not exist.{RESET}")


def main():
    parser = argparse.ArgumentParser(description="Upstash Redis CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    p_get = subparsers.add_parser("get", help="Get a key")
    p_get.add_argument("--key", required=True, help="Key name")

    p_set = subparsers.add_parser("set", help="Set a key")
    p_set.add_argument("--key", required=True, help="Key name")
    p_set.add_argument("--value", required=True, help="Value")
    p_set.add_argument("--ex", type=int, help="Expiration in seconds")

    p_del = subparsers.add_parser("del", help="Delete a key")
    p_del.add_argument("--key", required=True, help="Key name")

    p_keys = subparsers.add_parser("keys", help="List keys")
    p_keys.add_argument("--pattern", default="*", help="Glob pattern")

    subparsers.add_parser("info", help="Server info")

    p_ttl = subparsers.add_parser("ttl", help="Get TTL")
    p_ttl.add_argument("--key", required=True, help="Key name")

    p_expire = subparsers.add_parser("expire", help="Set expiration")
    p_expire.add_argument("--key", required=True, help="Key name")
    p_expire.add_argument("--seconds", required=True, type=int, help="TTL in seconds")

    args = parser.parse_args()

    if args.command == "get":
        cmd_get(args.key)
    elif args.command == "set":
        cmd_set(args.key, args.value, args.ex)
    elif args.command == "del":
        cmd_del(args.key)
    elif args.command == "keys":
        cmd_keys(args.pattern)
    elif args.command == "info":
        cmd_info()
    elif args.command == "ttl":
        cmd_ttl(args.key)
    elif args.command == "expire":
        cmd_expire(args.key, args.seconds)


if __name__ == "__main__":
    main()

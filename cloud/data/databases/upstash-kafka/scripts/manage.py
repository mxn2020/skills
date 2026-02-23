#!/usr/bin/env python3
"""
Upstash Kafka Producer - Send events to serverless Kafka topics.
Uses Upstash Kafka REST API via requests.
"""

import sys
import os
import json
import argparse
import base64

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"


def get_config():
    url = os.environ.get("UPSTASH_KAFKA_URL")
    username = os.environ.get("UPSTASH_KAFKA_USERNAME")
    password = os.environ.get("UPSTASH_KAFKA_PASSWORD")
    if not url:
        print(f"{RED}Error: UPSTASH_KAFKA_URL environment variable not set.{RESET}")
        sys.exit(1)
    if not username or not password:
        print(f"{RED}Error: UPSTASH_KAFKA_USERNAME and UPSTASH_KAFKA_PASSWORD must be set.{RESET}")
        sys.exit(1)
    return url.rstrip("/"), username, password


def api_request(method, endpoint, params=None, json_data=None):
    try:
        import requests
    except ImportError:
        print(f"{RED}Error: 'requests' library not installed. Run: pip install requests{RESET}")
        sys.exit(1)

    url, username, password = get_config()
    creds = base64.b64encode(f"{username}:{password}".encode()).decode()
    headers = {"Authorization": f"Basic {creds}", "Content-Type": "application/json"}

    resp = requests.request(method, f"{url}{endpoint}", headers=headers, params=params, json=json_data, timeout=30)
    if resp.status_code >= 400:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.text else None


def list_topics():
    print(f"{YELLOW}Listing Kafka topics...{RESET}")
    data = api_request("GET", "/topics")
    topics = data if isinstance(data, list) else data.get("topics", [])
    print(f"{GREEN}Found {len(topics)} topics:{RESET}")
    for t in topics:
        if isinstance(t, str):
            print(f"  {t}")
        else:
            print(f"  {t.get('name', 'N/A')}  partitions={t.get('num_partitions', 'N/A')}")


def produce(topic, message, key=None):
    print(f"{YELLOW}Producing to '{topic}'...{RESET}")
    body = {"topic": topic, "value": message}
    if key:
        body["key"] = key
    data = api_request("POST", f"/produce/{topic}", json_data=body)
    print(f"{GREEN}Message produced:{RESET}")
    print(f"  Topic:     {topic}")
    print(f"  Offset:    {data.get('offset', 'N/A')}")
    print(f"  Partition: {data.get('partition', 'N/A')}")


def consume(topic, group, instance, timeout=5000):
    print(f"{YELLOW}Consuming from '{topic}' (group={group})...{RESET}")
    data = api_request("GET", f"/consume/{group}/{instance}/{topic}", params={"timeout": timeout})
    messages = data if isinstance(data, list) else []
    if not messages:
        print(f"{YELLOW}No messages available.{RESET}")
        return
    print(f"{GREEN}Received {len(messages)} messages:{RESET}")
    for m in messages:
        val = m.get("value", "")
        # Try to decode base64 value
        try:
            val = base64.b64decode(val).decode()
        except Exception:
            pass
        print(f"  [{m.get('offset', '?')}] key={m.get('key', 'N/A')} value={val}")


def create_topic(name, partitions=1, retention_ms=604800000):
    print(f"{YELLOW}Creating topic '{name}'...{RESET}")
    body = {"name": name, "partitions": partitions, "retention_time": retention_ms}
    data = api_request("POST", "/topic", json_data=body)
    print(f"{GREEN}Topic '{name}' created with {partitions} partition(s).{RESET}")


def get_topic(topic):
    print(f"{YELLOW}Getting topic '{topic}'...{RESET}")
    data = api_request("GET", f"/topic/{topic}")
    print(f"{GREEN}Topic: {topic}{RESET}")
    if isinstance(data, dict):
        print(f"  Partitions:  {data.get('num_partitions', 'N/A')}")
        print(f"  Retention:   {data.get('retention_time', 'N/A')}ms")
        print(f"  Max Message: {data.get('max_message_size', 'N/A')} bytes")


def main():
    parser = argparse.ArgumentParser(description="Upstash Kafka Producer")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list-topics", help="List all topics")

    p_produce = subparsers.add_parser("produce", help="Produce a message")
    p_produce.add_argument("--topic", required=True, help="Topic name")
    p_produce.add_argument("--message", required=True, help="Message body")
    p_produce.add_argument("--key", help="Message key")

    p_consume = subparsers.add_parser("consume", help="Consume messages")
    p_consume.add_argument("--topic", required=True, help="Topic name")
    p_consume.add_argument("--group", required=True, help="Consumer group name")
    p_consume.add_argument("--instance", required=True, help="Consumer instance name")
    p_consume.add_argument("--timeout", type=int, default=5000, help="Timeout in ms")

    p_create = subparsers.add_parser("create-topic", help="Create a topic")
    p_create.add_argument("--name", required=True, help="Topic name")
    p_create.add_argument("--partitions", type=int, default=1, help="Partitions")
    p_create.add_argument("--retention-ms", type=int, default=604800000, help="Retention in ms")

    p_get = subparsers.add_parser("get-topic", help="Get topic details")
    p_get.add_argument("--topic", required=True, help="Topic name")

    args = parser.parse_args()

    if args.command == "list-topics":
        list_topics()
    elif args.command == "produce":
        produce(args.topic, args.message, args.key)
    elif args.command == "consume":
        consume(args.topic, args.group, args.instance, args.timeout)
    elif args.command == "create-topic":
        create_topic(args.name, args.partitions, args.retention_ms)
    elif args.command == "get-topic":
        get_topic(args.topic)


if __name__ == "__main__":
    main()

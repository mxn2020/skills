#!/usr/bin/env python3
"""MQTT Publisher - Publish and subscribe to MQTT topics for IoT messaging. OC-0166"""

import argparse
import json
import os
import sys
import time

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BROKER_HOST = os.environ.get("MQTT_BROKER_HOST", "")
BROKER_PORT = int(os.environ.get("MQTT_PORT", "1883"))
MQTT_USER = os.environ.get("MQTT_USERNAME", "")
MQTT_PASS = os.environ.get("MQTT_PASSWORD", "")


def fail(msg):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def success(msg):
    print(f"{GREEN}{msg}{RESET}")


def warn(msg):
    print(f"{YELLOW}{msg}{RESET}")


def _get_client():
    try:
        import paho.mqtt.client as mqtt
    except ImportError:
        fail("paho-mqtt is not installed. Run: pip install paho-mqtt")
    if not BROKER_HOST:
        fail("MQTT_BROKER_HOST environment variable is required.")
    client = mqtt.Client()
    if MQTT_USER:
        client.username_pw_set(MQTT_USER, MQTT_PASS)
    return client, mqtt


def publish(args):
    client, _ = _get_client()
    print(f"{YELLOW}Connecting to {BROKER_HOST}:{BROKER_PORT}...{RESET}")
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=10)
    retain = getattr(args, "retain", False)
    qos = args.qos if args.qos is not None else 0
    result = client.publish(args.topic, args.payload, qos=qos, retain=retain)
    result.wait_for_publish()
    client.disconnect()
    success(f"Published to '{args.topic}' (QoS={qos}, retain={retain}): {args.payload}")


def subscribe_once(args):
    client, mqtt = _get_client()
    received = []
    timeout = args.timeout if args.timeout else 10

    def on_message(c, userdata, msg):
        received.append(msg)

    def on_connect(c, userdata, flags, rc):
        if rc == 0:
            c.subscribe(args.topic)
            success(f"Subscribed to '{args.topic}', waiting up to {timeout}s...")
        else:
            fail(f"Connection failed with code {rc}")

    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=60)
    client.loop_start()
    start = time.time()
    while not received and (time.time() - start) < timeout:
        time.sleep(0.1)
    client.loop_stop()
    client.disconnect()
    if received:
        msg = received[0]
        print(f"\n{GREEN}Received message:{RESET}")
        print(f"  Topic:   {msg.topic}")
        print(f"  Payload: {msg.payload.decode('utf-8', errors='replace')}")
        print(f"  QoS:     {msg.qos}")
    else:
        warn(f"No message received on '{args.topic}' within {timeout}s.")


def publish_batch(args):
    if not os.path.exists(args.file):
        fail(f"File not found: {args.file}")
    with open(args.file) as f:
        messages = json.load(f)
    if not isinstance(messages, list):
        fail("--file must contain a JSON array of {topic, payload} objects.")
    client, _ = _get_client()
    print(f"{YELLOW}Connecting to {BROKER_HOST}:{BROKER_PORT}...{RESET}")
    client.connect(BROKER_HOST, BROKER_PORT, keepalive=10)
    client.loop_start()
    ok = 0
    for i, item in enumerate(messages):
        topic = item.get("topic")
        payload = item.get("payload", "")
        if not topic:
            warn(f"  Item {i}: missing 'topic', skipping.")
            continue
        if not isinstance(payload, str):
            payload = json.dumps(payload)
        client.publish(topic, payload, qos=item.get("qos", 0))
        print(f"  {GREEN}Published{RESET} [{i+1}/{len(messages)}] {topic}: {str(payload)[:60]}")
        ok += 1
    time.sleep(0.5)
    client.loop_stop()
    client.disconnect()
    success(f"Batch complete: {ok}/{len(messages)} messages published.")


def test_connection(args):
    client, _ = _get_client()
    connected = []

    def on_connect(c, userdata, flags, rc):
        connected.append(rc)

    client.on_connect = on_connect
    print(f"{YELLOW}Testing connection to {BROKER_HOST}:{BROKER_PORT}...{RESET}")
    try:
        client.connect(BROKER_HOST, BROKER_PORT, keepalive=5)
        client.loop_start()
        time.sleep(2)
        client.loop_stop()
        client.disconnect()
    except Exception as e:
        fail(f"Connection failed: {e}")
    if connected and connected[0] == 0:
        success(f"Successfully connected to broker at {BROKER_HOST}:{BROKER_PORT}")
        if MQTT_USER:
            print(f"  Authenticated as: {MQTT_USER}")
    else:
        rc = connected[0] if connected else "no response"
        fail(f"Connection refused (rc={rc}). Check credentials and broker settings.")


def list_topics(args):
    prefix = args.prefix_filter or ""
    warn("Note: MQTT does not natively support topic listing — brokers do not expose a topic directory.")
    print(f"\n{YELLOW}To discover topics on your broker, try subscribing to a wildcard:{RESET}")
    wildcard = f"{prefix}#" if prefix else "#"
    print(f"  python3 scripts/mqtt_publisher.py subscribe-once --topic '{wildcard}' --timeout 30")
    print(f"\n{YELLOW}Common patterns for brokers that support $SYS:{RESET}")
    print(f"  Subscribe to '$SYS/#' for broker statistics and connected client info.")
    print(f"\nBroker: {BROKER_HOST}:{BROKER_PORT}")


def main():
    parser = argparse.ArgumentParser(description="MQTT Publisher CLI (OC-0166)")
    sub = parser.add_subparsers(dest="command")

    p_pub = sub.add_parser("publish", help="Publish a message to a topic")
    p_pub.add_argument("--topic", required=True)
    p_pub.add_argument("--payload", required=True)
    p_pub.add_argument("--qos", type=int, choices=[0, 1, 2], default=0)
    p_pub.add_argument("--retain", action="store_true")

    p_sub = sub.add_parser("subscribe-once", help="Subscribe and get first message")
    p_sub.add_argument("--topic", required=True)
    p_sub.add_argument("--timeout", type=int, default=10)

    p_bat = sub.add_parser("publish-batch", help="Publish messages from a JSON file")
    p_bat.add_argument("--file", required=True, help="JSON array of {topic, payload} objects")

    sub.add_parser("test-connection", help="Test broker connection")

    p_lt = sub.add_parser("list-topics", help="Info on discovering broker topics")
    p_lt.add_argument("--prefix-filter", help="Topic prefix to filter")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    dispatch = {
        "publish": publish,
        "subscribe-once": subscribe_once,
        "publish-batch": publish_batch,
        "test-connection": test_connection,
        "list-topics": list_topics,
    }
    try:
        dispatch[args.command](args)
    except Exception as e:
        fail(str(e))


if __name__ == "__main__":
    main()

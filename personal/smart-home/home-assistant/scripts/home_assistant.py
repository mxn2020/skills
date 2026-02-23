#!/usr/bin/env python3
"""Home Assistant - Control and query your Home Assistant instance. OC-0165"""

import argparse
import json
import os
import sys

import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

HA_BASE_URL = os.environ.get("HA_BASE_URL", "").rstrip("/")
HA_TOKEN = os.environ.get("HA_TOKEN", "")


def fail(msg):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def success(msg):
    print(f"{GREEN}{msg}{RESET}")


def warn(msg):
    print(f"{YELLOW}{msg}{RESET}")


def _headers():
    if not HA_BASE_URL:
        fail("HA_BASE_URL environment variable is required.")
    if not HA_TOKEN:
        fail("HA_TOKEN environment variable is required.")
    return {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json",
    }


def _request(method, path, payload=None):
    url = f"{HA_BASE_URL}/api{path}"
    resp = requests.request(method, url, headers=_headers(), json=payload, timeout=15)
    resp.raise_for_status()
    if resp.text.strip():
        return resp.json()
    return {}


def list_entities(args):
    states = _request("GET", "/states")
    domain = args.domain_filter
    if domain:
        states = [s for s in states if s["entity_id"].startswith(f"{domain}.")]
    print(f"\n{GREEN}Entities{' (' + domain + ')' if domain else ''} — {len(states)} found:{RESET}\n")
    for s in states:
        state_val = s.get("state", "unknown")
        color = GREEN if state_val in ("on", "home", "playing") else YELLOW
        print(f"  {s['entity_id']:<50} {color}{state_val}{RESET}")
    print()


def get_state(args):
    if not args.entity_id:
        fail("--entity-id is required.")
    data = _request("GET", f"/states/{args.entity_id}")
    print(f"\n{GREEN}State for {args.entity_id}:{RESET}\n")
    print(f"  State:       {data.get('state', 'unknown')}")
    attrs = data.get("attributes", {})
    for k, v in list(attrs.items())[:15]:
        print(f"  {k:<30} {v}")
    print()


def call_service(args):
    if not args.domain or not args.service:
        fail("--domain and --service are required.")
    payload = {}
    if args.entity_id:
        payload["entity_id"] = args.entity_id
    if args.data_json:
        try:
            extra = json.loads(args.data_json)
            payload.update(extra)
        except json.JSONDecodeError as e:
            fail(f"Invalid --data-json: {e}")
    _request("POST", f"/services/{args.domain}/{args.service}", payload)
    success(f"Called {args.domain}.{args.service}" + (f" on {args.entity_id}" if args.entity_id else ""))


def turn_on(args):
    if not args.entity_id:
        fail("--entity-id is required.")
    _request("POST", "/services/homeassistant/turn_on", {"entity_id": args.entity_id})
    success(f"Turned ON: {args.entity_id}")


def turn_off(args):
    if not args.entity_id:
        fail("--entity-id is required.")
    _request("POST", "/services/homeassistant/turn_off", {"entity_id": args.entity_id})
    success(f"Turned OFF: {args.entity_id}")


def toggle(args):
    if not args.entity_id:
        fail("--entity-id is required.")
    _request("POST", "/services/homeassistant/toggle", {"entity_id": args.entity_id})
    success(f"Toggled: {args.entity_id}")


def list_scenes(args):
    states = _request("GET", "/states")
    scenes = [s for s in states if s["entity_id"].startswith("scene.")]
    print(f"\n{GREEN}Scenes — {len(scenes)} found:{RESET}\n")
    for s in scenes:
        name = s.get("attributes", {}).get("friendly_name", s["entity_id"])
        print(f"  {s['entity_id']:<50} {name}")
    print()


def activate_scene(args):
    if not args.scene_id:
        fail("--scene-id is required.")
    _request("POST", "/services/scene/turn_on", {"entity_id": args.scene_id})
    success(f"Activated scene: {args.scene_id}")


def main():
    parser = argparse.ArgumentParser(description="Home Assistant CLI (OC-0165)")
    sub = parser.add_subparsers(dest="command")

    p_le = sub.add_parser("list-entities", help="List all entity states")
    p_le.add_argument("--domain-filter", help="Filter by domain (light/switch/climate/...)")

    p_gs = sub.add_parser("get-state", help="Get the state of an entity")
    p_gs.add_argument("--entity-id", required=True)

    p_cs = sub.add_parser("call-service", help="Call a Home Assistant service")
    p_cs.add_argument("--domain", required=True)
    p_cs.add_argument("--service", required=True)
    p_cs.add_argument("--entity-id")
    p_cs.add_argument("--data-json", help="Extra JSON payload")

    p_on = sub.add_parser("turn-on", help="Turn on an entity")
    p_on.add_argument("--entity-id", required=True)

    p_off = sub.add_parser("turn-off", help="Turn off an entity")
    p_off.add_argument("--entity-id", required=True)

    p_tg = sub.add_parser("toggle", help="Toggle an entity")
    p_tg.add_argument("--entity-id", required=True)

    sub.add_parser("list-scenes", help="List all scenes")

    p_as = sub.add_parser("activate-scene", help="Activate a scene")
    p_as.add_argument("--scene-id", required=True)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    dispatch = {
        "list-entities": list_entities,
        "get-state": get_state,
        "call-service": call_service,
        "turn-on": turn_on,
        "turn-off": turn_off,
        "toggle": toggle,
        "list-scenes": list_scenes,
        "activate-scene": activate_scene,
    }
    try:
        dispatch[args.command](args)
    except requests.HTTPError as e:
        fail(f"HTTP {e.response.status_code}: {e.response.text[:200]}")
    except Exception as e:
        fail(str(e))


if __name__ == "__main__":
    main()

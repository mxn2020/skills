#!/usr/bin/env python3
"""
Camera Feed Analyzer — OC-0168
Describe or detect objects in a home camera snapshot using GPT-4 Vision.
"""

import os
import sys
import base64
import argparse
import requests

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

OPENAI_URL = "https://api.openai.com/v1/chat/completions"


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _get_api_key() -> str:
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        _die("OPENAI_API_KEY is not set.")
    return key


def _fetch_ha_snapshot(entity_id: str) -> bytes:
    base  = os.environ.get("HOME_ASSISTANT_URL", "")
    token = os.environ.get("HOME_ASSISTANT_TOKEN", "")
    if not base or not token:
        _die("HOME_ASSISTANT_URL and HOME_ASSISTANT_TOKEN are required.")
    url = f"{base.rstrip('/')}/api/camera_proxy/{entity_id}"
    resp = requests.get(
        url,
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    if not resp.ok:
        _die(f"Could not fetch camera snapshot: {resp.status_code}")
    return resp.content


def _encode_image(image_bytes: bytes) -> str:
    return base64.b64encode(image_bytes).decode("utf-8")


def _analyze_image(image_bytes: bytes, prompt: str) -> str:
    b64 = _encode_image(image_bytes)
    resp = requests.post(
        OPENAI_URL,
        headers={
            "Authorization": f"Bearer {_get_api_key()}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{b64}"},
                        },
                    ],
                }
            ],
            "max_tokens": 500,
        },
        timeout=60,
    )
    if not resp.ok:
        _die(f"OpenAI Vision API {resp.status_code}: {resp.text[:200]}")
    return resp.json()["choices"][0]["message"]["content"].strip()


def analyze_snapshot(entity_id: str):
    print(f"{YELLOW}Fetching snapshot from {entity_id}...{RESET}")
    image_bytes = _fetch_ha_snapshot(entity_id)
    print(f"{YELLOW}Analyzing image ({len(image_bytes):,} bytes)...{RESET}\n")

    prompt = (
        "Analyze this home security camera image. Describe:\n"
        "1. What you see (people, vehicles, animals, objects)\n"
        "2. Any unusual activity or security concerns\n"
        "3. Time of day based on lighting\n"
        "4. Overall security status (normal/alert)\n"
        "Be concise and factual."
    )
    result = _analyze_image(image_bytes, prompt)
    print(f"{BOLD}Camera Analysis — {entity_id}:{RESET}\n")
    print(result)
    print()


def detect_motion(entity_id: str):
    print(f"{YELLOW}Fetching snapshot from {entity_id}...{RESET}")
    image_bytes = _fetch_ha_snapshot(entity_id)
    print(f"{YELLOW}Detecting motion/activity...{RESET}\n")

    prompt = (
        "Analyze this camera image for motion and activity detection:\n"
        "1. Is there any movement or people/vehicles present? (Yes/No)\n"
        "2. If yes, describe what you see\n"
        "3. Is this typical (mail carrier, resident) or unusual (unfamiliar person)?  \n"
        "4. Alert level: NORMAL, MONITOR, or ALERT\n"
        "Be direct and concise."
    )
    result = _analyze_image(image_bytes, prompt)

    if "ALERT" in result.upper():
        print(f"{RED}{BOLD}⚠ ALERT DETECTED{RESET}")
    elif "MONITOR" in result.upper():
        print(f"{YELLOW}MONITOR:{RESET}")
    else:
        print(f"{GREEN}NORMAL:{RESET}")

    print(result)
    print()


def describe_scene(entity_id: str):
    print(f"{YELLOW}Fetching snapshot from {entity_id}...{RESET}")
    image_bytes = _fetch_ha_snapshot(entity_id)
    print(f"{YELLOW}Generating scene description...{RESET}\n")

    prompt = (
        "Provide a detailed, natural language description of this camera scene. "
        "Include: what area is shown (entrance, backyard, street), lighting conditions, "
        "weather if visible, any people or vehicles, and general activity level. "
        "Write as a security log entry."
    )
    result = _analyze_image(image_bytes, prompt)
    print(f"{BOLD}Scene Description:{RESET}\n")
    print(result)
    print()


def analyze_file(filepath: str, mode: str = "general"):
    if not os.path.exists(filepath):
        _die(f"File not found: {filepath}")

    with open(filepath, "rb") as f:
        image_bytes = f.read()

    print(f"{YELLOW}Analyzing {filepath} ({len(image_bytes):,} bytes)...{RESET}\n")

    prompts = {
        "general": (
            "Analyze this image. Describe what you see, identify any objects, people, "
            "or activities, and note anything that seems unusual or important."
        ),
        "security": (
            "This is a security camera image. Analyze for: people present, vehicles, "
            "unusual activity, security concerns, and provide an alert level (NORMAL/MONITOR/ALERT)."
        ),
        "detailed": (
            "Provide a comprehensive analysis of this image including: scene type, "
            "all visible objects and their positions, any text visible, lighting, "
            "time of day estimate, and any notable details."
        ),
    }
    prompt = prompts.get(mode, prompts["general"])
    result = _analyze_image(image_bytes, prompt)
    print(f"{BOLD}Image Analysis ({mode}):{RESET}\n")
    print(result)
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="camera_feed_analyzer.py",
        description="Camera Feed Analyzer — OC-0168"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("analyze-snapshot", help="Analyze HA camera snapshot")
    p.add_argument("--entity-id", required=True, help="Home Assistant camera entity ID")

    p = sub.add_parser("detect-motion", help="Detect motion/activity in snapshot")
    p.add_argument("--entity-id", required=True)

    p = sub.add_parser("describe-scene", help="Describe scene in detail")
    p.add_argument("--entity-id", required=True)

    p = sub.add_parser("analyze-file", help="Analyze a local image file")
    p.add_argument("--file", required=True, help="Path to image file")
    p.add_argument("--mode", default="general", choices=["general", "security", "detailed"])

    args = parser.parse_args()
    dispatch = {
        "analyze-snapshot": lambda: analyze_snapshot(args.entity_id),
        "detect-motion":    lambda: detect_motion(args.entity_id),
        "describe-scene":   lambda: describe_scene(args.entity_id),
        "analyze-file":     lambda: analyze_file(args.file, args.mode),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()

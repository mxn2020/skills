#!/usr/bin/env python3
"""Sound Effect Foley – OC-0103"""

import argparse
import os
import sys
import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://api.elevenlabs.io/v1"


def _headers():
    token = os.environ.get("ELEVENLABS_API_KEY")
    if not token:
        print(f"{RED}Error: ELEVENLABS_API_KEY is not set{RESET}")
        sys.exit(1)
    return {"xi-api-key": token, "Content-Type": "application/json"}


def _request(method, path, **kwargs):
    resp = getattr(requests, method)(f"{BASE_URL}{path}", headers=_headers(), **kwargs)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp


def generate(args):
    payload = {
        "text": args.text,
        "prompt_influence": args.prompt_influence,
    }
    if args.duration is not None:
        payload["duration_seconds"] = args.duration

    resp = _request("post", "/sound-generation", json=payload)
    with open(args.output, "wb") as f:
        f.write(resp.content)
    print(f"{GREEN}Saved:{RESET} {args.output}")
    print(f"  Prompt: {args.text}")
    if args.duration:
        print(f"  Duration: {args.duration}s")


def list_examples(args):
    examples = [
        ("Footsteps", "Footsteps walking on gravel path, slow rhythmic crunching"),
        ("Rain", "Heavy rain on a tin roof, steady downpour with occasional thunder"),
        ("Thunder", "Deep rolling thunder crack, distant rumble fading away"),
        ("Explosion", "Large explosion with debris, deep boom and crackling fire"),
        ("Gunshot", "Single gunshot in empty warehouse, sharp crack with echo"),
        ("Fire", "Crackling campfire, wood burning and popping"),
        ("Wind", "Howling wind through trees, leaves rustling"),
        ("Ocean", "Ocean waves crashing on rocky shore, rhythmic and powerful"),
        ("Crowd", "Busy restaurant crowd noise, muffled conversations and clinking"),
        ("Car engine", "Car engine starting and revving, mechanical rumble"),
        ("Keyboard", "Mechanical keyboard typing, rapid clacking sounds"),
        ("Notification", "Soft digital notification chime, pleasant bell tone"),
        ("Sword", "Metal sword unsheathed, sharp metallic ring"),
        ("Magic spell", "Fantasy magic spell cast, sparkling whoosh with shimmer"),
        ("Dog bark", "Large dog barking twice, deep authoritative woof"),
    ]
    print(f"{GREEN}Example sound effect prompts:{RESET}")
    print()
    for category, prompt in examples:
        print(f"{YELLOW}{category}:{RESET}")
        print(f"  {prompt}")
        print()
    print(f"{YELLOW}Tip:{RESET} Use descriptive language including material, environment, and intensity")


def main():
    parser = argparse.ArgumentParser(description="Sound Effect Foley – OC-0103")
    sub = parser.add_subparsers(dest="command", required=True)

    p_gen = sub.add_parser("generate", help="Generate a sound effect from a text prompt")
    p_gen.add_argument("--text", required=True, help="Description of the sound effect")
    p_gen.add_argument("--duration", type=float, default=None, help="Duration in seconds (0.5-22.0)")
    p_gen.add_argument("--prompt-influence", type=float, default=0.3, help="Influence of prompt (0.0-1.0)")
    p_gen.add_argument("--output", default="output.mp3")

    sub.add_parser("list-examples", help="Show example prompts for various SFX types")

    args = parser.parse_args()
    commands = {
        "generate": generate,
        "list-examples": list_examples,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()

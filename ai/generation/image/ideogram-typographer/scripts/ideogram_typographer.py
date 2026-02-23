#!/usr/bin/env python3
"""Ideogram Typographer – OC-0087"""

import argparse
import base64
import os
import sys
import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://api.ideogram.ai"

STYLE_TYPES = ["AUTO", "GENERAL", "REALISTIC", "DESIGN", "RENDER_3D", "ANIME"]
ASPECT_RATIOS = ["ASPECT_1_1", "ASPECT_16_9", "ASPECT_9_16", "ASPECT_4_3", "ASPECT_3_4"]
MODELS = ["V_2", "V_2_TURBO"]
MAGIC_PROMPT_OPTIONS = ["AUTO", "ON", "OFF"]


def _headers():
    token = os.environ.get("IDEOGRAM_API_KEY")
    if not token:
        print(f"{RED}Error: IDEOGRAM_API_KEY is not set{RESET}")
        sys.exit(1)
    return {"Api-Key": token, "Content-Type": "application/json"}


def _request(method, path, **kwargs):
    resp = getattr(requests, method)(f"{BASE_URL}{path}", headers=_headers(), **kwargs)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.content else {}


def _download(url, output_path):
    resp = requests.get(url, timeout=120)
    if not resp.ok:
        print(f"{RED}Failed to download image: {resp.status_code}{RESET}")
        sys.exit(1)
    with open(output_path, "wb") as f:
        f.write(resp.content)
    print(f"{GREEN}Saved:{RESET} {output_path}")


def generate(args):
    image_request = {
        "prompt": args.prompt,
        "aspect_ratio": args.aspect_ratio,
        "model": args.model,
        "style_type": args.style_type,
        "magic_prompt_option": args.magic_prompt,
    }
    if args.negative_prompt:
        image_request["negative_prompt"] = args.negative_prompt
    if args.seed is not None:
        image_request["seed"] = args.seed

    payload = {"image_request": image_request}
    data = _request("post", "/generate", json=payload)
    images = data.get("data", [])
    if not images:
        print(f"{RED}No images returned{RESET}")
        sys.exit(1)
    for i, img in enumerate(images):
        base, ext = os.path.splitext(args.output)
        ext = ext or ".png"
        out_path = f"{base}_{i}{ext}" if len(images) > 1 else f"{base}{ext}"
        _download(img["url"], out_path)
        if img.get("prompt"):
            print(f"{YELLOW}Prompt used:{RESET} {img['prompt']}")


def remix(args):
    if not os.path.exists(args.input):
        print(f"{RED}Error: input file '{args.input}' not found{RESET}")
        sys.exit(1)
    token = os.environ.get("IDEOGRAM_API_KEY")
    if not token:
        print(f"{RED}Error: IDEOGRAM_API_KEY is not set{RESET}")
        sys.exit(1)
    with open(args.input, "rb") as f:
        image_data = f.read()
    image_b64 = base64.b64encode(image_data).decode()
    payload = {
        "image_request": {
            "prompt": args.prompt,
            "image_weight": args.strength,
        },
        "image_file": image_b64,
    }
    resp = requests.post(
        f"{BASE_URL}/remix",
        headers={"Api-Key": token, "Content-Type": "application/json"},
        json=payload,
        timeout=60,
    )
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    data = resp.json()
    images = data.get("data", [])
    output = args.output or "remix_output.png"
    for i, img in enumerate(images):
        base, ext = os.path.splitext(output)
        out_path = f"{base}_{i}{ext}" if len(images) > 1 else output
        _download(img["url"], out_path)


def describe(args):
    if not os.path.exists(args.input):
        print(f"{RED}Error: input file '{args.input}' not found{RESET}")
        sys.exit(1)
    token = os.environ.get("IDEOGRAM_API_KEY")
    if not token:
        print(f"{RED}Error: IDEOGRAM_API_KEY is not set{RESET}")
        sys.exit(1)
    with open(args.input, "rb") as f:
        resp = requests.post(
            f"{BASE_URL}/describe",
            headers={"Api-Key": token},
            files={"image_file": (os.path.basename(args.input), f)},
            timeout=30,
        )
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    data = resp.json()
    descriptions = data.get("descriptions", [])
    print(f"{GREEN}Image descriptions:{RESET}")
    for d in descriptions:
        print(f"  {d.get('text', 'n/a')}")


def list_styles(args):
    print(f"{GREEN}Available style types:{RESET}")
    descriptions = {
        "AUTO": "Automatically select the best style",
        "GENERAL": "General purpose imagery",
        "REALISTIC": "Photorealistic images",
        "DESIGN": "Graphic design and typography-focused",
        "RENDER_3D": "3D rendered look",
        "ANIME": "Anime and illustration style",
    }
    for style in STYLE_TYPES:
        print(f"  {style:12s}  {descriptions.get(style, '')}")


def main():
    parser = argparse.ArgumentParser(description="Ideogram Typographer – OC-0087")
    sub = parser.add_subparsers(dest="command", required=True)

    p_gen = sub.add_parser("generate", help="Generate an image from a prompt")
    p_gen.add_argument("--prompt", required=True)
    p_gen.add_argument("--aspect-ratio", default="ASPECT_1_1", choices=ASPECT_RATIOS)
    p_gen.add_argument("--model", default="V_2", choices=MODELS)
    p_gen.add_argument("--style-type", default="AUTO", choices=STYLE_TYPES)
    p_gen.add_argument("--magic-prompt", default="AUTO", choices=MAGIC_PROMPT_OPTIONS)
    p_gen.add_argument("--negative-prompt", default=None)
    p_gen.add_argument("--seed", type=int, default=None)
    p_gen.add_argument("--output", default="output.png")

    p_remix = sub.add_parser("remix", help="Remix an existing image with a new prompt")
    p_remix.add_argument("--input", required=True)
    p_remix.add_argument("--prompt", required=True)
    p_remix.add_argument("--strength", type=float, default=0.5)
    p_remix.add_argument("--output", default=None)

    p_desc = sub.add_parser("describe", help="Get a text description of an image")
    p_desc.add_argument("--input", required=True)

    sub.add_parser("list-styles", help="Show available style types")

    args = parser.parse_args()
    commands = {
        "generate": generate,
        "remix": remix,
        "describe": describe,
        "list-styles": list_styles,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()

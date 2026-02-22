#!/usr/bin/env python3
"""DALL-E 3 Artist – OC-0082"""

import argparse
import base64
import json
import os
import sys
import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://api.openai.com/v1"


def _headers():
    token = os.environ.get("OPENAI_API_KEY")
    if not token:
        print(f"{RED}Error: OPENAI_API_KEY is not set{RESET}")
        sys.exit(1)
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _request(method, path, **kwargs):
    resp = getattr(requests, method)(f"{BASE_URL}{path}", headers=_headers(), **kwargs)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.content else {}


def _save_image(url_or_b64, output_path, is_b64=False):
    if is_b64:
        data = base64.b64decode(url_or_b64)
        with open(output_path, "wb") as f:
            f.write(data)
    else:
        resp = requests.get(url_or_b64, timeout=60)
        if not resp.ok:
            print(f"{RED}Failed to download image: {resp.status_code}{RESET}")
            sys.exit(1)
        with open(output_path, "wb") as f:
            f.write(resp.content)
    print(f"{GREEN}Saved:{RESET} {output_path}")


def generate(args):
    payload = {
        "model": "dall-e-3",
        "prompt": args.prompt,
        "size": args.size,
        "quality": args.quality,
        "style": args.style,
        "n": 1,
        "response_format": "url",
    }
    data = _request("post", "/images/generations", json=payload)
    images = data.get("data", [])
    if not images:
        print(f"{RED}No images returned{RESET}")
        sys.exit(1)
    image_url = images[0]["url"]
    revised_prompt = images[0].get("revised_prompt", "")
    if revised_prompt:
        print(f"{YELLOW}Revised prompt:{RESET} {revised_prompt}")
    _save_image(image_url, args.output)


def variations(args):
    if not os.path.exists(args.input):
        print(f"{RED}Error: input file '{args.input}' not found{RESET}")
        sys.exit(1)
    with open(args.input, "rb") as f:
        image_data = f.read()
    token = os.environ.get("OPENAI_API_KEY")
    if not token:
        print(f"{RED}Error: OPENAI_API_KEY is not set{RESET}")
        sys.exit(1)
    files = {"image": (os.path.basename(args.input), image_data, "image/png")}
    data_fields = {"n": str(args.n), "size": args.size, "response_format": "url", "model": "dall-e-2"}
    resp = requests.post(
        f"{BASE_URL}/images/variations",
        headers={"Authorization": f"Bearer {token}"},
        files=files,
        data=data_fields,
        timeout=60,
    )
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    result = resp.json()
    images = result.get("data", [])
    for i, img in enumerate(images):
        base, ext = os.path.splitext(args.output)
        out_path = f"{base}_{i}{ext}" if len(images) > 1 else args.output
        _save_image(img["url"], out_path)


def list_models(args):
    data = _request("get", "/models")
    dalle_models = [m for m in data.get("data", []) if "dall-e" in m["id"].lower()]
    if not dalle_models:
        print(f"{YELLOW}No DALL-E models found in response{RESET}")
        return
    print(f"{GREEN}Available DALL-E models:{RESET}")
    for m in dalle_models:
        print(f"  {m['id']}")


def main():
    parser = argparse.ArgumentParser(description="DALL-E 3 Artist – OC-0082")
    sub = parser.add_subparsers(dest="command", required=True)

    p_gen = sub.add_parser("generate", help="Generate an image from a text prompt")
    p_gen.add_argument("--prompt", required=True, help="Text prompt for image generation")
    p_gen.add_argument("--size", default="1024x1024", choices=["1024x1024", "1792x1024", "1024x1792"])
    p_gen.add_argument("--quality", default="standard", choices=["standard", "hd"])
    p_gen.add_argument("--style", default="vivid", choices=["vivid", "natural"])
    p_gen.add_argument("--output", default="output.png", help="Output file path")

    p_var = sub.add_parser("variations", help="Create variations of an existing image")
    p_var.add_argument("--input", required=True, help="Input image path (PNG)")
    p_var.add_argument("--n", type=int, default=1, choices=[1, 2, 3, 4], help="Number of variations")
    p_var.add_argument("--size", default="1024x1024", choices=["256x256", "512x512", "1024x1024"])
    p_var.add_argument("--output", default="output.png", help="Output file path")

    sub.add_parser("list-models", help="List available DALL-E models")

    args = parser.parse_args()
    commands = {
        "generate": generate,
        "variations": variations,
        "list-models": list_models,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()

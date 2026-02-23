#!/usr/bin/env python3
"""Background Remover – OC-0089"""

import argparse
import os
import sys
import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://api.remove.bg/v1.0"

SIZES = ["auto", "preview", "small", "regular", "hd", "4k"]
TYPES = ["auto", "person", "product", "animal", "car", "other"]
FORMATS = ["auto", "png", "jpg", "zip"]


def _headers():
    token = os.environ.get("REMOVEBG_API_KEY")
    if not token:
        print(f"{RED}Error: REMOVEBG_API_KEY is not set{RESET}")
        sys.exit(1)
    return {"X-Api-Key": token}


def remove(args):
    if not os.path.exists(args.input):
        print(f"{RED}Error: input file '{args.input}' not found{RESET}")
        sys.exit(1)
    headers = _headers()
    data_fields = {
        "size": args.size,
        "format": args.format,
    }
    if args.type:
        data_fields["type"] = args.type
    if args.bg_color:
        data_fields["bg_color"] = args.bg_color
    if args.crop:
        data_fields["crop"] = "true"

    with open(args.input, "rb") as f:
        resp = requests.post(
            f"{BASE_URL}/removebg",
            headers=headers,
            files={"image_file": f},
            data=data_fields,
            timeout=60,
        )
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    credits = resp.headers.get("X-Credits-Charged", "unknown")
    with open(args.output, "wb") as f:
        f.write(resp.content)
    print(f"{GREEN}Saved:{RESET} {args.output}  (credits charged: {credits})")


def bulk_remove(args):
    if not os.path.isdir(args.input_dir):
        print(f"{RED}Error: input directory '{args.input_dir}' not found{RESET}")
        sys.exit(1)
    os.makedirs(args.output_dir, exist_ok=True)
    exts = (".jpg", ".jpeg", ".png", ".webp")
    files = [f for f in os.listdir(args.input_dir) if f.lower().endswith(exts)]
    if not files:
        print(f"{YELLOW}No image files found in '{args.input_dir}'{RESET}")
        return
    print(f"{GREEN}Processing {len(files)} images...{RESET}")
    headers = _headers()
    for filename in files:
        input_path = os.path.join(args.input_dir, filename)
        base = os.path.splitext(filename)[0]
        output_path = os.path.join(args.output_dir, f"{base}_nobg.png")
        data_fields = {"size": args.size or "auto", "format": "png"}
        if args.type:
            data_fields["type"] = args.type
        with open(input_path, "rb") as f:
            resp = requests.post(
                f"{BASE_URL}/removebg",
                headers=headers,
                files={"image_file": f},
                data=data_fields,
                timeout=60,
            )
        if not resp.ok:
            print(f"{RED}  {filename}: error ({resp.status_code}){RESET}")
            continue
        with open(output_path, "wb") as f:
            f.write(resp.content)
        print(f"{GREEN}  Saved:{RESET} {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Background Remover – OC-0089")
    sub = parser.add_subparsers(dest="command", required=True)

    p_remove = sub.add_parser("remove", help="Remove background from a single image")
    p_remove.add_argument("--input", required=True)
    p_remove.add_argument("--output", default="output.png")
    p_remove.add_argument("--size", default="auto", choices=SIZES)
    p_remove.add_argument("--type", default=None, choices=TYPES)
    p_remove.add_argument("--format", default="png", choices=FORMATS)
    p_remove.add_argument("--bg-color", default=None, help="Background color hex (e.g. ffffff)")
    p_remove.add_argument("--crop", action="store_true", help="Crop to subject bounding box")

    p_bulk = sub.add_parser("bulk-remove", help="Remove backgrounds from all images in a folder")
    p_bulk.add_argument("--input-dir", required=True)
    p_bulk.add_argument("--output-dir", required=True)
    p_bulk.add_argument("--size", default=None, choices=SIZES)
    p_bulk.add_argument("--type", default=None, choices=TYPES)

    args = parser.parse_args()
    commands = {
        "remove": remove,
        "bulk-remove": bulk_remove,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()

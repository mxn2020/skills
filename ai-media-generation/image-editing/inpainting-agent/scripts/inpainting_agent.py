#!/usr/bin/env python3
"""Inpainting Agent – OC-0091"""

import argparse
import os
import sys
import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://api.stability.ai/v2beta"


def _headers():
    token = os.environ.get("STABILITY_API_KEY")
    if not token:
        print(f"{RED}Error: STABILITY_API_KEY is not set{RESET}")
        sys.exit(1)
    return {"Authorization": f"Bearer {token}"}


def _save_response(resp, output_path):
    content_type = resp.headers.get("Content-Type", "")
    if "json" in content_type:
        print(f"{YELLOW}Response JSON:{RESET} {resp.json()}")
        return
    with open(output_path, "wb") as f:
        f.write(resp.content)
    print(f"{GREEN}Saved:{RESET} {output_path}")


def _check_files(*paths):
    for path in paths:
        if not os.path.exists(path):
            print(f"{RED}Error: file '{path}' not found{RESET}")
            sys.exit(1)


def inpaint(args):
    _check_files(args.input, args.mask)
    token = os.environ.get("STABILITY_API_KEY")
    if not token:
        print(f"{RED}Error: STABILITY_API_KEY is not set{RESET}")
        sys.exit(1)
    with open(args.input, "rb") as img_f, open(args.mask, "rb") as mask_f:
        files = {
            "image": (os.path.basename(args.input), img_f),
            "mask": (os.path.basename(args.mask), mask_f),
        }
        data_fields = {"prompt": args.prompt}
        if args.negative_prompt:
            data_fields["negative_prompt"] = args.negative_prompt
        if args.seed is not None:
            data_fields["seed"] = str(args.seed)
        resp = requests.post(
            f"{BASE_URL}/stable-image/edit/inpaint",
            headers={**_headers(), "Accept": "image/*"},
            files=files,
            data=data_fields,
            timeout=120,
        )
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    output = args.output or "inpainted.png"
    _save_response(resp, output)


def erase(args):
    _check_files(args.input, args.mask)
    token = os.environ.get("STABILITY_API_KEY")
    if not token:
        print(f"{RED}Error: STABILITY_API_KEY is not set{RESET}")
        sys.exit(1)
    with open(args.input, "rb") as img_f, open(args.mask, "rb") as mask_f:
        files = {
            "image": (os.path.basename(args.input), img_f),
            "mask": (os.path.basename(args.mask), mask_f),
        }
        data_fields = {}
        if args.seed is not None:
            data_fields["seed"] = str(args.seed)
        resp = requests.post(
            f"{BASE_URL}/stable-image/edit/erase",
            headers={**_headers(), "Accept": "image/*"},
            files=files,
            data=data_fields,
            timeout=120,
        )
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    output = args.output or "erased.png"
    _save_response(resp, output)


def search_and_replace(args):
    _check_files(args.input)
    token = os.environ.get("STABILITY_API_KEY")
    if not token:
        print(f"{RED}Error: STABILITY_API_KEY is not set{RESET}")
        sys.exit(1)
    with open(args.input, "rb") as img_f:
        files = {"image": (os.path.basename(args.input), img_f)}
        data_fields = {
            "prompt": args.prompt,
            "search_prompt": args.search_prompt,
        }
        if args.seed is not None:
            data_fields["seed"] = str(args.seed)
        resp = requests.post(
            f"{BASE_URL}/stable-image/edit/search-and-replace",
            headers={**_headers(), "Accept": "image/*"},
            files=files,
            data=data_fields,
            timeout=120,
        )
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    output = args.output or "replaced.png"
    _save_response(resp, output)


def main():
    parser = argparse.ArgumentParser(description="Inpainting Agent – OC-0091")
    sub = parser.add_subparsers(dest="command", required=True)

    p_inp = sub.add_parser("inpaint", help="Fill a masked region using a text prompt")
    p_inp.add_argument("--input", required=True)
    p_inp.add_argument("--mask", required=True)
    p_inp.add_argument("--prompt", required=True)
    p_inp.add_argument("--negative-prompt", default=None)
    p_inp.add_argument("--output", default="output.png")
    p_inp.add_argument("--seed", type=int, default=None)

    p_erase = sub.add_parser("erase", help="Erase a masked region from an image")
    p_erase.add_argument("--input", required=True)
    p_erase.add_argument("--mask", required=True)
    p_erase.add_argument("--output", default=None)
    p_erase.add_argument("--seed", type=int, default=None)

    p_sar = sub.add_parser("search-and-replace", help="Find and replace an object by prompt")
    p_sar.add_argument("--input", required=True)
    p_sar.add_argument("--search-prompt", required=True, help="Description of the object to find")
    p_sar.add_argument("--prompt", required=True, help="Description of the replacement")
    p_sar.add_argument("--output", default=None)
    p_sar.add_argument("--seed", type=int, default=None)

    args = parser.parse_args()
    commands = {
        "inpaint": inpaint,
        "erase": erase,
        "search-and-replace": search_and_replace,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()

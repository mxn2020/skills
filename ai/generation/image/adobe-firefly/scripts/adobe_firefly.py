#!/usr/bin/env python3
"""Adobe Firefly – OC-0088"""

import argparse
import base64
import os
import sys
import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

FIREFLY_BASE_URL = "https://firefly-api.adobe.io"
IMS_TOKEN_URL = "https://ims-na1.adobelogin.com/ims/token/v3"


def _get_access_token():
    client_id = os.environ.get("FIREFLY_CLIENT_ID")
    client_secret = os.environ.get("FIREFLY_CLIENT_SECRET")
    if not client_id:
        print(f"{RED}Error: FIREFLY_CLIENT_ID is not set{RESET}")
        sys.exit(1)
    if not client_secret:
        print(f"{RED}Error: FIREFLY_CLIENT_SECRET is not set{RESET}")
        sys.exit(1)
    resp = requests.post(
        IMS_TOKEN_URL,
        data={
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "openid,AdobeID,firefly_api",
        },
        timeout=30,
    )
    if not resp.ok:
        print(f"{RED}Auth error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json().get("access_token"), client_id


def _headers():
    token, client_id = _get_access_token()
    return {
        "Authorization": f"Bearer {token}",
        "X-Api-Key": client_id,
        "Content-Type": "application/json",
    }


def _request(method, path, **kwargs):
    resp = getattr(requests, method)(f"{FIREFLY_BASE_URL}{path}", headers=_headers(), **kwargs)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.content else {}


def _download(url, output_path):
    resp = requests.get(url, timeout=120)
    if not resp.ok:
        print(f"{RED}Failed to download: {resp.status_code}{RESET}")
        sys.exit(1)
    with open(output_path, "wb") as f:
        f.write(resp.content)
    print(f"{GREEN}Saved:{RESET} {output_path}")


def _image_to_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def generate(args):
    payload = {
        "numVariations": args.num_variations,
        "size": {"width": args.width, "height": args.height},
        "prompt": args.prompt,
        "locale": args.locale,
    }
    if args.negative_prompt:
        payload["negativePrompt"] = args.negative_prompt
    if args.style:
        payload["styles"] = [{"presetId": args.style}]
    if args.seed is not None:
        payload["seeds"] = [args.seed]

    data = _request("post", "/v3/images/generate", json=payload)
    outputs = data.get("outputs", [])
    os.makedirs(args.output_dir, exist_ok=True)
    for i, output in enumerate(outputs):
        img_data = output.get("image", {})
        url = img_data.get("url") or img_data.get("presignedUrl")
        if url:
            out_path = os.path.join(args.output_dir, f"firefly_{i}.jpg")
            _download(url, out_path)
        else:
            print(f"{YELLOW}Output {i}: no URL found. Data: {img_data}{RESET}")


def expand(args):
    if not os.path.exists(args.input):
        print(f"{RED}Error: input file '{args.input}' not found{RESET}")
        sys.exit(1)
    payload = {
        "image": {"source": {"dataUrl": f"data:image/jpeg;base64,{_image_to_b64(args.input)}"}},
        "size": {
            "left": args.left,
            "right": args.right,
            "top": args.top,
            "bottom": args.bottom,
        },
    }
    if args.prompt:
        payload["prompt"] = args.prompt
    data = _request("post", "/v3/images/expand", json=payload)
    outputs = data.get("outputs", [])
    output_path = args.output or "expanded.jpg"
    for i, out in enumerate(outputs):
        url = out.get("image", {}).get("url") or out.get("image", {}).get("presignedUrl")
        if url:
            _download(url, output_path)
            break


def remove_background(args):
    if not os.path.exists(args.input):
        print(f"{RED}Error: input file '{args.input}' not found{RESET}")
        sys.exit(1)
    payload = {
        "image": {"source": {"dataUrl": f"data:image/jpeg;base64,{_image_to_b64(args.input)}"}},
    }
    data = _request("post", "/v3/images/remove-background", json=payload)
    outputs = data.get("outputs", [])
    output_path = args.output or "output.png"
    for out in outputs:
        url = out.get("image", {}).get("url") or out.get("image", {}).get("presignedUrl")
        if url:
            _download(url, output_path)
            break


def generative_fill(args):
    for path in [args.input, args.mask]:
        if not os.path.exists(path):
            print(f"{RED}Error: file '{path}' not found{RESET}")
            sys.exit(1)
    payload = {
        "prompt": args.prompt,
        "image": {"source": {"dataUrl": f"data:image/jpeg;base64,{_image_to_b64(args.input)}"}},
        "mask": {"source": {"dataUrl": f"data:image/png;base64,{_image_to_b64(args.mask)}"}},
    }
    data = _request("post", "/v3/images/fill", json=payload)
    outputs = data.get("outputs", [])
    output_path = args.output or "filled.jpg"
    for out in outputs:
        url = out.get("image", {}).get("url") or out.get("image", {}).get("presignedUrl")
        if url:
            _download(url, output_path)
            break


def list_styles(args):
    print(f"{GREEN}Available Adobe Firefly content styles:{RESET}")
    styles = [
        ("photo", "Photographic look"),
        ("art", "Artistic illustration"),
        ("graphic", "Graphic design"),
        ("bw", "Black and white"),
        ("sketch", "Pencil sketch"),
        ("watercolor", "Watercolor painting"),
        ("oil_paint", "Oil painting"),
        ("pixel_art", "Pixel art"),
    ]
    for style_id, desc in styles:
        print(f"  {style_id:15s}  {desc}")


def main():
    parser = argparse.ArgumentParser(description="Adobe Firefly – OC-0088")
    sub = parser.add_subparsers(dest="command", required=True)

    p_gen = sub.add_parser("generate", help="Generate images from a text prompt")
    p_gen.add_argument("--prompt", required=True)
    p_gen.add_argument("--negative-prompt", default=None)
    p_gen.add_argument("--width", type=int, default=1024)
    p_gen.add_argument("--height", type=int, default=1024)
    p_gen.add_argument("--style", default=None)
    p_gen.add_argument("--locale", default="en-US")
    p_gen.add_argument("--num-variations", type=int, default=1, choices=[1, 2, 3, 4])
    p_gen.add_argument("--seed", type=int, default=None)
    p_gen.add_argument("--output-dir", default=".")

    p_exp = sub.add_parser("expand", help="Expand image canvas with AI content")
    p_exp.add_argument("--input", required=True)
    p_exp.add_argument("--left", type=int, default=0)
    p_exp.add_argument("--right", type=int, default=0)
    p_exp.add_argument("--top", type=int, default=0)
    p_exp.add_argument("--bottom", type=int, default=0)
    p_exp.add_argument("--prompt", default=None)
    p_exp.add_argument("--output", default=None)

    p_rbg = sub.add_parser("remove-background", help="Remove background from image")
    p_rbg.add_argument("--input", required=True)
    p_rbg.add_argument("--output", default="output.png")

    p_fill = sub.add_parser("generative-fill", help="Fill masked area with generated content")
    p_fill.add_argument("--input", required=True)
    p_fill.add_argument("--mask", required=True)
    p_fill.add_argument("--prompt", required=True)
    p_fill.add_argument("--output", default=None)

    sub.add_parser("list-styles", help="List available content styles")

    args = parser.parse_args()
    commands = {
        "generate": generate,
        "expand": expand,
        "remove-background": remove_background,
        "generative-fill": generative_fill,
        "list-styles": list_styles,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Style Transfer – OC-0092"""

import argparse
import base64
import os
import sys
import time
import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://api.replicate.com/v1"
MODEL_OWNER = "fofr"
MODEL_NAME = "style-transfer"


def _headers():
    token = os.environ.get("REPLICATE_API_TOKEN")
    if not token:
        print(f"{RED}Error: REPLICATE_API_TOKEN is not set{RESET}")
        sys.exit(1)
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


def _request(method, path, **kwargs):
    resp = getattr(requests, method)(f"{BASE_URL}{path}", headers=_headers(), **kwargs)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.content else {}


def _poll_prediction(prediction_id, max_wait=300):
    print(f"{YELLOW}Polling prediction {prediction_id}...{RESET}")
    for _ in range(max_wait // 5):
        data = _request("get", f"/predictions/{prediction_id}")
        status = data.get("status", "unknown")
        if status == "succeeded":
            return data
        if status in ("failed", "canceled"):
            print(f"{RED}Prediction {status}: {data.get('error', 'Unknown error')}{RESET}")
            sys.exit(1)
        print(f"{YELLOW}  status={status}...{RESET}")
        time.sleep(5)
    print(f"{RED}Timed out waiting for prediction{RESET}")
    sys.exit(1)


def _download(url, output_path):
    resp = requests.get(url, timeout=120)
    if not resp.ok:
        print(f"{RED}Failed to download image: {resp.status_code}{RESET}")
        sys.exit(1)
    with open(output_path, "wb") as f:
        f.write(resp.content)
    print(f"{GREEN}Saved:{RESET} {output_path}")


def _image_to_data_url(path):
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}.get(ext, "image/jpeg")
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:{mime};base64,{b64}"


def transfer(args):
    for path in [args.content, args.style]:
        if not os.path.exists(path):
            print(f"{RED}Error: file '{path}' not found{RESET}")
            sys.exit(1)
    token = os.environ.get("REPLICATE_API_TOKEN")
    if not token:
        print(f"{RED}Error: REPLICATE_API_TOKEN is not set{RESET}")
        sys.exit(1)
    input_params = {
        "content_image": _image_to_data_url(args.content),
        "style_image": _image_to_data_url(args.style),
        "style_strength": args.style_strength,
    }
    if args.preserve_color:
        input_params["preserve_color"] = True
    if args.seed is not None:
        input_params["seed"] = args.seed

    resp = requests.post(
        f"{BASE_URL}/models/{MODEL_OWNER}/{MODEL_NAME}/predictions",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"input": input_params},
        timeout=30,
    )
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    prediction = resp.json()
    prediction_id = prediction.get("id")
    if not prediction_id:
        print(f"{RED}No prediction ID returned{RESET}")
        sys.exit(1)
    result = _poll_prediction(prediction_id)
    output = result.get("output")
    if isinstance(output, list):
        output = output[0]
    if output:
        _download(output, args.output)
    else:
        print(f"{YELLOW}No output URL found. Result:{RESET}")
        print(result)


def list_styles(args):
    print(f"{GREEN}Popular artistic style presets:{RESET}")
    styles = [
        ("Van Gogh", "Swirling brushstrokes, vivid colors"),
        ("Monet", "Impressionist, soft light and color"),
        ("Picasso", "Cubist, abstract geometric forms"),
        ("Hokusai", "Japanese woodblock print style"),
        ("Kandinsky", "Abstract expressionism"),
        ("Dali", "Surrealist dreamlike imagery"),
        ("Watercolor", "Soft translucent washes of color"),
        ("Pencil Sketch", "Hand-drawn pencil style"),
        ("Oil Painting", "Classic oil on canvas texture"),
        ("Anime", "Japanese anime illustration style"),
    ]
    print(f"  {'Style':<20} Description")
    print(f"  {'-'*20} {'-'*40}")
    for name, desc in styles:
        print(f"  {name:<20} {desc}")
    print()
    print(f"{YELLOW}Tip:{RESET} Use any image as the --style input for custom style transfer")


def main():
    parser = argparse.ArgumentParser(description="Style Transfer – OC-0092")
    sub = parser.add_subparsers(dest="command", required=True)

    p_transfer = sub.add_parser("transfer", help="Apply a style image to a content image")
    p_transfer.add_argument("--content", required=True, help="Content image path")
    p_transfer.add_argument("--style", required=True, help="Style image path")
    p_transfer.add_argument("--output", default="output.png")
    p_transfer.add_argument("--style-strength", type=float, default=0.5, help="Style strength (0.0-1.0)")
    p_transfer.add_argument("--preserve-color", action="store_true", help="Preserve content image colors")
    p_transfer.add_argument("--seed", type=int, default=None)

    sub.add_parser("list-styles", help="Show popular style preset descriptions")

    args = parser.parse_args()
    commands = {
        "transfer": transfer,
        "list-styles": list_styles,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()

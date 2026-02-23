#!/usr/bin/env python3
"""AI Upscaler – OC-0090"""

import argparse
import os
import sys
import time
import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://api.replicate.com/v1"
ESRGAN_MODEL = "nightmareai/real-esrgan"
ESRGAN_VERSION = "42fed1c4974146d4d2414e2be2c5277c7fcf05fcc3a73abf41610695738c1d7b"


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
    import base64
    ext = os.path.splitext(path)[1].lower().lstrip(".")
    mime = {"jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp"}.get(ext, "image/jpeg")
    with open(path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:{mime};base64,{b64}"


def _run_upscale(input_path, scale, face_enhance, output_path):
    if not os.path.exists(input_path):
        print(f"{RED}Error: input file '{input_path}' not found{RESET}")
        sys.exit(1)
    input_data_url = _image_to_data_url(input_path)
    payload = {
        "version": ESRGAN_VERSION,
        "input": {
            "image": input_data_url,
            "scale": scale,
            "face_enhance": face_enhance,
        },
    }
    data = _request("post", "/predictions", json=payload)
    prediction_id = data.get("id")
    if not prediction_id:
        print(f"{RED}No prediction ID returned{RESET}")
        sys.exit(1)
    result = _poll_prediction(prediction_id)
    output_url = result.get("output")
    if isinstance(output_url, list):
        output_url = output_url[0]
    if output_url:
        _download(output_url, output_path)
    else:
        print(f"{YELLOW}No output URL returned. Result:{RESET}")
        print(result)


def upscale(args):
    _run_upscale(args.input, args.scale, args.face_enhance, args.output)


def batch_upscale(args):
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
    for filename in files:
        input_path = os.path.join(args.input_dir, filename)
        base, ext = os.path.splitext(filename)
        output_path = os.path.join(args.output_dir, f"{base}_x{args.scale}{ext}")
        print(f"{YELLOW}  Upscaling:{RESET} {filename}")
        _run_upscale(input_path, args.scale, args.face_enhance, output_path)


def main():
    parser = argparse.ArgumentParser(description="AI Upscaler – OC-0090")
    sub = parser.add_subparsers(dest="command", required=True)

    p_up = sub.add_parser("upscale", help="Upscale a single image")
    p_up.add_argument("--input", required=True)
    p_up.add_argument("--scale", type=int, default=4, choices=[2, 4, 8])
    p_up.add_argument("--face-enhance", action="store_true", help="Apply face enhancement")
    p_up.add_argument("--output", default="output.png")

    p_batch = sub.add_parser("batch-upscale", help="Upscale all images in a directory")
    p_batch.add_argument("--input-dir", required=True)
    p_batch.add_argument("--output-dir", required=True)
    p_batch.add_argument("--scale", type=int, default=4, choices=[2, 4, 8])
    p_batch.add_argument("--face-enhance", action="store_true")

    args = parser.parse_args()
    commands = {
        "upscale": upscale,
        "batch-upscale": batch_upscale,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()

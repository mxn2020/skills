#!/usr/bin/env python3
"""Face Restoration – OC-0093"""

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
GFPGAN_MODEL = "tencentarc/gfpgan"
GFPGAN_VERSION = "9283608cc6b7be6b65a8e44983db012355fde4132009bf99d976b2f0896856a3"


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


def _run_gfpgan(input_path, scale, version, bg_upsampler, output_path):
    if not os.path.exists(input_path):
        print(f"{RED}Error: input file '{input_path}' not found{RESET}")
        sys.exit(1)
    input_params = {
        "img": _image_to_data_url(input_path),
        "scale": scale,
        "version": version,
    }
    if bg_upsampler:
        input_params["bg_upsampler"] = "realesrgan"

    payload = {"version": GFPGAN_VERSION, "input": input_params}
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
        print(f"{YELLOW}No output URL found. Result:{RESET}")
        print(result)


def restore(args):
    output = args.output or "output.png"
    _run_gfpgan(args.input, args.scale, args.version, False, output)


def enhance(args):
    output = args.output or "enhanced.png"
    _run_gfpgan(args.input, args.scale, "1.4", args.bg_upsampler, output)


def main():
    parser = argparse.ArgumentParser(description="Face Restoration – OC-0093")
    sub = parser.add_subparsers(dest="command", required=True)

    p_restore = sub.add_parser("restore", help="Restore faces using GFPGAN")
    p_restore.add_argument("--input", required=True)
    p_restore.add_argument("--output", default="output.png")
    p_restore.add_argument("--scale", type=int, default=2, choices=[1, 2, 4])
    p_restore.add_argument("--version", default="1.4", choices=["1", "1.2", "1.3", "1.4", "RestoreFormer"])

    p_enhance = sub.add_parser("enhance", help="Restore faces with optional background upsampling")
    p_enhance.add_argument("--input", required=True)
    p_enhance.add_argument("--output", default=None)
    p_enhance.add_argument("--scale", type=int, default=2, choices=[1, 2, 4])
    p_enhance.add_argument("--bg-upsampler", action="store_true", help="Use Real-ESRGAN for background")

    args = parser.parse_args()
    commands = {
        "restore": restore,
        "enhance": enhance,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()

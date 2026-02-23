#!/usr/bin/env python3
"""Stable Diffusion (SDXL) – OC-0084"""

import argparse
import base64
import os
import sys
import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://api.stability.ai/v1"


def _headers():
    token = os.environ.get("STABILITY_API_KEY")
    if not token:
        print(f"{RED}Error: STABILITY_API_KEY is not set{RESET}")
        sys.exit(1)
    return {"Authorization": f"Bearer {token}", "Accept": "application/json"}


def _request(method, path, **kwargs):
    resp = getattr(requests, method)(f"{BASE_URL}{path}", headers=_headers(), **kwargs)
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    return resp.json() if resp.content else {}


def _save_artifacts(artifacts, output_base):
    saved = []
    for i, artifact in enumerate(artifacts):
        if artifact.get("finishReason") == "ERROR":
            print(f"{RED}Artifact {i} had an error{RESET}")
            continue
        base, ext = os.path.splitext(output_base)
        ext = ext or ".png"
        out_path = f"{base}_{i}{ext}" if len(artifacts) > 1 else f"{base}{ext}"
        with open(out_path, "wb") as f:
            f.write(base64.b64decode(artifact["base64"]))
        print(f"{GREEN}Saved:{RESET} {out_path}")
        saved.append(out_path)
    return saved


def generate(args):
    payload = {
        "text_prompts": [{"text": args.prompt, "weight": 1.0}],
        "width": args.width,
        "height": args.height,
        "steps": args.steps,
        "cfg_scale": args.cfg_scale,
        "samples": args.samples,
    }
    if args.negative_prompt:
        payload["text_prompts"].append({"text": args.negative_prompt, "weight": -1.0})
    if args.seed is not None:
        payload["seed"] = args.seed

    data = _request("post", f"/generation/{args.engine}/text-to-image", json=payload)
    artifacts = data.get("artifacts", [])
    if not artifacts:
        print(f"{RED}No artifacts returned{RESET}")
        sys.exit(1)
    _save_artifacts(artifacts, args.output)


def upscale(args):
    if not os.path.exists(args.input):
        print(f"{RED}Error: input file '{args.input}' not found{RESET}")
        sys.exit(1)
    token = os.environ.get("STABILITY_API_KEY")
    if not token:
        print(f"{RED}Error: STABILITY_API_KEY is not set{RESET}")
        sys.exit(1)
    with open(args.input, "rb") as f:
        resp = requests.post(
            f"{BASE_URL}/generation/esrgan-v1-x2plus/image-to-image/upscale",
            headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
            files={"image": f},
            data={"width": args.width},
            timeout=60,
        )
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    artifacts = resp.json().get("artifacts", [])
    output = args.output or "upscaled.png"
    _save_artifacts(artifacts, output)


def inpaint(args):
    for path in [args.init_image, args.mask_image]:
        if not os.path.exists(path):
            print(f"{RED}Error: file '{path}' not found{RESET}")
            sys.exit(1)
    token = os.environ.get("STABILITY_API_KEY")
    if not token:
        print(f"{RED}Error: STABILITY_API_KEY is not set{RESET}")
        sys.exit(1)
    with open(args.init_image, "rb") as img_f, open(args.mask_image, "rb") as mask_f:
        resp = requests.post(
            f"{BASE_URL}/generation/stable-diffusion-xl-1024-v1-0/image-to-image/masking",
            headers={"Authorization": f"Bearer {token}", "Accept": "application/json"},
            files={"init_image": img_f, "mask_image": mask_f},
            data={
                "text_prompts[0][text]": args.prompt,
                "text_prompts[0][weight]": "1",
                "mask_source": "MASK_IMAGE_WHITE",
            },
            timeout=120,
        )
    if not resp.ok:
        print(f"{RED}API error ({resp.status_code}): {resp.text}{RESET}")
        sys.exit(1)
    artifacts = resp.json().get("artifacts", [])
    output = args.output or "inpainted.png"
    _save_artifacts(artifacts, output)


def list_engines(args):
    data = _request("get", "/engines/list")
    print(f"{GREEN}Available engines:{RESET}")
    for engine in data:
        ready = engine.get("ready", False)
        color = GREEN if ready else YELLOW
        print(f"  {color}{'ready' if ready else 'not ready'}{RESET}  {engine['id']}  {engine.get('name', '')}")


def main():
    parser = argparse.ArgumentParser(description="Stable Diffusion SDXL – OC-0084")
    sub = parser.add_subparsers(dest="command", required=True)

    p_gen = sub.add_parser("generate", help="Generate an image from a text prompt")
    p_gen.add_argument("--prompt", required=True)
    p_gen.add_argument("--negative-prompt", default=None)
    p_gen.add_argument("--engine", default="stable-diffusion-xl-1024-v1-0")
    p_gen.add_argument("--width", type=int, default=1024)
    p_gen.add_argument("--height", type=int, default=1024)
    p_gen.add_argument("--steps", type=int, default=30)
    p_gen.add_argument("--cfg-scale", type=float, default=7.0)
    p_gen.add_argument("--seed", type=int, default=None)
    p_gen.add_argument("--samples", type=int, default=1, choices=[1, 2, 3, 4])
    p_gen.add_argument("--output", default="output.png")

    p_up = sub.add_parser("upscale", help="Upscale an image")
    p_up.add_argument("--input", required=True)
    p_up.add_argument("--output", default=None)
    p_up.add_argument("--width", type=int, default=2048)

    p_inp = sub.add_parser("inpaint", help="Inpaint a masked region")
    p_inp.add_argument("--init-image", required=True)
    p_inp.add_argument("--mask-image", required=True)
    p_inp.add_argument("--prompt", required=True)
    p_inp.add_argument("--output", default=None)

    sub.add_parser("list-engines", help="List available engines")

    args = parser.parse_args()
    commands = {
        "generate": generate,
        "upscale": upscale,
        "inpaint": inpaint,
        "list-engines": list_engines,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()

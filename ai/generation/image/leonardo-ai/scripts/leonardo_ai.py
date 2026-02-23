#!/usr/bin/env python3
"""Leonardo.ai – OC-0086"""

import argparse
import os
import sys
import time
import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

BASE_URL = "https://cloud.leonardo.ai/api/rest/v1"
DEFAULT_MODEL_ID = "b24e16ff-06e3-43eb-8d33-4416c2d75876"  # Leonardo Diffusion XL


def _headers():
    token = os.environ.get("LEONARDO_API_KEY")
    if not token:
        print(f"{RED}Error: LEONARDO_API_KEY is not set{RESET}")
        sys.exit(1)
    return {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}


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
    payload = {
        "prompt": args.prompt,
        "modelId": args.model_id,
        "width": args.width,
        "height": args.height,
        "num_images": args.num_images,
        "guidance_scale": args.guidance_scale,
        "num_inference_steps": args.steps,
    }
    if args.negative_prompt:
        payload["negative_prompt"] = args.negative_prompt
    if args.seed is not None:
        payload["seed"] = args.seed

    data = _request("post", "/generations", json=payload)
    generation_id = data.get("sdGenerationJob", {}).get("generationId")
    if not generation_id:
        print(f"{RED}No generation ID returned{RESET}")
        sys.exit(1)
    print(f"{GREEN}Generation started:{RESET} {generation_id}")

    # Poll for completion
    print(f"{YELLOW}Waiting for generation to complete...{RESET}")
    for _ in range(60):
        time.sleep(5)
        gen_data = _request("get", f"/generations/{generation_id}")
        gen = gen_data.get("generations_by_pk", {})
        status = gen.get("status", "PENDING")
        if status == "COMPLETE":
            images = gen.get("generated_images", [])
            os.makedirs(args.output_dir, exist_ok=True)
            for i, img in enumerate(images):
                out_path = os.path.join(args.output_dir, f"image_{generation_id}_{i}.jpg")
                _download(img["url"], out_path)
            return
        if status == "FAILED":
            print(f"{RED}Generation failed{RESET}")
            sys.exit(1)
        print(f"{YELLOW}  status={status}...{RESET}")
    print(f"{RED}Timed out waiting for generation{RESET}")
    sys.exit(1)


def get_generation(args):
    data = _request("get", f"/generations/{args.generation_id}")
    gen = data.get("generations_by_pk", {})
    status = gen.get("status", "unknown")
    color = GREEN if status == "COMPLETE" else YELLOW
    print(f"{color}Status:{RESET} {status}")
    print(f"  ID: {gen.get('id', 'n/a')}")
    print(f"  Created: {gen.get('createdAt', 'n/a')}")
    images = gen.get("generated_images", [])
    for img in images:
        print(f"  Image: {img.get('url', 'n/a')}")


def list_models(args):
    data = _request("get", "/platformModels")
    models = data.get("custom_models", []) or data.get("platformModels", [])
    print(f"{GREEN}Available models:{RESET}")
    for m in models:
        print(f"  {m.get('id', 'n/a')}  {m.get('name', 'n/a')}")


def list_generations(args):
    data = _request("get", f"/generations/user/me?limit={args.limit}")
    gens = data.get("generations", [])
    print(f"{GREEN}Recent generations:{RESET}")
    for g in gens:
        status = g.get("status", "unknown")
        color = GREEN if status == "COMPLETE" else YELLOW
        print(f"  {color}{status}{RESET}  {g.get('id', 'n/a')}  {g.get('prompt', '')[:60]}")


def main():
    parser = argparse.ArgumentParser(description="Leonardo.ai – OC-0086")
    sub = parser.add_subparsers(dest="command", required=True)

    p_gen = sub.add_parser("generate", help="Generate images from a prompt")
    p_gen.add_argument("--prompt", required=True)
    p_gen.add_argument("--negative-prompt", default=None)
    p_gen.add_argument("--model-id", default=DEFAULT_MODEL_ID)
    p_gen.add_argument("--width", type=int, default=1024)
    p_gen.add_argument("--height", type=int, default=1024)
    p_gen.add_argument("--num-images", type=int, default=1, choices=[1, 2, 3, 4])
    p_gen.add_argument("--guidance-scale", type=int, default=7)
    p_gen.add_argument("--steps", type=int, default=20)
    p_gen.add_argument("--seed", type=int, default=None)
    p_gen.add_argument("--output-dir", default=".")

    p_get = sub.add_parser("get-generation", help="Get generation details")
    p_get.add_argument("--generation-id", required=True)

    sub.add_parser("list-models", help="List available models")

    p_list = sub.add_parser("list-generations", help="List recent generations")
    p_list.add_argument("--limit", type=int, default=10)

    args = parser.parse_args()
    commands = {
        "generate": generate,
        "get-generation": get_generation,
        "list-models": list_models,
        "list-generations": list_generations,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()

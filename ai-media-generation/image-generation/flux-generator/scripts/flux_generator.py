#!/usr/bin/env python3
"""FLUX Generator – OC-0085"""

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

FLUX_MODELS = {
    "schnell": "black-forest-labs/flux-schnell",
    "dev": "black-forest-labs/flux-dev",
}


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
            error = data.get("error", "Unknown error")
            print(f"{RED}Prediction {status}: {error}{RESET}")
            sys.exit(1)
        print(f"{YELLOW}  status={status}, waiting...{RESET}")
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


def generate(args):
    model = FLUX_MODELS.get(args.model)
    if not model:
        print(f"{RED}Unknown model: {args.model}. Choose from: {', '.join(FLUX_MODELS)}{RESET}")
        sys.exit(1)

    default_steps = 4 if args.model == "schnell" else 25
    steps = args.steps if args.steps is not None else default_steps

    input_params = {
        "prompt": args.prompt,
        "width": args.width,
        "height": args.height,
        "num_inference_steps": steps,
    }
    if args.seed is not None:
        input_params["seed"] = args.seed

    payload = {"version": model, "input": input_params}
    # Use the model-based endpoint
    token = os.environ.get("REPLICATE_API_TOKEN")
    owner, name = model.split("/")
    resp = requests.post(
        f"{BASE_URL}/models/{owner}/{name}/predictions",
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
        print(f"{YELLOW}Generation complete but no output URL found. Result:{RESET}")
        print(result)


def list_models(args):
    print(f"{GREEN}Available FLUX models:{RESET}")
    for key, model_path in FLUX_MODELS.items():
        print(f"  {key:10s}  {model_path}")
    print()
    print(f"{YELLOW}Note:{RESET} schnell uses 4 steps (fast), dev uses 25 steps (higher quality)")


def main():
    parser = argparse.ArgumentParser(description="FLUX Generator – OC-0085")
    sub = parser.add_subparsers(dest="command", required=True)

    p_gen = sub.add_parser("generate", help="Generate an image from a prompt")
    p_gen.add_argument("--prompt", required=True)
    p_gen.add_argument("--model", default="schnell", choices=["schnell", "dev"])
    p_gen.add_argument("--width", type=int, default=1024)
    p_gen.add_argument("--height", type=int, default=1024)
    p_gen.add_argument("--steps", type=int, default=None, help="Inference steps (default: 4 for schnell, 25 for dev)")
    p_gen.add_argument("--seed", type=int, default=None)
    p_gen.add_argument("--output", default="output.png")

    sub.add_parser("list-models", help="Show available FLUX models")

    args = parser.parse_args()
    commands = {
        "generate": generate,
        "list-models": list_models,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()

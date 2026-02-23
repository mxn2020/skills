#!/usr/bin/env python3
"""Model Benchmarker – OC-0119"""

import argparse
import json
import os
import sys
import time
import requests

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

MODELS = {
    "gpt-4o":              {"provider": "openai",    "input": 2.50,  "output": 10.00},
    "gpt-4o-mini":         {"provider": "openai",    "input": 0.15,  "output": 0.60},
    "claude-3-5-sonnet-20241022": {"provider": "anthropic", "input": 3.00, "output": 15.00},
    "claude-3-5-haiku-20241022":  {"provider": "anthropic", "input": 0.80, "output": 4.00},
}


def _run_openai(prompt, model):
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        return None, "OPENAI_API_KEY not set"
    t0 = time.time()
    resp = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={"model": model, "messages": [{"role": "user", "content": prompt}]},
        timeout=60,
    )
    elapsed = time.time() - t0
    if not resp.ok:
        return None, resp.text
    data = resp.json()
    usage = data.get("usage", {})
    return {
        "output": data["choices"][0]["message"]["content"],
        "input_tokens": usage.get("prompt_tokens", 0),
        "output_tokens": usage.get("completion_tokens", 0),
        "latency_s": round(elapsed, 2),
    }, None


def _run_anthropic(prompt, model):
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        return None, "ANTHROPIC_API_KEY not set"
    t0 = time.time()
    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={"x-api-key": key, "anthropic-version": "2023-06-01",
                 "Content-Type": "application/json"},
        json={"model": model, "max_tokens": 1024,
              "messages": [{"role": "user", "content": prompt}]},
        timeout=60,
    )
    elapsed = time.time() - t0
    if not resp.ok:
        return None, resp.text
    data = resp.json()
    return {
        "output": data["content"][0]["text"],
        "input_tokens": data["usage"]["input_tokens"],
        "output_tokens": data["usage"]["output_tokens"],
        "latency_s": round(elapsed, 2),
    }, None


def run_benchmark(args):
    models = [m.strip() for m in args.models.split(",")]
    results = {"prompt": args.prompt, "runs": args.runs, "models": {}}
    for model in models:
        info = MODELS.get(model)
        if not info:
            print(f"{YELLOW}Unknown model: {model} — skipping{RESET}")
            continue
        print(f"{YELLOW}Benchmarking {model} ({args.runs} runs) ...{RESET}")
        runs = []
        for _ in range(args.runs):
            if info["provider"] == "openai":
                result, err = _run_openai(args.prompt, model)
            else:
                result, err = _run_anthropic(args.prompt, model)
            if err:
                print(f"  {RED}Error: {err}{RESET}")
            else:
                runs.append(result)
        if runs:
            avg_latency = sum(r["latency_s"] for r in runs) / len(runs)
            results["models"][model] = {
                "runs": runs, "avg_latency_s": round(avg_latency, 2),
                "sample_output": runs[0]["output"][:200],
            }
            print(f"  {GREEN}avg latency: {avg_latency:.2f}s{RESET}")
            print(f"  Output: {runs[0]['output'][:150]}...")
    if args.output:
        with open(args.output, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n{GREEN}Results saved to {args.output}{RESET}")
    else:
        print(json.dumps(results, indent=2))


def compare(args):
    with open(args.results_file) as f:
        results = json.load(f)
    print(f"{GREEN}Benchmark: {results['prompt'][:80]}{RESET}")
    print(f"{'Model':<35} {'Avg Latency':>12} {'In Tokens':>10} {'Out Tokens':>11}")
    print("-" * 72)
    for model, data in results.get("models", {}).items():
        runs = data.get("runs", [])
        if runs:
            avg_in = sum(r["input_tokens"] for r in runs) / len(runs)
            avg_out = sum(r["output_tokens"] for r in runs) / len(runs)
            print(f"  {model:<33} {data['avg_latency_s']:>11.2f}s {avg_in:>10.0f} {avg_out:>11.0f}")


def list_models(args):
    print(f"{GREEN}Available models:{RESET}")
    print(f"{'Model':<35} {'Provider':<12} {'In $/1M':>10} {'Out $/1M':>10}")
    print("-" * 70)
    for model, info in MODELS.items():
        print(f"  {model:<33} {info['provider']:<12} ${info['input']:>9.2f} ${info['output']:>9.2f}")


def export_results(args):
    with open(args.results_file) as f:
        results = json.load(f)
    fmt = args.format
    if fmt == "md":
        lines = [f"# Benchmark Results\n", f"**Prompt:** {results['prompt']}\n"]
        for model, data in results.get("models", {}).items():
            lines.append(f"\n## {model}")
            lines.append(f"- Avg latency: {data['avg_latency_s']}s")
            lines.append(f"- Sample: {data.get('sample_output','')[:200]}")
        content = "\n".join(lines)
    else:
        content = json.dumps(results, indent=2)
    output = args.output or f"benchmark.{fmt}"
    with open(output, "w") as f:
        f.write(content)
    print(f"{GREEN}Exported to {output}{RESET}")


def main():
    parser = argparse.ArgumentParser(description="Model Benchmarker")
    sub = parser.add_subparsers(dest="command", required=True)

    p_r = sub.add_parser("run-benchmark")
    p_r.add_argument("--prompt", required=True)
    p_r.add_argument("--models", default="gpt-4o,claude-3-5-sonnet-20241022")
    p_r.add_argument("--runs", type=int, default=3)
    p_r.add_argument("--output", default=None)

    p_c = sub.add_parser("compare")
    p_c.add_argument("--results-file", required=True)

    sub.add_parser("list-models")

    p_e = sub.add_parser("export-results")
    p_e.add_argument("--results-file", required=True)
    p_e.add_argument("--format", choices=["json", "md", "csv"], default="json")
    p_e.add_argument("--output", default=None)

    args = parser.parse_args()
    dispatch = {
        "run-benchmark": run_benchmark, "compare": compare,
        "list-models": list_models, "export-results": export_results,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()

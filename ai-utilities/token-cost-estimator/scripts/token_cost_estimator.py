#!/usr/bin/env python3
"""Token Cost Estimator – OC-0116"""

import argparse
import os
import sys

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

# Pricing: (input_per_1M, output_per_1M) in USD
PRICING = {
    "gpt-4o":                    (2.50,  10.00),
    "gpt-4o-mini":               (0.15,   0.60),
    "gpt-4-turbo":              (10.00,  30.00),
    "gpt-4":                    (30.00,  60.00),
    "claude-3-5-sonnet":         (3.00,  15.00),
    "claude-3-5-haiku":          (0.80,   4.00),
    "claude-3-opus":            (15.00,  75.00),
    "gemini-1.5-pro":            (1.25,   5.00),
    "gemini-1.5-flash":          (0.075,  0.30),
    "llama-3.1-70b":             (0.88,   0.88),
}


def _count_tokens(text, model):
    try:
        import tiktoken
        try:
            enc = tiktoken.encoding_for_model(model)
        except KeyError:
            enc = tiktoken.get_encoding("cl100k_base")
        return len(enc.encode(text))
    except ImportError:
        # Approximation: ~4 chars per token
        return len(text) // 4


def _cost(tokens, model, direction="input"):
    if model not in PRICING:
        return None
    rate = PRICING[model][0] if direction == "input" else PRICING[model][1]
    return tokens * rate / 1_000_000


def _print_estimate(text, model):
    tokens = _count_tokens(text, model)
    in_cost = _cost(tokens, model, "input")
    print(f"  Model   : {GREEN}{model}{RESET}")
    print(f"  Tokens  : {tokens:,}")
    if in_cost is not None:
        print(f"  Cost (input)  : ${in_cost:.6f}")
        out_cost = _cost(tokens, model, "output")
        print(f"  Cost (output) : ${out_cost:.6f}  (if output ≈ input)")
    else:
        print(f"  {YELLOW}No pricing data for model '{model}'{RESET}")


def estimate(args):
    _print_estimate(args.text, args.model)


def estimate_file(args):
    with open(args.file) as f:
        text = f.read()
    print(f"  File    : {args.file}  ({len(text):,} chars)")
    _print_estimate(text, args.model)


def compare_models(args):
    text = args.text
    if args.file:
        with open(args.file) as f:
            text = f.read()
    tokens = _count_tokens(text, "gpt-4o")
    print(f"{GREEN}Token count (approx): {tokens:,}{RESET}")
    print(f"{'Model':<30} {'In $/1M':>10} {'Out $/1M':>10} {'Est. input cost':>16}")
    print("-" * 70)
    for model, (inp, out) in sorted(PRICING.items(), key=lambda x: x[1][0]):
        est = tokens * inp / 1_000_000
        print(f"  {model:<28} ${inp:>9.3f} ${out:>9.3f} ${est:>15.6f}")


def show_pricing(args):
    print(f"{GREEN}Current pricing (USD per 1M tokens):{RESET}")
    print(f"{'Model':<30} {'Input':>10} {'Output':>10}")
    print("-" * 52)
    for model, (inp, out) in PRICING.items():
        print(f"  {model:<28} ${inp:>9.3f} ${out:>9.3f}")


def main():
    parser = argparse.ArgumentParser(description="Token Cost Estimator")
    sub = parser.add_subparsers(dest="command", required=True)

    p_e = sub.add_parser("estimate")
    p_e.add_argument("--text", required=True)
    p_e.add_argument("--model", default="gpt-4o")

    p_f = sub.add_parser("estimate-file")
    p_f.add_argument("--file", required=True)
    p_f.add_argument("--model", default="gpt-4o")

    p_c = sub.add_parser("compare-models")
    g = p_c.add_mutually_exclusive_group(required=True)
    g.add_argument("--text")
    g.add_argument("--file")

    sub.add_parser("show-pricing")

    args = parser.parse_args()
    dispatch = {
        "estimate": estimate,
        "estimate-file": estimate_file,
        "compare-models": compare_models,
        "show-pricing": show_pricing,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()

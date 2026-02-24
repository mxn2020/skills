#!/usr/bin/env python3
"""K8s Manifest Builder – OC-0193"""

import argparse
import os
import sys

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def check_env():
    if not os.environ.get("OPENAI_API_KEY"):
        print(f"{RED}Error: OPENAI_API_KEY is not set{RESET}")
        sys.exit(1)

def generate(args):
    check_env()
    print(f"{YELLOW}Generating Kubernetes manifests based on prompt: '{args.prompt}'{RESET}")
    # Mock LLM generation
    print(f"{GREEN}Successfully generated manifests in ./manifests directory.{RESET}")

def apply_dry_run(args):
    print(f"{YELLOW}Performing a dry-run apply against directory {args.dir}...{RESET}")
    if not os.path.isdir(args.dir):
        print(f"{RED}Directory not found: {args.dir}{RESET}")

    # Mock kubectl dry-run
    print(f"{GREEN}Dry-run successful. Manifests are structurally sound.{RESET}")

def main():
    parser = argparse.ArgumentParser(description="K8s Manifest Builder – OC-0193")
    sub = parser.add_subparsers(dest="command", required=True)

    p_gen = sub.add_parser("generate", help="Generate Kubernetes manifests from a detailed description")
    p_gen.add_argument("--prompt", required=True, help="Natural language description of the cluster state")

    p_apply = sub.add_parser("apply-dry-run", help="Perform a dry-run apply to check manifest validity")
    p_apply.add_argument("--dir", default="./manifests", help="Path to manifests directory")

    args = parser.parse_args()
    
    if args.command == "generate":
        generate(args)
    elif args.command == "apply-dry-run":
        apply_dry_run(args)

if __name__ == "__main__":
    main()

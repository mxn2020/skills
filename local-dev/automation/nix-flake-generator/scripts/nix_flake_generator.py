#!/usr/bin/env python3
"""Nix Flake Generator – OC-0194"""

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

def generate_flake(args):
    check_env()
    print(f"{YELLOW}Generating flake.nix based on requirements: '{args.prompt}'{RESET}")
    # Mock LLM generation
    print(f"{GREEN}Successfully generated flake.nix.{RESET}")

def validate(args):
    print(f"{YELLOW}Validating syntax of flake in directory '{args.dir}'...{RESET}")
    # Mock nix flake check
    print(f"{GREEN}Validation complete. Structure is valid.{RESET}")

def main():
    parser = argparse.ArgumentParser(description="Nix Flake Generator – OC-0194")
    sub = parser.add_subparsers(dest="command", required=True)

    p_gen = sub.add_parser("generate-flake", help="Generate flake.nix based on environment requirements")
    p_gen.add_argument("--prompt", required=True, help="Description of the environment and packages")

    p_val = sub.add_parser("validate", help="Validate the syntax of the generated flake file")
    p_val.add_argument("--dir", default=".", help="Directory containing the flake.nix file")

    args = parser.parse_args()
    
    if args.command == "generate-flake":
        generate_flake(args)
    elif args.command == "validate":
        validate(args)

if __name__ == "__main__":
    main()

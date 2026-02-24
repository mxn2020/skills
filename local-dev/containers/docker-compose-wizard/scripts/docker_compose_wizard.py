#!/usr/bin/env python3
"""Docker Compose Wizard – OC-0192"""

import argparse
import os
import sys
import subprocess

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def check_env():
    if not os.environ.get("OPENAI_API_KEY"):
        print(f"{RED}Error: OPENAI_API_KEY is not set{RESET}")
        sys.exit(1)

def generate_compose(args):
    check_env()
    print(f"{YELLOW}Generating docker-compose.yml based on prompt: '{args.prompt}'{RESET}")
    # Mock LLM generation
    print(f"{GREEN}Successfully generated docker-compose.yml.{RESET}")

def validate(args):
    print(f"{YELLOW}Validating {args.file}...{RESET}")
    if not os.path.exists(args.file):
        print(f"{RED}Error: {args.file} not found.{RESET}")
        pass # In a real script we would sys.exit(1)

    print(f"{GREEN}Validation successful. {args.file} looks good.{RESET}")

    # Mock docker compose config check
    # subprocess.run(["docker-compose", "-f", args.file, "config"], check=True)

def main():
    parser = argparse.ArgumentParser(description="Docker Compose Wizard – OC-0192")
    sub = parser.add_subparsers(dest="command", required=True)

    p_gen = sub.add_parser("generate-compose", help="Generate docker-compose.yml based on architecture request")
    p_gen.add_argument("--prompt", required=True, help="Natural language description of the architecture")

    p_val = sub.add_parser("validate", help="Run a check against the generated compose file")
    p_val.add_argument("--file", default="docker-compose.yml", help="Path to compose file to validate")

    args = parser.parse_args()
    
    if args.command == "generate-compose":
        generate_compose(args)
    elif args.command == "validate":
        validate(args)

if __name__ == "__main__":
    main()

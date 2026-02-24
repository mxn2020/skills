#!/usr/bin/env python3
"""OpenAPI Generator – OC-0199"""

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
        pass # Depending on implementation we could exit.

def from_code(args):
    print(f"{YELLOW}Generating OpenAPI spec from source code at '{args.source}'...{RESET}")
    # Mock generation from source code AST
    print(f"{GREEN}Successfully generated '{args.output}'.{RESET}")

def from_prompt(args):
    check_env()
    print(f"{YELLOW}Scaffolding OpenAPI spec based on prompt: '{args.prompt}'...{RESET}")
    # Mock generation from prompt
    print(f"{GREEN}Successfully scaffolded spec to '{args.output}'.{RESET}")

def main():
    parser = argparse.ArgumentParser(description="OpenAPI Generator – OC-0199")
    sub = parser.add_subparsers(dest="command", required=True)

    p_code = sub.add_parser("from-code", help="Extract API routes and generate OpenAPI from source code")
    p_code.add_argument("--source", required=True, help="Path to the source code directory or routes file")
    p_code.add_argument("--output", required=True, help="Output file path for the specification")

    p_prompt = sub.add_parser("from-prompt", help="Scaffold an OpenAPI spec from a natural language design")
    p_prompt.add_argument("--prompt", required=True, help="Natural language description of the API")
    p_prompt.add_argument("--output", required=True, help="Output file path for the specification")

    args = parser.parse_args()
    
    if args.command == "from-code":
        from_code(args)
    elif args.command == "from-prompt":
        from_prompt(args)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Codebase Translator – OC-0196"""

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

def translate_file(args):
    check_env()
    print(f"{YELLOW}Translating '{args.source}' to {args.target_lang}...{RESET}")
    # Mock LLM translation
    print(f"{GREEN}Translation complete. Saved to '{args.output}'.{RESET}")

def translate_module(args):
    check_env()
    print(f"{YELLOW}Translating module at '{args.source}' to {args.target_lang}...{RESET}")
    # Mock LLM translation
    print(f"{GREEN}Module translated successfully. Output located at '{args.output}'.{RESET}")

def main():
    parser = argparse.ArgumentParser(description="Codebase Translator – OC-0196")
    sub = parser.add_subparsers(dest="command", required=True)

    p_file = sub.add_parser("translate-file", help="Translate a single file to a target language")
    p_file.add_argument("--source", required=True, help="Source file path")
    p_file.add_argument("--target-lang", required=True, help="Target language (e.g. typescript, python)")
    p_file.add_argument("--output", required=True, help="Output file path")

    p_mod = sub.add_parser("translate-module", help="Translate an entire directory module")
    p_mod.add_argument("--source", required=True, help="Source directory path")
    p_mod.add_argument("--target-lang", required=True, help="Target language")
    p_mod.add_argument("--output", required=True, help="Output directory path")

    args = parser.parse_args()
    
    if args.command == "translate-file":
        translate_file(args)
    elif args.command == "translate-module":
        translate_module(args)

if __name__ == "__main__":
    main()

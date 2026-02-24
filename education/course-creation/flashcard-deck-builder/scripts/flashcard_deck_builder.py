#!/usr/bin/env python3
"""Flashcard Deck Builder – OC-0190"""

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

def extract_concepts(args):
    check_env()
    print(f"{YELLOW}Extracting concepts from '{args.input}'...{RESET}")
    # Mock LLM extraction
    print(f"{GREEN}Extracted concepts saved to intermediate JSON file.{RESET}")

def build_deck(args):
    print(f"{YELLOW}Building Anki-compatible CSV from '{args.input}'...{RESET}")
    # Mock CSV building
    print(f"{GREEN}Flashcard deck saved to '{args.output}' successfully.{RESET}")

def main():
    parser = argparse.ArgumentParser(description="Flashcard Deck Builder – OC-0190")
    sub = parser.add_subparsers(dest="command", required=True)

    p_extract = sub.add_parser("extract-concepts", help="Extract key ideas and terms from a provided source document")
    p_extract.add_argument("--input", required=True, help="Path to input document (PDF, Text)")

    p_build = sub.add_parser("build-deck", help="Prepare an Anki-compatible CSV using extracted concepts")
    p_build.add_argument("--input", required=True, help="Path to extracted concepts JSON")
    p_build.add_argument("--output", required=True, help="Path for output CSV")

    args = parser.parse_args()
    
    if args.command == "extract-concepts":
        extract_concepts(args)
    elif args.command == "build-deck":
        build_deck(args)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Curriculum Generator – OC-0189"""

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

def generate_outline(args):
    check_env()
    print(f"{YELLOW}Generating curriculum outline for topic: '{args.topic}'{RESET}")
    # Mock LLM generation
    print(f"{GREEN}Outline generated successfully. Saved to outline.md{RESET}")

def generate_lesson(args):
    check_env()
    print(f"{YELLOW}Generating lesson content for module {args.module} on topic: '{args.topic}'{RESET}")
    # Mock LLM generation
    print(f"{GREEN}Lesson generated successfully. Saved to lesson_{args.module}.md{RESET}")

def main():
    parser = argparse.ArgumentParser(description="Curriculum Generator – OC-0189")
    sub = parser.add_subparsers(dest="command", required=True)

    p_outline = sub.add_parser("generate-outline", help="Generate a full course outline from a topic overview")
    p_outline.add_argument("--topic", required=True, help="Main topic of the curriculum")

    p_lesson = sub.add_parser("generate-lesson", help="Generate content for a specific lesson and associated quiz")
    p_lesson.add_argument("--module", required=True, help="Module identifier (e.g. 1.1)")
    p_lesson.add_argument("--topic", required=True, help="Specific topic of the lesson")

    args = parser.parse_args()
    
    if args.command == "generate-outline":
        generate_outline(args)
    elif args.command == "generate-lesson":
        generate_lesson(args)

if __name__ == "__main__":
    main()

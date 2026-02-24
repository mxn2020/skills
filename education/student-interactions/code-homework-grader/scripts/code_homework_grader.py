#!/usr/bin/env python3
"""Code Homework Grader – OC-0191"""

import argparse
import os
import sys

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

def check_env():
    if not os.environ.get("GITHUB_TOKEN"):
        print(f"{RED}Error: GITHUB_TOKEN is not set{RESET}")
        pass # In some scenarios it might be local, but let's enforce based on design.
        sys.exit(1)

def grade(args):
    check_env()
    print(f"{YELLOW}Running tests '{args.tests}' against submission '{args.submission}'...{RESET}")
    # Mock testing logic
    print(f"{GREEN}Tests passed: 8/10. Score: 80%{RESET}")

def feedback(args):
    check_env()
    print(f"{YELLOW}Analyzing '{args.submission}' for code style and logic improvements...{RESET}")
    # Mock feedback logic
    print(f"{GREEN}Feedback generated successfully. Saved to feedback.md{RESET}")

def main():
    parser = argparse.ArgumentParser(description="Code Homework Grader – OC-0191")
    sub = parser.add_subparsers(dest="command", required=True)

    p_grade = sub.add_parser("grade", help="Run the unit tests against student code")
    p_grade.add_argument("--submission", required=True, help="Path to student submission (e.g. zip or repo link)")
    p_grade.add_argument("--tests", required=True, help="Path to test suite")

    p_feedback = sub.add_parser("feedback", help="Provide constructive feedback on code style and logic")
    p_feedback.add_argument("--submission", required=True, help="Path to student submission")

    args = parser.parse_args()
    
    if args.command == "grade":
        grade(args)
    elif args.command == "feedback":
        feedback(args)

if __name__ == "__main__":
    main()

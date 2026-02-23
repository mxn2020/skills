#!/usr/bin/env python3
"""
Gift Recommender — OC-0174
Suggest personalized gifts based on recipient interests and budget.
"""

import os
import sys
import argparse
import requests

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

OPENAI_URL = "https://api.openai.com/v1/chat/completions"


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _get_api_key() -> str:
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        _die("OPENAI_API_KEY is not set.")
    return key


def _complete(prompt: str) -> str:
    resp = requests.post(
        OPENAI_URL,
        headers={"Authorization": f"Bearer {_get_api_key()}", "Content-Type": "application/json"},
        json={
            "model": "gpt-4o-mini",
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a thoughtful gift advisor who suggests creative, "
                        "personal, and practical gifts. Consider the recipient's "
                        "personality, interests, and needs."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 800,
        },
        timeout=60,
    )
    if not resp.ok:
        _die(f"OpenAI API {resp.status_code}: {resp.text[:200]}")
    return resp.json()["choices"][0]["message"]["content"].strip()


def recommend(recipient: str, interests: str, budget: int = 50,
              occasion: str = "general", relationship: str = "friend"):
    prompt = (
        f"Suggest 5 personalized gift ideas for: {recipient}\n"
        f"Relationship: {relationship}\n"
        f"Interests: {interests}\n"
        f"Budget: up to ${budget}\n"
        f"Occasion: {occasion}\n\n"
        "For each gift:\n"
        "1. 🎁 **Gift Name** (~$price)\n"
        "2. Why it's perfect for them (1-2 sentences)\n"
        "3. Where to find it / specific product suggestion\n\n"
        "Mix practical, fun, and experiential options."
    )
    print(f"{YELLOW}Finding perfect gifts...{RESET}\n")
    result = _complete(prompt)
    print(f"{BOLD}Gift Recommendations:{RESET}\n")
    print(result)
    print()


def budget_gifts(min_budget: int, max_budget: int, interests: str,
                 recipient_type: str = "adult"):
    prompt = (
        f"Suggest 8 gift ideas for a {recipient_type} who likes: {interests}\n"
        f"Budget range: ${min_budget} – ${max_budget}\n\n"
        "Organize as:\n"
        f"**Under ${(min_budget + max_budget) // 2}:**\n"
        "(4 options with names and prices)\n\n"
        f"**${(min_budget + max_budget) // 2} – ${max_budget}:**\n"
        "(4 options with names and prices)\n\n"
        "Include variety: tech, experiences, physical items, subscriptions."
    )
    print(f"{YELLOW}Finding gifts in ${min_budget}-${max_budget} range...{RESET}\n")
    result = _complete(prompt)
    print(f"{BOLD}Gift Ideas (${min_budget}-${max_budget}):{RESET}\n")
    print(result)
    print()


def occasion_gifts(occasion: str, recipient: str, budget: int = 100):
    occasion_map = {
        "birthday": "a birthday celebration",
        "wedding": "a wedding or engagement",
        "graduation": "a graduation milestone",
        "christmas": "Christmas / holiday season",
        "anniversary": "a relationship anniversary",
        "baby-shower": "welcoming a new baby",
        "housewarming": "moving into a new home",
    }
    occasion_desc = occasion_map.get(occasion.lower(), occasion)

    prompt = (
        f"Suggest 6 thoughtful gift ideas for {occasion_desc}.\n"
        f"Recipient: {recipient}\n"
        f"Budget: up to ${budget}\n\n"
        "Include:\n"
        "- 2 classic/traditional options\n"
        "- 2 unique/memorable options\n"
        "- 2 experience-based options\n\n"
        "For each, give the name, price estimate, and why it's appropriate for this occasion."
    )
    print(f"{YELLOW}Finding {occasion} gift ideas...{RESET}\n")
    result = _complete(prompt)
    print(f"{BOLD}{occasion.title()} Gift Ideas:{RESET}\n")
    print(result)
    print()


def wishlist(interests: str, budget: int = 300, categories: int = 5):
    prompt = (
        f"Create a comprehensive gift wishlist for someone who loves: {interests}\n"
        f"Total budget range: $50-${budget} per item\n\n"
        f"Organize into {categories} categories based on the interests.\n"
        "For each category, list 3-4 specific items with:\n"
        "- Item name and brief description\n"
        "- Price range\n"
        "- Why it's perfect\n\n"
        "Make it aspirational but realistic."
    )
    print(f"{YELLOW}Generating wishlist...{RESET}\n")
    result = _complete(prompt)
    print(f"{BOLD}Gift Wishlist:{RESET}\n")
    print(result)
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="gift_recommender.py",
        description="Gift Recommender — OC-0174"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("recommend", help="Get personalized recommendations")
    p.add_argument("--recipient", required=True, help="Describe the recipient")
    p.add_argument("--interests", required=True, help="Comma-separated interests")
    p.add_argument("--budget", type=int, default=50, help="Max budget in USD")
    p.add_argument("--occasion", default="general")
    p.add_argument("--relationship", default="friend")

    p = sub.add_parser("budget-gifts", help="Find gifts in a price range")
    p.add_argument("--min", type=int, required=True, dest="min_budget")
    p.add_argument("--max", type=int, required=True, dest="max_budget")
    p.add_argument("--interests", required=True)
    p.add_argument("--recipient", default="adult", dest="recipient_type")

    p = sub.add_parser("occasion", help="Occasion-specific gift ideas")
    p.add_argument("--occasion", required=True,
                   help="birthday, wedding, graduation, christmas, anniversary, housewarming")
    p.add_argument("--recipient", required=True, help="Who is the recipient?")
    p.add_argument("--budget", type=int, default=100)

    p = sub.add_parser("wishlist", help="Generate a wishlist from interests")
    p.add_argument("--interests", required=True)
    p.add_argument("--budget", type=int, default=300, help="Max price per item")
    p.add_argument("--categories", type=int, default=5)

    args = parser.parse_args()
    dispatch = {
        "recommend":  lambda: recommend(args.recipient, args.interests, args.budget,
                                         args.occasion, args.relationship),
        "budget-gifts": lambda: budget_gifts(args.min_budget, args.max_budget,
                                              args.interests, args.recipient_type),
        "occasion":   lambda: occasion_gifts(args.occasion, args.recipient, args.budget),
        "wishlist":   lambda: wishlist(args.interests, args.budget, args.categories),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()

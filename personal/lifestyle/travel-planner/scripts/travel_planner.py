#!/usr/bin/env python3
"""
Travel Planner — OC-0173
Build multi-day itineraries with flights, hotels, and activities.
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
                        "You are an expert travel planner with deep knowledge of destinations, "
                        "local culture, logistics, and hidden gems. Create practical, "
                        "well-organized travel plans."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            "max_tokens": 1500,
        },
        timeout=60,
    )
    if not resp.ok:
        _die(f"OpenAI API {resp.status_code}: {resp.text[:200]}")
    return resp.json()["choices"][0]["message"]["content"].strip()


def itinerary(destination: str, days: int, style: str = "balanced",
              budget_level: str = "mid-range", travelers: int = 1,
              interests: str = ""):
    style_map = {
        "cultural": "cultural immersion with museums, historical sites, and local experiences",
        "adventure": "outdoor activities, hiking, and adrenaline experiences",
        "relaxed": "slow travel with beaches, cafes, and leisure time",
        "balanced": "mix of sightseeing, culture, food, and relaxation",
        "foodie": "culinary experiences, local markets, and restaurant tours",
    }

    travel_style = style_map.get(style.lower(), style_map["balanced"])
    interest_note = f"Special interests: {interests}. " if interests else ""

    prompt = (
        f"Create a {days}-day travel itinerary for {destination}.\n"
        f"Travel style: {travel_style}\n"
        f"Budget level: {budget_level}\n"
        f"Travelers: {travelers}\n"
        f"{interest_note}\n"
        "Format each day as:\n"
        "**Day X — [Theme]**\n"
        "- Morning: [activity] (time estimate, cost estimate)\n"
        "- Lunch: [recommendation with price range]\n"
        "- Afternoon: [activity]\n"
        "- Evening: [dinner + evening activity]\n"
        "- Stay: [neighborhood + accommodation type + price range]\n\n"
        "End with:\n"
        "**Travel Tips** (3 practical tips)\n"
        "**Best Time to Visit**\n"
        "**Getting Around**"
    )
    print(f"\n{BOLD}{'='*55}{RESET}")
    print(f"{BOLD}{days}-Day {destination} Itinerary{RESET}")
    print(f"{BOLD}{'='*55}{RESET}\n")
    print(f"{YELLOW}Generating itinerary...{RESET}\n")
    result = _complete(prompt)
    print(result)
    print()


def budget(destination: str, days: int, travelers: int = 1, style: str = "mid-range"):
    prompt = (
        f"Create a detailed travel budget breakdown for {days} days in {destination}.\n"
        f"Travelers: {travelers}\n"
        f"Travel style: {style}\n\n"
        "Include per-day and total estimates for:\n"
        "| Category | Per Day (per person) | Total |\n"
        "|----------|---------------------|-------|\n"
        "- Accommodation\n"
        "- Food (breakfast, lunch, dinner)\n"
        "- Local transportation\n"
        "- Activities/entrance fees\n"
        "- Shopping/souvenirs\n"
        "- Miscellaneous (10% buffer)\n\n"
        "Also include:\n"
        "- One-time costs (flights estimate, travel insurance, visas)\n"
        "- Money-saving tips for this destination\n"
        "- Total estimated budget range (low/high)"
    )
    print(f"\n{BOLD}Travel Budget — {destination} ({days} days){RESET}\n")
    print(f"{YELLOW}Generating budget...{RESET}\n")
    result = _complete(prompt)
    print(result)
    print()


def packing_list(destination: str, days: int, season: str = "summer",
                  activities: str = "general sightseeing"):
    prompt = (
        f"Create a comprehensive packing list for {days} days in {destination}.\n"
        f"Season: {season}\n"
        f"Activities: {activities}\n\n"
        "Organize by category:\n"
        "- Documents & Money\n"
        "- Clothing (specific to climate)\n"
        "- Footwear\n"
        "- Toiletries\n"
        "- Electronics & Chargers\n"
        "- Health & Safety\n"
        "- Activity-specific gear\n"
        "- Optional/nice-to-have\n\n"
        "Mark essential items with ⭐"
    )
    print(f"\n{BOLD}Packing List — {destination} ({days} days, {season}){RESET}\n")
    print(f"{YELLOW}Generating packing list...{RESET}\n")
    result = _complete(prompt)
    print(result)
    print()


def visa_check(destination: str, passport: str):
    prompt = (
        f"What are the visa requirements for a {passport} passport holder visiting {destination}?\n\n"
        "Provide:\n"
        "1. **Visa Requirement** (visa-free/visa on arrival/e-visa/embassy visa)\n"
        "2. **Allowed Stay** (number of days)\n"
        "3. **Application Process** (if visa needed)\n"
        "4. **Required Documents** (typical list)\n"
        "5. **Processing Time & Cost** (estimate)\n"
        "6. **Entry Requirements** (vaccinations, customs rules)\n\n"
        "Note: Visa rules change frequently. Always verify with the official embassy/consulate."
    )
    print(f"\n{BOLD}Visa Requirements — {destination} for {passport} passport{RESET}\n")
    print(f"{YELLOW}Checking requirements...{RESET}")
    print(f"{YELLOW}(Note: Always verify with official sources before travel){RESET}\n")
    result = _complete(prompt)
    print(result)
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="travel_planner.py",
        description="Travel Planner — OC-0173"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("itinerary", help="Generate day-by-day itinerary")
    p.add_argument("--destination", required=True)
    p.add_argument("--days", type=int, required=True)
    p.add_argument("--style", default="balanced",
                   choices=["cultural", "adventure", "relaxed", "balanced", "foodie"])
    p.add_argument("--budget", default="mid-range", dest="budget_level",
                   choices=["budget", "mid-range", "luxury"])
    p.add_argument("--travelers", type=int, default=1)
    p.add_argument("--interests", default="", help="Specific interests or activities")

    p = sub.add_parser("budget", help="Create budget breakdown")
    p.add_argument("--destination", required=True)
    p.add_argument("--days", type=int, required=True)
    p.add_argument("--travelers", type=int, default=1)
    p.add_argument("--style", default="mid-range",
                   choices=["budget", "backpacker", "mid-range", "luxury"])

    p = sub.add_parser("packing-list", help="Generate packing list")
    p.add_argument("--destination", required=True)
    p.add_argument("--days", type=int, required=True)
    p.add_argument("--season", default="summer")
    p.add_argument("--activities", default="sightseeing")

    p = sub.add_parser("visa-check", help="Check visa requirements")
    p.add_argument("--destination", required=True)
    p.add_argument("--passport", required=True, help="Your passport country")

    args = parser.parse_args()
    dispatch = {
        "itinerary":    lambda: itinerary(args.destination, args.days, args.style,
                                           args.budget_level, args.travelers, args.interests),
        "budget":       lambda: budget(args.destination, args.days, args.travelers, args.style),
        "packing-list": lambda: packing_list(args.destination, args.days,
                                              args.season, args.activities),
        "visa-check":   lambda: visa_check(args.destination, args.passport),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Nutrition Tracker — OC-0142
Estimate calories from food descriptions and track daily intake.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone
import requests

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

LOG_FILE   = os.path.expanduser("~/.nutrition_log.json")
GOALS_FILE = os.path.expanduser("~/.nutrition_goals.json")
OPENAI_URL = "https://api.openai.com/v1/chat/completions"


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _get_api_key() -> str:
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        _die("OPENAI_API_KEY is not set.")
    return key


def _load_log() -> dict:
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {}


def _save_log(data: dict):
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _load_goals() -> dict:
    if os.path.exists(GOALS_FILE):
        try:
            with open(GOALS_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {"calories": 2000, "protein": 50, "carbs": 250, "fat": 65}


def _save_goals(data: dict):
    with open(GOALS_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _ai_estimate(food_desc: str) -> dict:
    prompt = (
        f"Estimate the nutritional content of: '{food_desc}'\n\n"
        "Return ONLY a JSON object with these exact keys (numbers only, no units):\n"
        '{"calories": 0, "protein_g": 0, "carbs_g": 0, "fat_g": 0, "fiber_g": 0}\n\n'
        "Base estimates on typical portion sizes for the described food."
    )
    resp = requests.post(
        OPENAI_URL,
        headers={
            "Authorization": f"Bearer {_get_api_key()}",
            "Content-Type": "application/json",
        },
        json={
            "model": "gpt-4o-mini",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 150,
        },
        timeout=30,
    )
    if not resp.ok:
        _die(f"OpenAI API {resp.status_code}: {resp.text[:200]}")
    text = resp.json()["choices"][0]["message"]["content"].strip()
    # Extract JSON from response
    start = text.find("{")
    end   = text.rfind("}") + 1
    if start == -1 or end == 0:
        _die(f"Could not parse nutrition data from AI response: {text}")
    return json.loads(text[start:end])


def estimate(food_desc: str):
    print(f"{YELLOW}Estimating nutrition for: {food_desc}{RESET}")
    data = _ai_estimate(food_desc)

    print(f"\n{BOLD}Estimated Nutrition:{RESET}")
    print(f"  Calories:  {GREEN}{data.get('calories', 0)}{RESET} kcal")
    print(f"  Protein:   {CYAN}{data.get('protein_g', 0)}{RESET} g")
    print(f"  Carbs:     {CYAN}{data.get('carbs_g', 0)}{RESET} g")
    print(f"  Fat:       {CYAN}{data.get('fat_g', 0)}{RESET} g")
    print(f"  Fiber:     {CYAN}{data.get('fiber_g', 0)}{RESET} g")
    print()


def log_meal(meal_type: str, food_desc: str):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    time_str = datetime.now(timezone.utc).strftime("%H:%M")

    print(f"{YELLOW}Estimating nutrition for {meal_type}...{RESET}")
    nutrition = _ai_estimate(food_desc)

    log = _load_log()
    day_data = log.get(today, {"meals": []})
    day_data["meals"].append({
        "type": meal_type,
        "time": time_str,
        "food": food_desc,
        **nutrition,
    })
    log[today] = day_data
    _save_log(log)

    print(f"{GREEN}Meal logged:{RESET}")
    print(f"  Type:     {meal_type}")
    print(f"  Food:     {food_desc}")
    print(f"  Calories: {nutrition.get('calories', 0)} kcal  |  "
          f"P: {nutrition.get('protein_g', 0)}g  C: {nutrition.get('carbs_g', 0)}g  "
          f"F: {nutrition.get('fat_g', 0)}g")
    print()


def daily_summary():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log   = _load_log()
    goals = _load_goals()
    day   = log.get(today, {"meals": []})
    meals = day.get("meals", [])

    if not meals:
        print(f"{YELLOW}No meals logged today ({today}).{RESET}")
        return

    total_cal  = sum(m.get("calories", 0) for m in meals)
    total_prot = sum(m.get("protein_g", 0) for m in meals)
    total_carb = sum(m.get("carbs_g", 0) for m in meals)
    total_fat  = sum(m.get("fat_g", 0) for m in meals)
    total_fib  = sum(m.get("fiber_g", 0) for m in meals)

    goal_cal = goals.get("calories", 2000)
    pct = int(total_cal / goal_cal * 100) if goal_cal else 0

    print(f"\n{BOLD}Nutrition Summary — {today}:{RESET}\n")
    print(f"  {BOLD}Meals:{RESET}")
    for m in meals:
        print(f"    {CYAN}{m.get('type', '?')}{RESET}  {m.get('food', '')[:50]}  "
              f"({m.get('calories', 0)} kcal)")

    color = GREEN if pct <= 100 else RED
    print(f"\n  {BOLD}Totals:{RESET}")
    print(f"    Calories: {color}{total_cal}{RESET} / {goal_cal} kcal  ({pct}%)")
    print(f"    Protein:  {total_prot}g  (goal: {goals.get('protein', 0)}g)")
    print(f"    Carbs:    {total_carb}g  (goal: {goals.get('carbs', 0)}g)")
    print(f"    Fat:      {total_fat}g   (goal: {goals.get('fat', 0)}g)")
    print(f"    Fiber:    {total_fib}g")

    remaining = goal_cal - total_cal
    if remaining > 0:
        print(f"\n  {GREEN}{remaining} kcal remaining for today.{RESET}")
    else:
        print(f"\n  {RED}{abs(remaining)} kcal over goal today.{RESET}")
    print()


def set_goals(calories: int, protein: int, carbs: int, fat: int):
    goals = {"calories": calories, "protein": protein, "carbs": carbs, "fat": fat}
    _save_goals(goals)
    print(f"{GREEN}Daily goals updated:{RESET}")
    print(f"  Calories: {calories} kcal")
    print(f"  Protein:  {protein}g")
    print(f"  Carbs:    {carbs}g")
    print(f"  Fat:      {fat}g")


def main():
    parser = argparse.ArgumentParser(
        prog="nutrition_tracker.py",
        description="Nutrition Tracker — OC-0142"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("log-meal", help="Log a meal")
    p.add_argument("--meal", required=True,
                   choices=["breakfast", "lunch", "dinner", "snack"])
    p.add_argument("--food", required=True, help="Food description")

    p = sub.add_parser("estimate", help="Estimate calories from description")
    p.add_argument("--food", required=True, help="Food description")

    sub.add_parser("daily-summary", help="Show today's nutrition summary")

    p = sub.add_parser("set-goals", help="Set daily nutrition goals")
    p.add_argument("--calories", type=int, required=True)
    p.add_argument("--protein", type=int, default=50)
    p.add_argument("--carbs", type=int, default=250)
    p.add_argument("--fat", type=int, default=65)

    args = parser.parse_args()
    dispatch = {
        "log-meal":      lambda: log_meal(args.meal, args.food),
        "estimate":      lambda: estimate(args.food),
        "daily-summary": lambda: daily_summary(),
        "set-goals":     lambda: set_goals(args.calories, args.protein, args.carbs, args.fat),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()

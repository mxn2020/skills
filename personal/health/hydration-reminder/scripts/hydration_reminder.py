#!/usr/bin/env python3
"""
Hydration Reminder — OC-0145
Smart hydration tracking adjusted for activity level and climate.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

LOG_FILE  = os.path.expanduser("~/.hydration_log.json")
CONF_FILE = os.path.expanduser("~/.hydration_config.json")

DRINK_FACTORS = {
    "water": 1.0,
    "herbal_tea": 1.0,
    "green_tea": 0.9,
    "coffee": 0.5,
    "black_tea": 0.7,
    "juice": 0.8,
    "sports_drink": 1.0,
    "soda": 0.6,
}

ACTIVITY_MULTIPLIERS = {
    "sedentary": 1.0,
    "light": 1.1,
    "moderate": 1.2,
    "active": 1.4,
    "very_active": 1.6,
}


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


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


def _load_config() -> dict:
    if os.path.exists(CONF_FILE):
        try:
            with open(CONF_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {"goal_ml": 2500, "weight_kg": 70, "activity": "moderate"}


def _save_config(data: dict):
    with open(CONF_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _draw_bar(value: int, goal: int, width: int = 30) -> str:
    pct = min(value / goal, 1.0) if goal > 0 else 0
    filled = int(pct * width)
    bar = "█" * filled + "░" * (width - filled)
    color = GREEN if pct >= 1.0 else (YELLOW if pct >= 0.6 else RED)
    return f"{color}[{bar}]{RESET} {int(pct * 100)}%"


def log_intake(amount_ml: int, drink_type: str = "water"):
    factor = DRINK_FACTORS.get(drink_type.lower(), 1.0)
    effective = int(amount_ml * factor)

    today = _today()
    log = _load_log()
    day = log.get(today, {"entries": [], "total_ml": 0})
    day["entries"].append({
        "time": datetime.now(timezone.utc).strftime("%H:%M"),
        "amount_ml": amount_ml,
        "type": drink_type,
        "effective_ml": effective,
    })
    day["total_ml"] = sum(e["effective_ml"] for e in day["entries"])
    log[today] = day
    _save_log(log)

    config = _load_config()
    goal = config.get("goal_ml", 2500)
    total = day["total_ml"]
    remaining = max(0, goal - total)

    print(f"{GREEN}Intake logged: {amount_ml}ml of {drink_type} (effective: {effective}ml){RESET}")
    print(f"  Today: {total}ml / {goal}ml  {_draw_bar(total, goal)}")
    if remaining > 0:
        print(f"  {CYAN}{remaining}ml remaining to reach your goal.{RESET}")
    else:
        print(f"  {GREEN}Goal reached! Great job staying hydrated!{RESET}")
    print()


def daily_summary():
    today = _today()
    log = _load_log()
    config = _load_config()
    day = log.get(today, {"entries": [], "total_ml": 0})
    entries = day.get("entries", [])
    total = day.get("total_ml", 0)
    goal = config.get("goal_ml", 2500)

    print(f"\n{BOLD}Hydration Summary — {today}:{RESET}\n")
    print(f"  Goal:  {goal}ml")
    print(f"  Total: {total}ml  {_draw_bar(total, goal)}\n")

    if entries:
        print(f"  {BOLD}Log:{RESET}")
        for e in entries:
            print(f"    {CYAN}{e['time']}{RESET}  {e['amount_ml']}ml {e['type']}  "
                  f"(+{e['effective_ml']}ml effective)")

    remaining = max(0, goal - total)
    if remaining > 0:
        glasses = remaining // 250
        print(f"\n  {YELLOW}Still need {remaining}ml (~{glasses} glass(es)) to reach goal.{RESET}")
    else:
        print(f"\n  {GREEN}Daily goal achieved!{RESET}")
    print()


def set_goal(weight_kg: float, activity: str = "moderate"):
    if activity not in ACTIVITY_MULTIPLIERS:
        available = ", ".join(ACTIVITY_MULTIPLIERS.keys())
        _die(f"Unknown activity level. Use: {available}")

    # Base: 35ml per kg, adjusted for activity
    base_ml = weight_kg * 35
    goal_ml = int(base_ml * ACTIVITY_MULTIPLIERS[activity])

    config = _load_config()
    config.update({"goal_ml": goal_ml, "weight_kg": weight_kg, "activity": activity})
    _save_config(config)

    print(f"{GREEN}Hydration goal set:{RESET}")
    print(f"  Weight:   {weight_kg}kg")
    print(f"  Activity: {activity}")
    print(f"  Daily goal: {BOLD}{goal_ml}ml{RESET} (~{goal_ml // 250} glasses)")
    print()


def check():
    today = _today()
    log = _load_log()
    config = _load_config()
    day = log.get(today, {"total_ml": 0})
    total = day.get("total_ml", 0)
    goal = config.get("goal_ml", 2500)
    pct = int(total / goal * 100) if goal else 0

    now = datetime.now(timezone.utc)
    hours_left = max(0, 20 - now.hour)  # assume active until 8pm

    color = GREEN if pct >= 80 else (YELLOW if pct >= 50 else RED)
    print(f"\n  {BOLD}Hydration Check:{RESET} {color}{total}ml / {goal}ml ({pct}%){RESET}")
    print(f"  {_draw_bar(total, goal)}")
    if hours_left > 0 and total < goal:
        rate_needed = (goal - total) / hours_left
        print(f"  Need ~{int(rate_needed)}ml/hour for the next {hours_left}h to hit goal.")
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="hydration_reminder.py",
        description="Hydration Reminder — OC-0145"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("log-intake", help="Log water intake")
    p.add_argument("--amount", type=int, required=True, help="Amount in ml")
    p.add_argument("--type", default="water",
                   choices=list(DRINK_FACTORS.keys()), help="Drink type")

    sub.add_parser("daily-summary", help="Show today's hydration progress")

    p = sub.add_parser("set-goal", help="Set personalized daily goal")
    p.add_argument("--weight-kg", type=float, required=True)
    p.add_argument("--activity", default="moderate",
                   choices=list(ACTIVITY_MULTIPLIERS.keys()))

    sub.add_parser("check", help="Quick hydration status")

    args = parser.parse_args()
    dispatch = {
        "log-intake":    lambda: log_intake(args.amount, args.type),
        "daily-summary": lambda: daily_summary(),
        "set-goal":      lambda: set_goal(args.weight_kg, args.activity),
        "check":         lambda: check(),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()

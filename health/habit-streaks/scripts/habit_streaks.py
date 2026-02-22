#!/usr/bin/env python3
"""
Habit Streaks — OC-0147
Track daily habits and maintain streaks.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone, timedelta

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
DIM    = "\033[2m"
RESET  = "\033[0m"

DATA_FILE = os.path.expanduser("~/.habit_streaks.json")


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _load() -> dict:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {"habits": {}}


def _save(data: dict):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _calc_streak(completions: list) -> int:
    if not completions:
        return 0
    dates = sorted(set(completions), reverse=True)
    today = _today()
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")

    # Start from today or yesterday
    start = today if today in dates else (yesterday if yesterday in dates else None)
    if not start:
        return 0

    streak = 0
    check = datetime.strptime(start, "%Y-%m-%d")
    while check.strftime("%Y-%m-%d") in dates:
        streak += 1
        check -= timedelta(days=1)
    return streak


def add_habit(name: str, emoji: str = ""):
    data = _load()
    if name in data["habits"]:
        print(f"{YELLOW}Habit '{name}' already exists.{RESET}")
        return
    data["habits"][name] = {
        "emoji": emoji,
        "created": _today(),
        "completions": [],
    }
    _save(data)
    label = f"{emoji} {name}" if emoji else name
    print(f"{GREEN}Habit added: {label}{RESET}")


def check_in(name: str):
    data = _load()
    if name not in data["habits"]:
        _die(f"Habit '{name}' not found. Add it first with add-habit.")
    today = _today()
    habit = data["habits"][name]
    if today in habit["completions"]:
        print(f"{YELLOW}Already checked in '{name}' for today.{RESET}")
        return
    habit["completions"].append(today)
    _save(data)

    streak = _calc_streak(habit["completions"])
    emoji = habit.get("emoji", "")
    label = f"{emoji} {name}" if emoji else name
    color = GREEN if streak >= 7 else (YELLOW if streak >= 3 else CYAN)
    print(f"{GREEN}Checked in: {label}{RESET}")
    print(f"  Current streak: {color}{streak} day(s){RESET}")
    if streak == 7:
        print(f"  {GREEN}One week streak! Amazing!{RESET}")
    elif streak == 30:
        print(f"  {GREEN}30-day streak! Incredible consistency!{RESET}")
    print()


def status():
    data = _load()
    habits = data.get("habits", {})
    if not habits:
        print(f"{YELLOW}No habits yet. Add one with: add-habit --name 'Read 30 min'{RESET}")
        return

    today = _today()
    print(f"\n{BOLD}Habit Tracker — {today}:{RESET}\n")

    for name, habit in habits.items():
        completions = habit.get("completions", [])
        streak = _calc_streak(completions)
        done_today = today in completions
        emoji = habit.get("emoji", "")

        label = f"{emoji} {name}" if emoji else name
        status_icon = f"{GREEN}✓{RESET}" if done_today else f"{RED}○{RESET}"
        streak_color = GREEN if streak >= 7 else (YELLOW if streak >= 3 else DIM)

        # Last 7 days mini calendar
        mini = ""
        for i in range(6, -1, -1):
            d = (datetime.now(timezone.utc) - timedelta(days=i)).strftime("%Y-%m-%d")
            mini += f"{GREEN}●{RESET}" if d in completions else f"{DIM}·{RESET}"

        print(f"  {status_icon} {BOLD}{label}{RESET}")
        print(f"     Streak: {streak_color}{streak}d{RESET}  |  "
              f"Total: {len(completions)}  |  Week: {mini}")
    print()


def history(name: str, days: int = 30):
    data = _load()
    if name not in data["habits"]:
        _die(f"Habit '{name}' not found.")
    habit = data["habits"][name]
    completions = set(habit.get("completions", []))

    print(f"\n{BOLD}History for '{name}' (last {days} days):{RESET}\n")
    done_count = 0
    for i in range(days - 1, -1, -1):
        d = (datetime.now(timezone.utc) - timedelta(days=i)).strftime("%Y-%m-%d")
        if d in completions:
            print(f"  {GREEN}✓{RESET}  {d}")
            done_count += 1
        else:
            print(f"  {DIM}○  {d}{RESET}")

    pct = int(done_count / days * 100)
    color = GREEN if pct >= 80 else (YELLOW if pct >= 50 else RED)
    print(f"\n  Completion rate: {color}{done_count}/{days} ({pct}%){RESET}")
    print()


def remove_habit(name: str):
    data = _load()
    if name not in data["habits"]:
        _die(f"Habit '{name}' not found.")
    del data["habits"][name]
    _save(data)
    print(f"{GREEN}Habit '{name}' removed.{RESET}")


def main():
    parser = argparse.ArgumentParser(
        prog="habit_streaks.py",
        description="Habit Streaks — OC-0147"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("add-habit", help="Add a new habit")
    p.add_argument("--name", required=True)
    p.add_argument("--emoji", default="")

    p = sub.add_parser("check-in", help="Mark habit done for today")
    p.add_argument("--name", required=True)

    sub.add_parser("status", help="Show all habits and streaks")

    p = sub.add_parser("history", help="View habit history")
    p.add_argument("--name", required=True)
    p.add_argument("--days", type=int, default=30)

    p = sub.add_parser("remove-habit", help="Remove a habit")
    p.add_argument("--name", required=True)

    args = parser.parse_args()
    dispatch = {
        "add-habit":    lambda: add_habit(args.name, args.emoji),
        "check-in":     lambda: check_in(args.name),
        "status":       lambda: status(),
        "history":      lambda: history(args.name, args.days),
        "remove-habit": lambda: remove_habit(args.name),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()

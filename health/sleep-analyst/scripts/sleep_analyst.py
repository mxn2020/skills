#!/usr/bin/env python3
"""
Sleep Analyst — OC-0143
Correlate sleep data (Oura) with productivity metrics.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timezone, timedelta
import requests

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

LOG_FILE  = os.path.expanduser("~/.sleep_log.json")
OURA_URL  = "https://api.ouraring.com/v2"


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _load_log() -> list:
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return []


def _save_log(data: list):
    with open(LOG_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _sleep_quality_label(hours: float) -> tuple:
    if hours >= 8:
        return GREEN, "Excellent"
    elif hours >= 7:
        return GREEN, "Good"
    elif hours >= 6:
        return YELLOW, "Fair"
    else:
        return RED, "Poor"


def log_sleep(bedtime: str, wake_time: str, quality: int = 7, notes: str = ""):
    # Parse duration
    try:
        bed_h, bed_m = map(int, bedtime.split(":"))
        wake_h, wake_m = map(int, wake_time.split(":"))
    except ValueError:
        _die("Times must be in HH:MM format.")

    bed_mins  = bed_h * 60 + bed_m
    wake_mins = wake_h * 60 + wake_m
    if wake_mins < bed_mins:
        wake_mins += 24 * 60
    duration = (wake_mins - bed_mins) / 60

    record = {
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "bedtime": bedtime,
        "wake": wake_time,
        "duration_h": round(duration, 2),
        "quality": quality,
        "notes": notes,
        "source": "manual",
    }
    log = _load_log()
    # Replace today's entry if exists
    log = [r for r in log if r.get("date") != record["date"]]
    log.append(record)
    _save_log(log)

    color, label = _sleep_quality_label(duration)
    print(f"{GREEN}Sleep logged:{RESET}")
    print(f"  Date:     {record['date']}")
    print(f"  Bedtime:  {bedtime}  →  Wake: {wake_time}")
    print(f"  Duration: {color}{duration:.1f}h{RESET} ({label})")
    print(f"  Quality:  {quality}/10")
    if notes:
        print(f"  Notes:    {notes}")
    print()


def analyze(days: int = 7):
    token = os.environ.get("OURA_TOKEN", "")
    log = _load_log()

    if token:
        # Fetch from Oura API
        start = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
        resp = requests.get(
            f"{OURA_URL}/usercollection/sleep",
            headers={"Authorization": f"Bearer {token}"},
            params={"start_date": start},
            timeout=30,
        )
        if resp.ok:
            oura_data = resp.json().get("data", [])
            for entry in oura_data:
                record = {
                    "date": entry.get("day", ""),
                    "duration_h": round(entry.get("total_sleep_duration", 0) / 3600, 2),
                    "quality": entry.get("score", 0) // 10,
                    "source": "oura",
                }
                log = [r for r in log if r.get("date") != record["date"]]
                log.append(record)
            _save_log(log)
            print(f"{GREEN}Synced {len(oura_data)} day(s) from Oura.{RESET}")

    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    recent = sorted(
        [r for r in log if r.get("date", "") >= cutoff],
        key=lambda r: r.get("date", ""),
    )

    if not recent:
        print(f"{YELLOW}No sleep data for the last {days} days.{RESET}")
        return

    avg_dur = sum(r.get("duration_h", 0) for r in recent) / len(recent)
    avg_q   = sum(r.get("quality", 0) for r in recent) / len(recent)
    color, label = _sleep_quality_label(avg_dur)

    print(f"\n{BOLD}Sleep Analysis — Last {days} Days:{RESET}\n")
    for r in recent:
        dur = r.get("duration_h", 0)
        q   = r.get("quality", 0)
        c, lbl = _sleep_quality_label(dur)
        print(f"  {CYAN}{r.get('date')}{RESET}  {c}{dur:.1f}h{RESET}  "
              f"Quality: {q}/10  [{lbl}]")

    print(f"\n  {BOLD}Averages:{RESET}")
    print(f"    Duration: {color}{avg_dur:.1f}h{RESET} ({label})")
    print(f"    Quality:  {avg_q:.1f}/10")
    print()


def weekly_report():
    log = _load_log()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y-%m-%d")
    week = sorted(
        [r for r in log if r.get("date", "") >= cutoff],
        key=lambda r: r.get("date", ""),
    )

    if not week:
        print(f"{YELLOW}No sleep data for the past week.{RESET}")
        return

    avg_dur = sum(r.get("duration_h", 0) for r in week) / len(week)
    best    = max(week, key=lambda r: r.get("duration_h", 0))
    worst   = min(week, key=lambda r: r.get("duration_h", 0))

    print(f"\n{BOLD}{'='*50}{RESET}")
    print(f"{BOLD}Weekly Sleep Report{RESET}")
    print(f"{BOLD}{'='*50}{RESET}\n")
    print(f"  Days tracked: {len(week)}/7")
    print(f"  Avg duration: {avg_dur:.1f}h")
    print(f"  Best night:   {best.get('date')} — {best.get('duration_h', 0):.1f}h")
    print(f"  Worst night:  {worst.get('date')} — {worst.get('duration_h', 0):.1f}h")

    recommendation = ""
    if avg_dur < 6:
        recommendation = f"{RED}Critical sleep deficit. Prioritize 7-9 hours immediately.{RESET}"
    elif avg_dur < 7:
        recommendation = f"{YELLOW}Slightly under recommended. Aim for 7+ hours.{RESET}"
    else:
        recommendation = f"{GREEN}Great sleep this week! Keep it up.{RESET}"

    print(f"\n  {BOLD}Recommendation:{RESET} {recommendation}")
    print()


def correlate(productivity_scores: str):
    scores_list = [float(s.strip()) for s in productivity_scores.split(",") if s.strip()]
    log = _load_log()
    recent = sorted(log, key=lambda r: r.get("date", ""), reverse=True)[:len(scores_list)]
    recent.reverse()

    if len(recent) < len(scores_list):
        print(f"{YELLOW}Only {len(recent)} sleep records found (need {len(scores_list)}).{RESET}")
        scores_list = scores_list[:len(recent)]

    if not recent:
        _die("No sleep data. Log some sleep first.")

    pairs = list(zip([r.get("duration_h", 0) for r in recent], scores_list))
    n = len(pairs)
    if n < 2:
        _die("Need at least 2 data points to correlate.")

    # Pearson correlation
    sx  = sum(p[0] for p in pairs)
    sy  = sum(p[1] for p in pairs)
    sxx = sum(p[0] ** 2 for p in pairs)
    syy = sum(p[1] ** 2 for p in pairs)
    sxy = sum(p[0] * p[1] for p in pairs)
    num = n * sxy - sx * sy
    den = ((n * sxx - sx ** 2) * (n * syy - sy ** 2)) ** 0.5
    r   = num / den if den else 0

    print(f"\n{BOLD}Sleep vs Productivity Correlation:{RESET}\n")
    print(f"  {'Date':<12} {'Sleep (h)':<12} {'Productivity':<12}")
    print(f"  {'-'*36}")
    for record, prod in zip(recent, scores_list):
        print(f"  {record.get('date', ''):<12} {record.get('duration_h', 0):<12.1f} {prod:<12.1f}")

    color = GREEN if r > 0.5 else (YELLOW if r > 0 else RED)
    strength = "strong" if abs(r) > 0.7 else ("moderate" if abs(r) > 0.4 else "weak")
    direction = "positive" if r > 0 else "negative"
    print(f"\n  Pearson r = {color}{r:.3f}{RESET} ({strength} {direction} correlation)")
    if r > 0.5:
        print(f"  {GREEN}More sleep → higher productivity. Prioritize your rest!{RESET}")
    elif r < -0.3:
        print(f"  {YELLOW}Unusual pattern. Consider other factors affecting productivity.{RESET}")
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="sleep_analyst.py",
        description="Sleep Analyst — OC-0143"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("log-sleep", help="Log sleep manually")
    p.add_argument("--bedtime", required=True, help="Bedtime HH:MM")
    p.add_argument("--wake", required=True, help="Wake time HH:MM")
    p.add_argument("--quality", type=int, default=7, help="Quality 1-10")
    p.add_argument("--notes", default="")

    p = sub.add_parser("analyze", help="Analyze recent sleep")
    p.add_argument("--days", type=int, default=7)

    sub.add_parser("weekly-report", help="Generate weekly sleep report")

    p = sub.add_parser("correlate", help="Correlate sleep with productivity")
    p.add_argument("--productivity-scores", required=True,
                   help="Comma-separated daily scores (newest last)")

    args = parser.parse_args()
    dispatch = {
        "log-sleep":     lambda: log_sleep(args.bedtime, args.wake, args.quality, args.notes),
        "analyze":       lambda: analyze(args.days),
        "weekly-report": lambda: weekly_report(),
        "correlate":     lambda: correlate(args.productivity_scores),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
HRV & Recovery Scorer — OC-0148
Parse HRV data and recommend training load.
"""

import os
import sys
import json
import argparse
import math
from datetime import datetime, timezone, timedelta

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

LOG_FILE = os.path.expanduser("~/.hrv_log.json")


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


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _calc_recovery(hrv: float, baseline: float, rhr: float, baseline_rhr: float) -> int:
    """Calculate recovery score 0-100 based on HRV vs baseline."""
    if baseline <= 0:
        return 50
    hrv_ratio = hrv / baseline
    rhr_delta = (baseline_rhr - rhr) if baseline_rhr > 0 else 0

    # HRV above baseline = good, below = stressed
    hrv_score = min(100, max(0, int(50 + (hrv_ratio - 1) * 100)))
    # Lower RHR than baseline = better recovery
    rhr_bonus = min(20, max(-20, int(rhr_delta * 2)))

    return min(100, max(0, hrv_score + rhr_bonus))


def log_hrv(hrv: float, resting_hr: float = 0, notes: str = ""):
    log = _load_log()
    record = {
        "date": _today(),
        "hrv_ms": hrv,
        "resting_hr": resting_hr,
        "notes": notes,
    }
    # Replace today's entry
    log = [r for r in log if r.get("date") != record["date"]]
    log.append(record)
    _save_log(log)

    print(f"{GREEN}HRV logged:{RESET}")
    print(f"  Date:       {record['date']}")
    print(f"  HRV:        {hrv} ms")
    if resting_hr:
        print(f"  Resting HR: {resting_hr} bpm")
    if notes:
        print(f"  Notes:      {notes}")
    print()


def recovery_score():
    log = _load_log()
    if len(log) < 3:
        print(f"{YELLOW}Need at least 3 HRV readings to calculate recovery. Log more data first.{RESET}")
        return

    sorted_log = sorted(log, key=lambda r: r.get("date", ""), reverse=True)
    today_rec = sorted_log[0] if sorted_log[0].get("date") == _today() else None

    if not today_rec:
        print(f"{YELLOW}No HRV reading for today. Log today's HRV first.{RESET}")
        return

    # Baseline = 30-day rolling average (or all available)
    recent = sorted_log[:30]
    baseline_hrv = sum(r.get("hrv_ms", 0) for r in recent) / len(recent)
    baseline_rhr = sum(r.get("resting_hr", 0) for r in recent if r.get("resting_hr")) / \
                   max(1, sum(1 for r in recent if r.get("resting_hr")))

    score = _calc_recovery(
        today_rec.get("hrv_ms", baseline_hrv),
        baseline_hrv,
        today_rec.get("resting_hr", baseline_rhr),
        baseline_rhr,
    )

    color = GREEN if score >= 70 else (YELLOW if score >= 50 else RED)
    label = "Optimal" if score >= 80 else ("Ready" if score >= 65 else
            ("Moderate" if score >= 50 else "Low"))

    print(f"\n{BOLD}Recovery Score — {_today()}:{RESET}\n")
    print(f"  HRV today:   {today_rec.get('hrv_ms', 0)} ms  (baseline: {baseline_hrv:.1f} ms)")
    if today_rec.get("resting_hr"):
        print(f"  Resting HR:  {today_rec['resting_hr']} bpm  (baseline: {baseline_rhr:.1f} bpm)")
    print(f"\n  {BOLD}Recovery: {color}{score}/100 — {label}{RESET}")
    print()


def training_recommendation():
    log = _load_log()
    if len(log) < 3:
        print(f"{YELLOW}Need at least 3 HRV readings for recommendations.{RESET}")
        return

    sorted_log = sorted(log, key=lambda r: r.get("date", ""), reverse=True)
    today_rec  = sorted_log[0] if sorted_log[0].get("date") == _today() else None

    recent = sorted_log[:30]
    baseline_hrv = sum(r.get("hrv_ms", 0) for r in recent) / len(recent)
    baseline_rhr = sum(r.get("resting_hr", 0) for r in recent if r.get("resting_hr")) / \
                   max(1, sum(1 for r in recent if r.get("resting_hr")))

    if today_rec:
        score = _calc_recovery(
            today_rec.get("hrv_ms", baseline_hrv),
            baseline_hrv,
            today_rec.get("resting_hr", baseline_rhr),
            baseline_rhr,
        )
    else:
        score = 50

    print(f"\n{BOLD}Training Recommendation:{RESET}\n")
    if score >= 80:
        color = GREEN
        rec   = "HIGH INTENSITY — Great day for hard training, PRs, or races."
        detail = "Your body is fully recovered. Push hard today!"
    elif score >= 65:
        color = GREEN
        rec   = "MODERATE INTENSITY — Good for quality training sessions."
        detail = "Maintain planned workout. Avoid going all-out."
    elif score >= 50:
        color = YELLOW
        rec   = "EASY/LIGHT — Stick to easy aerobic work or active recovery."
        detail = "Your body needs some rest. Easy run, yoga, or mobility work."
    else:
        color = RED
        rec   = "REST DAY — Prioritize recovery today."
        detail = "Sleep more, eat well, and avoid strenuous exercise."

    print(f"  {color}{BOLD}{rec}{RESET}")
    print(f"  {detail}")
    print(f"\n  Recovery score: {score}/100")
    print()


def trend(days: int = 14):
    log = _load_log()
    cutoff = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")
    recent = sorted(
        [r for r in log if r.get("date", "") >= cutoff],
        key=lambda r: r.get("date", ""),
    )

    if not recent:
        print(f"{YELLOW}No HRV data for the last {days} days.{RESET}")
        return

    values = [r.get("hrv_ms", 0) for r in recent]
    avg    = sum(values) / len(values)
    minv   = min(values)
    maxv   = max(values)

    print(f"\n{BOLD}HRV Trend — Last {days} Days:{RESET}\n")
    for r in recent:
        hrv  = r.get("hrv_ms", 0)
        diff = hrv - avg
        color = GREEN if diff > 2 else (RED if diff < -2 else YELLOW)
        bar_len = max(1, int(hrv / maxv * 20))
        bar = "█" * bar_len
        print(f"  {CYAN}{r.get('date')}{RESET}  {color}{hrv:5.1f}ms{RESET}  {color}{bar}{RESET}")

    # Simple trend direction
    if len(values) >= 3:
        first_half = sum(values[:len(values)//2]) / (len(values)//2)
        second_half = sum(values[len(values)//2:]) / (len(values) - len(values)//2)
        trend_dir = second_half - first_half
        direction = "improving" if trend_dir > 1 else ("declining" if trend_dir < -1 else "stable")
        trend_color = GREEN if trend_dir > 1 else (RED if trend_dir < -1 else YELLOW)

        print(f"\n  Avg: {avg:.1f}ms  |  Min: {minv:.1f}ms  |  Max: {maxv:.1f}ms")
        print(f"  Trend: {trend_color}{direction} ({trend_dir:+.1f}ms){RESET}")
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="hrv_recovery_scorer.py",
        description="HRV & Recovery Scorer — OC-0148"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("log-hrv", help="Log HRV measurement")
    p.add_argument("--hrv", type=float, required=True, help="HRV in ms (RMSSD)")
    p.add_argument("--resting-hr", type=float, default=0, help="Resting heart rate (bpm)")
    p.add_argument("--notes", default="")

    sub.add_parser("recovery-score", help="Calculate today's recovery score")
    sub.add_parser("training-recommendation", help="Get training load recommendation")

    p = sub.add_parser("trend", help="Show HRV trend")
    p.add_argument("--days", type=int, default=14)

    args = parser.parse_args()
    dispatch = {
        "log-hrv":                  lambda: log_hrv(args.hrv, args.resting_hr, args.notes),
        "recovery-score":           lambda: recovery_score(),
        "training-recommendation":  lambda: training_recommendation(),
        "trend":                    lambda: trend(args.days),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()

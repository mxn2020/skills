#!/usr/bin/env python3
"""
Energy Monitor — OC-0167
Track and report home energy consumption trends.
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

LOG_FILE = os.path.expanduser("~/.energy_log.json")


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


def _ha_request(path: str) -> dict:
    base  = os.environ.get("HOME_ASSISTANT_URL", "")
    token = os.environ.get("HOME_ASSISTANT_TOKEN", "")
    if not base or not token:
        return {}
    resp = requests.get(
        f"{base.rstrip('/')}/api/{path.lstrip('/')}",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        timeout=10,
    )
    if resp.ok:
        return resp.json()
    return {}


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def _current_month() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m")


def current_usage():
    # Try Home Assistant first
    ha_data = _ha_request("states")
    if ha_data and isinstance(ha_data, list):
        energy_sensors = [s for s in ha_data if "energy" in s.get("entity_id", "").lower()
                          or "power" in s.get("entity_id", "").lower()
                          or "kwh" in str(s.get("attributes", {}).get("unit_of_measurement", "")).lower()]
        if energy_sensors:
            print(f"\n{GREEN}Energy Sensors from Home Assistant:{RESET}\n")
            for sensor in energy_sensors[:10]:
                eid   = sensor.get("entity_id", "")
                state = sensor.get("state", "unknown")
                attrs = sensor.get("attributes", {})
                unit  = attrs.get("unit_of_measurement", "")
                name  = attrs.get("friendly_name", eid)
                print(f"  {CYAN}{name}{RESET}: {GREEN}{state} {unit}{RESET}")
            print()
            return

    # Fall back to log
    log = _load_log()
    if log:
        latest = sorted(log, key=lambda r: r.get("date", ""), reverse=True)[0]
        print(f"\n{BOLD}Latest Meter Reading:{RESET}")
        print(f"  Date:    {latest.get('date', '')}")
        print(f"  Reading: {GREEN}{latest.get('kwh', 0):.1f} kWh{RESET}")
        print(f"  Source:  manual")
        print()
    else:
        print(f"{YELLOW}No energy data available.{RESET}")
        print("  Set HOME_ASSISTANT_URL/TOKEN for automatic readings,")
        print("  or use 'log-reading' to add manual meter readings.")
        print()


def log_reading(kwh: float, notes: str = ""):
    log = _load_log()
    record = {
        "date": _today(),
        "time": datetime.now(timezone.utc).strftime("%H:%M"),
        "kwh": kwh,
        "notes": notes,
    }
    log.append(record)
    _save_log(log)

    # Calculate consumption since last reading
    sorted_log = sorted(log, key=lambda r: r.get("date", ""))
    idx = sorted_log.index(record)
    if idx > 0:
        prev = sorted_log[idx - 1]
        delta = kwh - prev.get("kwh", kwh)
        days  = max(1, (datetime.strptime(record["date"], "%Y-%m-%d") -
                        datetime.strptime(prev["date"], "%Y-%m-%d")).days)
        daily_avg = delta / days if days > 0 else 0
        print(f"{GREEN}Reading logged: {kwh:.1f} kWh{RESET}")
        print(f"  Consumption: {delta:.1f} kWh in {days} day(s) ({daily_avg:.1f} kWh/day)")
    else:
        print(f"{GREEN}Reading logged: {kwh:.1f} kWh{RESET}")
    print()


def daily_report():
    today = _today()
    log = sorted(_load_log(), key=lambda r: r.get("date", ""))

    # Find today's and yesterday's readings for delta
    today_readings = [r for r in log if r.get("date") == today]
    yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
    yesterday_readings = [r for r in log if r.get("date") == yesterday]

    print(f"\n{BOLD}Energy Report — {today}:{RESET}\n")
    if today_readings:
        latest = today_readings[-1]
        print(f"  Latest reading: {GREEN}{latest.get('kwh', 0):.1f} kWh{RESET}")
        if yesterday_readings:
            delta = latest.get("kwh", 0) - yesterday_readings[-1].get("kwh", 0)
            color = GREEN if delta < 20 else (YELLOW if delta < 40 else RED)
            print(f"  Today's usage:  {color}{delta:.1f} kWh{RESET}")
    else:
        print(f"  {YELLOW}No readings for today.{RESET}")

    # Last 7 days
    if log:
        print(f"\n  {BOLD}Last 7 Readings:{RESET}")
        for r in log[-7:]:
            print(f"    {CYAN}{r.get('date')}{RESET}  {r.get('kwh', 0):.1f} kWh")
    print()


def monthly_summary():
    month = _current_month()
    log = sorted(_load_log(), key=lambda r: r.get("date", ""))
    month_data = [r for r in log if r.get("date", "").startswith(month)]

    if len(month_data) < 2:
        print(f"{YELLOW}Not enough data for {month} (need at least 2 readings).{RESET}")
        return

    total_kwh = month_data[-1].get("kwh", 0) - month_data[0].get("kwh", 0)
    days = max(1, (datetime.strptime(month_data[-1]["date"], "%Y-%m-%d") -
                   datetime.strptime(month_data[0]["date"], "%Y-%m-%d")).days)
    daily_avg = total_kwh / days

    print(f"\n{BOLD}Monthly Summary — {month}:{RESET}\n")
    print(f"  Total consumption: {GREEN}{total_kwh:.1f} kWh{RESET}")
    print(f"  Daily average:     {daily_avg:.1f} kWh/day")
    print(f"  Days tracked:      {days}")
    print()


def cost_estimate(kwh: float, rate: float = 0.12, peak_rate: float = 0, peak_pct: float = 0):
    if peak_rate and peak_pct:
        peak_kwh = kwh * (peak_pct / 100)
        off_kwh  = kwh - peak_kwh
        cost = (peak_kwh * peak_rate) + (off_kwh * rate)
        print(f"\n{BOLD}Energy Cost Estimate:{RESET}")
        print(f"  Peak usage:    {peak_kwh:.1f} kWh × ${peak_rate:.3f} = ${peak_kwh * peak_rate:.2f}")
        print(f"  Off-peak:      {off_kwh:.1f} kWh × ${rate:.3f} = ${off_kwh * rate:.2f}")
        print(f"  {BOLD}Total: {GREEN}${cost:.2f}{RESET}")
    else:
        cost = kwh * rate
        print(f"\n{BOLD}Energy Cost Estimate:{RESET}")
        print(f"  Usage: {kwh:.1f} kWh × ${rate:.4f}/kWh = {GREEN}${cost:.2f}{RESET}")

    monthly = cost * 30 / (kwh / 30) if kwh > 0 else cost
    print(f"  Estimated monthly: ${monthly:.2f}")
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="energy_monitor.py",
        description="Energy Monitor — OC-0167"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("current-usage", help="Get current energy readings")
    sub.add_parser("daily-report", help="Show daily consumption report")
    sub.add_parser("monthly-summary", help="Show monthly summary")

    p = sub.add_parser("log-reading", help="Log a manual meter reading")
    p.add_argument("--kwh", type=float, required=True, help="Meter reading in kWh")
    p.add_argument("--notes", default="")

    p = sub.add_parser("cost-estimate", help="Estimate energy cost")
    p.add_argument("--kwh", type=float, required=True)
    p.add_argument("--rate", type=float, default=0.12, help="Rate per kWh (default: $0.12)")
    p.add_argument("--peak-rate", type=float, default=0)
    p.add_argument("--peak-pct", type=float, default=0, help="Percentage as peak usage")

    args = parser.parse_args()
    dispatch = {
        "current-usage":   lambda: current_usage(),
        "daily-report":    lambda: daily_report(),
        "monthly-summary": lambda: monthly_summary(),
        "log-reading":     lambda: log_reading(args.kwh, args.notes),
        "cost-estimate":   lambda: cost_estimate(args.kwh, args.rate,
                                                   args.peak_rate, args.peak_pct),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()

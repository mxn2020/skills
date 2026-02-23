#!/usr/bin/env python3
"""
Smart Appliance Scheduler — OC-0169
Schedule dishwashers, EV charging, etc. for off-peak hours.
"""

import os
import sys
import json
import uuid
import argparse
from datetime import datetime, timezone, timedelta
import requests

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

SCHEDULES_FILE = os.path.expanduser("~/.appliance_schedules.json")


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _load_schedules() -> list:
    if os.path.exists(SCHEDULES_FILE):
        try:
            with open(SCHEDULES_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return []


def _save_schedules(data: list):
    with open(SCHEDULES_FILE, "w") as f:
        json.dump(data, f, indent=2)


def _ha_call(service_domain: str, service: str, entity_id: str) -> bool:
    base  = os.environ.get("HOME_ASSISTANT_URL", "")
    token = os.environ.get("HOME_ASSISTANT_TOKEN", "")
    if not base or not token:
        print(f"{YELLOW}HOME_ASSISTANT_URL/TOKEN not set. Simulating action.{RESET}")
        return True
    resp = requests.post(
        f"{base.rstrip('/')}/api/services/{service_domain}/{service}",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"entity_id": entity_id},
        timeout=10,
    )
    return resp.ok


def schedule(entity_id: str, run_at: str, duration_min: int = 60, label: str = ""):
    schedules = _load_schedules()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    schedule_id = str(uuid.uuid4())[:8]

    entry = {
        "id": schedule_id,
        "entity_id": entity_id,
        "label": label or entity_id,
        "date": today,
        "run_at": run_at,
        "duration_min": duration_min,
        "status": "scheduled",
        "created": datetime.now(timezone.utc).isoformat(),
    }
    schedules.append(entry)
    _save_schedules(schedules)

    print(f"{GREEN}Scheduled: {label or entity_id}{RESET}")
    print(f"  ID:       {schedule_id}")
    print(f"  Entity:   {entity_id}")
    print(f"  Run at:   {today} {run_at}")
    print(f"  Duration: {duration_min} minutes")
    print()
    print(f"{YELLOW}Note: Use a cron job or Home Assistant automation to trigger at the scheduled time.{RESET}")
    print(f"  Command: python3 smart_appliance_scheduler.py run-now --entity-id {entity_id} --duration {duration_min}")
    print()


def list_schedules():
    schedules = _load_schedules()
    if not schedules:
        print(f"{YELLOW}No schedules found.{RESET}")
        return

    print(f"\n{BOLD}Appliance Schedules ({len(schedules)}):{RESET}\n")
    for s in sorted(schedules, key=lambda x: x.get("run_at", "")):
        status = s.get("status", "scheduled")
        color  = GREEN if status == "completed" else (YELLOW if status == "scheduled" else RED)
        print(f"  {CYAN}{s.get('id', '')}{RESET}  {BOLD}{s.get('label', '')}{RESET}")
        print(f"    Entity:   {s.get('entity_id', '')}")
        print(f"    Run at:   {s.get('date', '')} {s.get('run_at', '')}")
        print(f"    Duration: {s.get('duration_min', 0)} min  |  "
              f"Status: {color}{status}{RESET}")
        print()


def cancel(schedule_id: str):
    schedules = _load_schedules()
    for s in schedules:
        if s.get("id") == schedule_id:
            s["status"] = "cancelled"
            _save_schedules(schedules)
            print(f"{GREEN}Schedule {schedule_id} cancelled.{RESET}")
            return
    _die(f"Schedule '{schedule_id}' not found.")


def off_peak_windows(peak_start: int = 16, peak_end: int = 21):
    """Show off-peak hours (outside peak window)."""
    print(f"\n{BOLD}Electricity Windows — Today:{RESET}\n")
    print(f"  Peak hours:     {YELLOW}{peak_start:02d}:00 – {peak_end:02d}:00{RESET}  (avoid high cost)")
    print(f"  {BOLD}Off-peak windows:{RESET}")

    now = datetime.now(timezone.utc).hour
    windows = []
    if peak_end <= 24:
        windows.append((peak_end, 24, "evening/overnight"))
    if peak_start > 0:
        windows.append((0, peak_start, "overnight/morning"))

    for start_h, end_h, label in windows:
        color = GREEN if now < peak_start or now >= peak_end else CYAN
        print(f"  {color}  {start_h:02d}:00 – {end_h:02d}:00{RESET}  "
              f"({end_h - start_h}h window, {label})")

    # Recommended scheduling
    best_start = peak_end
    print(f"\n  {GREEN}Best time to start heavy appliances: {best_start:02d}:00{RESET}")
    print(f"  (Avoids peak hours {peak_start}:00-{peak_end}:00)\n")

    # Typical appliance durations
    print(f"  {BOLD}Typical Durations:{RESET}")
    for appliance, mins in [("Dishwasher", 90), ("Washing Machine", 60),
                             ("Dryer", 45), ("EV Charge (full)", 480)]:
        start = best_start
        end_h = (best_start * 60 + mins) // 60
        end_m = (best_start * 60 + mins) % 60
        print(f"    {appliance:<22} {mins} min  →  "
              f"{start:02d}:00 – {end_h:02d}:{end_m:02d}")
    print()


def run_now(entity_id: str, duration_min: int = 60):
    print(f"{YELLOW}Turning on {entity_id}...{RESET}")
    if _ha_call("switch", "turn_on", entity_id):
        print(f"{GREEN}Turned ON: {entity_id}{RESET}")
        print(f"  Duration: {duration_min} minutes")
        print(f"  Will complete at: ~{(datetime.now(timezone.utc) + timedelta(minutes=duration_min)).strftime('%H:%M')} UTC")
        print()
        print(f"{YELLOW}To turn off after {duration_min} minutes, run:{RESET}")
        print(f"  sleep {duration_min * 60} && python3 smart_appliance_scheduler.py "
              f"run-now --entity-id {entity_id.replace('on', 'off')} --action off")
    else:
        print(f"{RED}Failed to control {entity_id}.{RESET}")


def main():
    parser = argparse.ArgumentParser(
        prog="smart_appliance_scheduler.py",
        description="Smart Appliance Scheduler — OC-0169"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("schedule", help="Schedule an appliance")
    p.add_argument("--entity-id", required=True)
    p.add_argument("--at", required=True, help="Start time HH:MM")
    p.add_argument("--duration", type=int, default=60, help="Duration in minutes")
    p.add_argument("--label", default="")

    sub.add_parser("list-schedules", help="Show all schedules")

    p = sub.add_parser("cancel", help="Cancel a schedule")
    p.add_argument("--schedule-id", required=True)

    p = sub.add_parser("off-peak-windows", help="Show off-peak time windows")
    p.add_argument("--peak-start", type=int, default=16, help="Peak start hour (default: 16)")
    p.add_argument("--peak-end", type=int, default=21, help="Peak end hour (default: 21)")

    p = sub.add_parser("run-now", help="Immediately run an appliance")
    p.add_argument("--entity-id", required=True)
    p.add_argument("--duration", type=int, default=60, help="Duration in minutes")

    args = parser.parse_args()
    dispatch = {
        "schedule":         lambda: schedule(args.entity_id, args.at,
                                              args.duration, args.label),
        "list-schedules":   lambda: list_schedules(),
        "cancel":           lambda: cancel(args.schedule_id),
        "off-peak-windows": lambda: off_peak_windows(args.peak_start, args.peak_end),
        "run-now":          lambda: run_now(args.entity_id, args.duration),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()

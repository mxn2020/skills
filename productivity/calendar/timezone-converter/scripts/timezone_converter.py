#!/usr/bin/env python3
"""
Time Zone Converter — OC-0136
Resolve scheduling across multiple time zones intelligently.
"""

import sys
import argparse
from datetime import datetime, time as dtime

RED    = "\033[91m"
GREEN  = "\033[92m"
YELLOW = "\033[93m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

try:
    import pytz
except ImportError:
    print(f"{RED}Error: pytz is required. Install with: pip install pytz{RESET}", file=sys.stderr)
    sys.exit(1)

COMMON_ZONES = {
    "US": [
        "America/New_York", "America/Chicago", "America/Denver",
        "America/Los_Angeles", "America/Anchorage", "Pacific/Honolulu",
    ],
    "Europe": [
        "Europe/London", "Europe/Paris", "Europe/Berlin",
        "Europe/Amsterdam", "Europe/Stockholm", "Europe/Moscow",
    ],
    "Asia": [
        "Asia/Dubai", "Asia/Kolkata", "Asia/Singapore",
        "Asia/Shanghai", "Asia/Tokyo", "Asia/Seoul",
    ],
    "Pacific": [
        "Australia/Sydney", "Pacific/Auckland", "Pacific/Auckland",
    ],
    "Americas": [
        "America/Toronto", "America/Vancouver", "America/Sao_Paulo",
        "America/Mexico_City", "America/Buenos_Aires",
    ],
}


def _die(msg: str):
    print(f"{RED}Error: {msg}{RESET}", file=sys.stderr)
    sys.exit(1)


def _parse_tz(zone: str) -> pytz.BaseTzInfo:
    try:
        return pytz.timezone(zone.strip())
    except pytz.UnknownTimeZoneError:
        _die(f"Unknown time zone: '{zone}'. Use 'list-zones' to see valid options.")


def convert(time_str: str, from_zone: str, to_zones_str: str):
    src_tz = _parse_tz(from_zone)
    try:
        naive = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
    except ValueError:
        _die("Time format must be: YYYY-MM-DD HH:MM (e.g. '2024-12-15 09:00')")

    aware = src_tz.localize(naive)
    print(f"\n{BOLD}Time Conversion:{RESET}")
    print(f"  {CYAN}{from_zone}{RESET}: {aware.strftime('%Y-%m-%d %H:%M %Z')}")

    for zone_str in to_zones_str.split(","):
        zone_str = zone_str.strip()
        if not zone_str:
            continue
        target_tz = _parse_tz(zone_str)
        converted = aware.astimezone(target_tz)
        # Color based on business hours
        hour = converted.hour
        if 9 <= hour < 18:
            color = GREEN
        elif 7 <= hour < 20:
            color = YELLOW
        else:
            color = RED
        print(f"  {color}{zone_str}{RESET}: {converted.strftime('%Y-%m-%d %H:%M %Z')}")
    print()


def list_zones(region: str = None):
    if region:
        region = region.upper()
        zones = COMMON_ZONES.get(region)
        if not zones:
            available = ", ".join(COMMON_ZONES.keys())
            _die(f"Unknown region '{region}'. Available: {available}")
        print(f"\n{BOLD}Time zones — {region}:{RESET}")
        for z in zones:
            tz = _parse_tz(z)
            now = datetime.now(tz)
            print(f"  {CYAN}{z}{RESET}  (now: {now.strftime('%H:%M %Z')})")
    else:
        for region_name, zones in COMMON_ZONES.items():
            print(f"\n{BOLD}{region_name}:{RESET}")
            for z in zones:
                print(f"  {z}")
    print()


def now(zones_str: str):
    utc_now = datetime.now(pytz.utc)
    print(f"\n{BOLD}Current Time:{RESET}")
    print(f"  {CYAN}UTC{RESET}: {utc_now.strftime('%Y-%m-%d %H:%M:%S %Z')}\n")
    for zone_str in zones_str.split(","):
        zone_str = zone_str.strip()
        if not zone_str:
            continue
        tz = _parse_tz(zone_str)
        local_now = utc_now.astimezone(tz)
        hour = local_now.hour
        if 9 <= hour < 18:
            color = GREEN
            note = "(business hours)"
        elif 7 <= hour < 20:
            color = YELLOW
            note = "(early/late)"
        else:
            color = RED
            note = "(off hours)"
        print(f"  {color}{zone_str}{RESET}: {local_now.strftime('%Y-%m-%d %H:%M %Z')} {note}")
    print()


def best_time(zones_str: str, work_start: int = 9, work_end: int = 17):
    zones = [_parse_tz(z.strip()) for z in zones_str.split(",") if z.strip()]
    if len(zones) < 2:
        _die("Provide at least 2 time zones to find overlap.")

    today = datetime.now(pytz.utc).date()
    overlapping = []

    # Check each hour of the day in UTC
    for hour in range(0, 24):
        utc_dt = pytz.utc.localize(datetime(today.year, today.month, today.day, hour, 0))
        all_business = all(
            work_start <= utc_dt.astimezone(tz).hour < work_end
            for tz in zones
        )
        if all_business:
            overlapping.append(utc_dt)

    print(f"\n{BOLD}Best Meeting Times (all zones in business hours {work_start:02d}:00-{work_end:02d}:00):{RESET}")

    zone_names = zones_str.split(",")
    if not overlapping:
        print(f"  {RED}No overlapping business hours found.{RESET}")
        # Show best partial overlaps
        print(f"\n{YELLOW}Partial overlap options (showing UTC times):{RESET}")
        for hour in range(0, 24):
            utc_dt = pytz.utc.localize(datetime(today.year, today.month, today.day, hour, 0))
            hits = sum(
                1 for tz in zones
                if work_start <= utc_dt.astimezone(tz).hour < work_end
            )
            if hits >= len(zones) - 1:
                converted = [utc_dt.astimezone(_parse_tz(z.strip())).strftime("%H:%M %Z")
                             for z in zone_names]
                print(f"  {YELLOW}{' | '.join(converted)}{RESET} ({hits}/{len(zones)} zones)")
    else:
        for slot in overlapping:
            converted = [slot.astimezone(_parse_tz(z.strip())).strftime("%H:%M %Z")
                         for z in zone_names]
            print(f"  {GREEN}{' | '.join(converted)}{RESET}")
    print()


def main():
    parser = argparse.ArgumentParser(
        prog="timezone_converter.py",
        description="Time Zone Converter — OC-0136"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("convert", help="Convert time from one zone to others")
    p.add_argument("--time", required=True, help="Time in format 'YYYY-MM-DD HH:MM'")
    p.add_argument("--from-zone", required=True, help="Source time zone")
    p.add_argument("--to-zones", required=True, help="Comma-separated target zones")

    p = sub.add_parser("list-zones", help="List common time zones")
    p.add_argument("--region", default=None, help="Region: US, Europe, Asia, Pacific, Americas")

    p = sub.add_parser("now", help="Show current time in multiple zones")
    p.add_argument("--zones", required=True, help="Comma-separated time zones")

    p = sub.add_parser("best-time", help="Find best meeting overlap for zones")
    p.add_argument("--zones", required=True, help="Comma-separated time zones")
    p.add_argument("--work-start", type=int, default=9, help="Business hours start (default: 9)")
    p.add_argument("--work-end", type=int, default=17, help="Business hours end (default: 17)")

    args = parser.parse_args()
    dispatch = {
        "convert":    lambda: convert(args.time, args.from_zone, args.to_zones),
        "list-zones": lambda: list_zones(args.region),
        "now":        lambda: now(args.zones),
        "best-time":  lambda: best_time(args.zones, args.work_start, args.work_end),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()

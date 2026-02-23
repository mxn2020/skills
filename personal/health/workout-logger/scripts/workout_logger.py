#!/usr/bin/env python3
"""
Workout Logger — OC-0141
Log exercises to a local store or Strava via API.
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

LOG_FILE = os.path.expanduser("~/.workout_log.json")
STRAVA_URL = "https://www.strava.com/api/v3"

WORKOUT_TYPES = {
    "run": "Run", "ride": "Ride", "swim": "Swim",
    "strength": "WeightTraining", "yoga": "Yoga", "walk": "Walk",
    "hike": "Hike", "crossfit": "Crossfit", "other": "Workout",
}


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


def _save_log(workouts: list):
    with open(LOG_FILE, "w") as f:
        json.dump(workouts, f, indent=2)


def log_workout(workout_type: str, duration: int, distance: float = 0.0,
                calories: int = 0, notes: str = ""):
    wtype = workout_type.lower()
    if wtype not in WORKOUT_TYPES:
        available = ", ".join(WORKOUT_TYPES.keys())
        _die(f"Unknown workout type '{wtype}'. Available: {available}")

    workout = {
        "id": str(uuid.uuid4())[:8],
        "type": wtype,
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M"),
        "duration_min": duration,
        "distance_km": distance,
        "calories": calories,
        "notes": notes,
    }
    workouts = _load_log()
    workouts.append(workout)
    _save_log(workouts)

    print(f"{GREEN}Workout logged:{RESET}")
    print(f"  ID:        {CYAN}{workout['id']}{RESET}")
    print(f"  Type:      {workout['type']}")
    print(f"  Duration:  {duration} min")
    if distance:
        print(f"  Distance:  {distance} km")
    if calories:
        print(f"  Calories:  {calories} kcal")
    if notes:
        print(f"  Notes:     {notes}")
    print()


def list_workouts(limit: int = 10):
    workouts = _load_log()
    if not workouts:
        print(f"{YELLOW}No workouts logged yet.{RESET}")
        return
    recent = sorted(workouts, key=lambda w: w.get("date", ""), reverse=True)[:limit]
    print(f"\n{BOLD}Recent Workouts:{RESET}\n")
    for w in recent:
        dist = f"  {w.get('distance_km', 0):.1f}km" if w.get("distance_km") else ""
        cal  = f"  {w.get('calories', 0)} kcal" if w.get("calories") else ""
        print(f"  {CYAN}{w['id']}{RESET}  {BOLD}{w.get('type', '').upper()}{RESET}  "
              f"{w.get('date', '')}")
        print(f"    {w.get('duration_min', 0)} min{dist}{cal}")
        if w.get("notes"):
            print(f"    {YELLOW}{w['notes']}{RESET}")
        print()


def summary(period: str = "week"):
    workouts = _load_log()
    now = datetime.now(timezone.utc)
    if period == "week":
        cutoff = now - timedelta(days=7)
        label = "Last 7 Days"
    elif period == "month":
        cutoff = now - timedelta(days=30)
        label = "Last 30 Days"
    else:
        cutoff = now - timedelta(days=365)
        label = "Last Year"

    recent = [
        w for w in workouts
        if datetime.fromisoformat(w.get("date", "2000-01-01").replace(" ", "T")).replace(
            tzinfo=timezone.utc) >= cutoff
    ]

    if not recent:
        print(f"{YELLOW}No workouts in the {label.lower()}.{RESET}")
        return

    total_dur = sum(w.get("duration_min", 0) for w in recent)
    total_cal = sum(w.get("calories", 0) for w in recent)
    total_dist = sum(w.get("distance_km", 0) for w in recent)
    by_type: dict = {}
    for w in recent:
        by_type[w.get("type", "other")] = by_type.get(w.get("type", "other"), 0) + 1

    print(f"\n{BOLD}Workout Summary — {label}:{RESET}\n")
    print(f"  Total workouts: {GREEN}{len(recent)}{RESET}")
    print(f"  Total time:     {GREEN}{total_dur} min ({total_dur // 60}h {total_dur % 60}m){RESET}")
    if total_dist:
        print(f"  Total distance: {GREEN}{total_dist:.1f} km{RESET}")
    if total_cal:
        print(f"  Total calories: {GREEN}{total_cal} kcal{RESET}")
    print(f"\n  {BOLD}By Type:{RESET}")
    for wtype, count in sorted(by_type.items(), key=lambda x: x[1], reverse=True):
        print(f"    {CYAN}{wtype}{RESET}: {count} session(s)")
    print()


def upload_strava(workout_id: str):
    token = os.environ.get("STRAVA_ACCESS_TOKEN", "")
    if not token:
        _die("STRAVA_ACCESS_TOKEN is not set.")

    workouts = _load_log()
    workout = next((w for w in workouts if w.get("id") == workout_id), None)
    if not workout:
        _die(f"Workout '{workout_id}' not found. Use 'list' to see IDs.")

    strava_type = WORKOUT_TYPES.get(workout.get("type", "other"), "Workout")
    start_dt = datetime.strptime(workout["date"], "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc)

    payload = {
        "name": workout.get("notes") or f"{workout['type'].capitalize()} Workout",
        "type": strava_type,
        "start_date_local": start_dt.isoformat(),
        "elapsed_time": workout.get("duration_min", 0) * 60,
        "description": workout.get("notes", ""),
    }
    if workout.get("distance_km"):
        payload["distance"] = workout["distance_km"] * 1000

    resp = requests.post(
        f"{STRAVA_URL}/activities",
        headers={"Authorization": f"Bearer {token}"},
        json=payload,
        timeout=30,
    )
    if not resp.ok:
        _die(f"Strava API {resp.status_code}: {resp.text[:300]}")
    activity = resp.json()
    print(f"{GREEN}Uploaded to Strava:{RESET}")
    print(f"  Activity ID: {activity.get('id')}")
    print(f"  Name: {activity.get('name')}")
    print(f"  URL: https://www.strava.com/activities/{activity.get('id')}")


def main():
    parser = argparse.ArgumentParser(
        prog="workout_logger.py",
        description="Workout Logger — OC-0141"
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("log", help="Log a new workout")
    p.add_argument("--type", required=True, choices=list(WORKOUT_TYPES.keys()))
    p.add_argument("--duration", type=int, required=True, help="Duration in minutes")
    p.add_argument("--distance", type=float, default=0.0, help="Distance in km")
    p.add_argument("--calories", type=int, default=0)
    p.add_argument("--notes", default="")

    p = sub.add_parser("list", help="List recent workouts")
    p.add_argument("--limit", type=int, default=10)

    p = sub.add_parser("summary", help="Show workout summary")
    p.add_argument("--period", default="week", choices=["week", "month", "year"])

    p = sub.add_parser("upload-strava", help="Upload a workout to Strava")
    p.add_argument("--workout-id", required=True)

    args = parser.parse_args()
    dispatch = {
        "log":            lambda: log_workout(args.type, args.duration, args.distance,
                                               args.calories, args.notes),
        "list":           lambda: list_workouts(args.limit),
        "summary":        lambda: summary(args.period),
        "upload-strava":  lambda: upload_strava(args.workout_id),
    }
    dispatch[args.cmd]()


if __name__ == "__main__":
    main()

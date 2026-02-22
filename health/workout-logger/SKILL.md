---
name: workout-logger
id: OC-0141
version: 1.0.0
description: "Workout Logger - Log exercises to a local store or Strava via API"
env:
  - STRAVA_ACCESS_TOKEN
commands:
  - log
  - list
  - summary
  - upload-strava
---

# Workout Logger

Log workouts locally and optionally sync them to Strava. Track exercises, duration, distance, and calories.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- `STRAVA_ACCESS_TOKEN` — Strava API access token (optional, for Strava sync)

## Commands

| Command | Description |
|---------|-------------|
| `log` | Log a new workout |
| `list` | List recent workouts |
| `summary` | Show weekly/monthly workout summary |
| `upload-strava` | Upload a workout to Strava |

## Usage

```bash
export STRAVA_ACCESS_TOKEN="your_token"  # optional

# Log a run
python3 scripts/workout_logger.py log --type run --duration 30 --distance 5.0 --calories 350 --notes "Morning 5K"

# Log a strength workout
python3 scripts/workout_logger.py log --type strength --duration 45 --calories 280 --notes "Upper body day"

# List recent workouts
python3 scripts/workout_logger.py list --limit 10

# Show weekly summary
python3 scripts/workout_logger.py summary --period week

# Upload last workout to Strava
python3 scripts/workout_logger.py upload-strava --workout-id WORKOUT_ID
```

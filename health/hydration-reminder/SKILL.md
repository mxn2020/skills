---
name: hydration-reminder
id: OC-0145
version: 1.0.0
description: "Hydration Reminder - Smart recurring reminders adjusted for activity level and climate"
env: []
commands:
  - log-intake
  - daily-summary
  - set-goal
  - check
---

# Hydration Reminder

Track daily water intake, get smart hydration recommendations based on weight and activity level, and monitor your hydration goals.

## Prerequisites

- Python 3.8+

## Commands

| Command | Description |
|---------|-------------|
| `log-intake` | Log a water intake entry |
| `daily-summary` | Show today's hydration progress |
| `set-goal` | Set personalized daily hydration goal |
| `check` | Quick check of current hydration status |

## Usage

```bash
# Log water intake (in ml)
python3 scripts/hydration_reminder.py log-intake --amount 500

# Log a coffee (counts partially toward hydration)
python3 scripts/hydration_reminder.py log-intake --amount 250 --type coffee

# Show today's hydration progress
python3 scripts/hydration_reminder.py daily-summary

# Set a custom goal based on weight and activity
python3 scripts/hydration_reminder.py set-goal --weight-kg 75 --activity moderate

# Quick status check
python3 scripts/hydration_reminder.py check
```

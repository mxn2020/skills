---
name: habit-streaks
id: OC-0147
version: 1.0.0
description: "Habit Streaks - Track daily habits such as reading, coding, and running"
env: []
commands:
  - add-habit
  - check-in
  - status
  - history
  - remove-habit
---

# Habit Streaks

Track daily habits, maintain streaks, and build consistent routines. Works entirely offline.

## Prerequisites

- Python 3.8+

## Commands

| Command | Description |
|---------|-------------|
| `add-habit` | Add a new habit to track |
| `check-in` | Mark a habit as done for today |
| `status` | Show all habits and current streaks |
| `history` | View habit completion history |
| `remove-habit` | Remove a habit |

## Usage

```bash
# Add a new habit
python3 scripts/habit_streaks.py add-habit --name "Read 30 min" --emoji "📚"

# Check in a habit for today
python3 scripts/habit_streaks.py check-in --name "Read 30 min"

# View all habits and streaks
python3 scripts/habit_streaks.py status

# View history for a habit
python3 scripts/habit_streaks.py history --name "Read 30 min" --days 30

# Remove a habit
python3 scripts/habit_streaks.py remove-habit --name "Read 30 min"
```

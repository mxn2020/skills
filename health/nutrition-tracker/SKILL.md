---
name: nutrition-tracker
id: OC-0142
version: 1.0.0
description: "Nutrition Tracker - Estimate calories from food descriptions and track daily intake"
env:
  - OPENAI_API_KEY
commands:
  - log-meal
  - estimate
  - daily-summary
  - set-goals
---

# Nutrition Tracker

Track daily nutrition by logging meals, estimating calories from natural language descriptions, and reviewing intake summaries.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- `OPENAI_API_KEY` — for AI-based food estimation

## Commands

| Command | Description |
|---------|-------------|
| `log-meal` | Log a meal with food items |
| `estimate` | Estimate calories from a food description |
| `daily-summary` | Show today's nutrition summary |
| `set-goals` | Set daily calorie and macro goals |

## Usage

```bash
export OPENAI_API_KEY="your_key"

# Estimate calories from description
python3 scripts/nutrition_tracker.py estimate --food "two scrambled eggs with toast and orange juice"

# Log a meal
python3 scripts/nutrition_tracker.py log-meal --meal breakfast --food "oatmeal with banana and coffee"

# Show today's summary
python3 scripts/nutrition_tracker.py daily-summary

# Set daily goals
python3 scripts/nutrition_tracker.py set-goals --calories 2000 --protein 150 --carbs 200 --fat 65
```

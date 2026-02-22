---
name: travel-planner
id: OC-0173
version: 1.0.0
description: "Travel Planner - Build multi-day itineraries with flights, hotels, and activities"
env:
  - OPENAI_API_KEY
commands:
  - itinerary
  - budget
  - packing-list
  - visa-check
---

# Travel Planner

Build detailed multi-day travel itineraries with day-by-day plans, budget estimates, packing lists, and visa/entry requirements.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- `OPENAI_API_KEY` — for AI itinerary generation

## Commands

| Command | Description |
|---------|-------------|
| `itinerary` | Generate a detailed day-by-day itinerary |
| `budget` | Create a travel budget breakdown |
| `packing-list` | Generate a customized packing list |
| `visa-check` | Check visa requirements for a destination |

## Usage

```bash
export OPENAI_API_KEY="your_key"

# Generate a 7-day Italy itinerary
python3 scripts/travel_planner.py itinerary --destination "Italy" --days 7 --style cultural --budget mid-range

# Create budget estimate
python3 scripts/travel_planner.py budget --destination "Thailand" --days 14 --travelers 2 --style backpacker

# Get packing list
python3 scripts/travel_planner.py packing-list --destination "Iceland" --days 5 --season winter --activities "hiking,hot springs"

# Check visa requirements
python3 scripts/travel_planner.py visa-check --destination "Japan" --passport "US"
```

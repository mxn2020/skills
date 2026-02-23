---
name: timezone-converter
id: OC-0136
version: 1.0.0
description: "Time Zone Converter - Resolve scheduling across multiple time zones intelligently"
env: []
commands:
  - convert
  - list-zones
  - best-time
  - now
---

# Time Zone Converter

Resolve scheduling across multiple time zones. Convert times, find overlapping business hours, and pick the best meeting time for distributed teams.

## Prerequisites

- Python 3.8+
- `pytz` library (`pip install pytz`)

## Commands

| Command | Description |
|---------|-------------|
| `convert` | Convert a time from one zone to others |
| `list-zones` | List common time zones by region |
| `best-time` | Find best meeting overlap for a set of zones |
| `now` | Show current time in multiple zones |

## Usage

```bash
# Convert a specific time to multiple zones
python3 scripts/timezone_converter.py convert --time "2024-12-15 09:00" --from-zone "America/New_York" --to-zones "Europe/London,Asia/Tokyo,America/Los_Angeles"

# Show current time in multiple zones
python3 scripts/timezone_converter.py now --zones "America/New_York,Europe/London,Asia/Singapore"

# Find best meeting time (9am-5pm overlap) for multiple zones
python3 scripts/timezone_converter.py best-time --zones "America/New_York,Europe/London,Asia/Tokyo"

# List all zones in a region
python3 scripts/timezone_converter.py list-zones --region US
```

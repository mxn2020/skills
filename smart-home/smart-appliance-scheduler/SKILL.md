---
name: smart-appliance-scheduler
id: OC-0169
version: 1.0.0
description: "Smart Appliance Scheduler - Schedule dishwashers, EV charging for off-peak hours"
env:
  - HOME_ASSISTANT_URL
  - HOME_ASSISTANT_TOKEN
commands:
  - schedule
  - list-schedules
  - cancel
  - off-peak-windows
  - run-now
---

# Smart Appliance Scheduler

Schedule smart appliances to run during off-peak electricity hours to reduce costs. Integrates with Home Assistant for smart plug and switch control.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- `HOME_ASSISTANT_URL` — Home Assistant base URL
- `HOME_ASSISTANT_TOKEN` — Long-lived access token

## Commands

| Command | Description |
|---------|-------------|
| `schedule` | Schedule an appliance for off-peak hours |
| `list-schedules` | Show all scheduled tasks |
| `cancel` | Cancel a scheduled task |
| `off-peak-windows` | Show today's off-peak time windows |
| `run-now` | Trigger an appliance immediately |

## Usage

```bash
export HOME_ASSISTANT_URL="http://homeassistant.local:8123"
export HOME_ASSISTANT_TOKEN="your_token"

# Schedule EV charger for off-peak overnight
python3 scripts/smart_appliance_scheduler.py schedule --entity-id "switch.ev_charger" --at "02:00" --duration 240 --label "EV Charge"

# Show off-peak windows
python3 scripts/smart_appliance_scheduler.py off-peak-windows --peak-start 16 --peak-end 21

# List all schedules
python3 scripts/smart_appliance_scheduler.py list-schedules

# Run an appliance immediately
python3 scripts/smart_appliance_scheduler.py run-now --entity-id "switch.dishwasher" --duration 90
```

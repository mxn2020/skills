---
name: energy-monitor
id: OC-0167
version: 1.0.0
description: "Energy Monitor - Track and report home energy consumption trends"
env:
  - HOME_ASSISTANT_URL
  - HOME_ASSISTANT_TOKEN
commands:
  - current-usage
  - daily-report
  - monthly-summary
  - log-reading
  - cost-estimate
---

# Energy Monitor

Track and analyze home energy consumption. Integrates with Home Assistant sensors or manual readings to build consumption trends.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- `HOME_ASSISTANT_URL` — Home Assistant base URL (optional, for smart meter integration)
- `HOME_ASSISTANT_TOKEN` — Home Assistant long-lived access token (optional)

## Commands

| Command | Description |
|---------|-------------|
| `current-usage` | Get current energy readings from HA |
| `daily-report` | Show today's consumption report |
| `monthly-summary` | Show monthly usage and cost summary |
| `log-reading` | Manually log a meter reading |
| `cost-estimate` | Estimate energy cost |

## Usage

```bash
export HOME_ASSISTANT_URL="http://homeassistant.local:8123"
export HOME_ASSISTANT_TOKEN="your_token"

# Get current energy usage from Home Assistant
python3 scripts/energy_monitor.py current-usage

# View daily report
python3 scripts/energy_monitor.py daily-report

# Log a manual meter reading (kWh)
python3 scripts/energy_monitor.py log-reading --kwh 1234.5

# Estimate monthly cost
python3 scripts/energy_monitor.py cost-estimate --kwh 300 --rate 0.12
```

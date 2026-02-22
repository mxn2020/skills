---
name: pagerduty-incident
id: OC-0079
version: 1.0.0
description: "PagerDuty Incident Creator - Open and escalate incidents from monitoring triggers"
env:
  - PAGERDUTY_API_KEY
  - PAGERDUTY_FROM_EMAIL
commands:
  - create-incident
  - list-incidents
  - get-incident
  - acknowledge
  - resolve
---

# PagerDuty Incident Creator

Open and escalate PagerDuty incidents from monitoring triggers.

## Prerequisites

- `PAGERDUTY_API_KEY` – PagerDuty REST API key.
- `PAGERDUTY_FROM_EMAIL` – Email address of the user making changes.

## Commands

| Command            | Description                              |
|--------------------|------------------------------------------|
| `create-incident`  | Create a new incident on a service       |
| `list-incidents`   | List incidents with optional status filter |
| `get-incident`     | Get details for a specific incident      |
| `acknowledge`      | Acknowledge an incident                  |
| `resolve`          | Resolve an incident                      |

## Usage

```bash
export PAGERDUTY_API_KEY="your-api-key"
export PAGERDUTY_FROM_EMAIL="user@example.com"
python3 scripts/pagerduty_incident.py create-incident --title "High CPU usage" --service-id P000000 --urgency high --details "CPU > 95% for 10 min"
python3 scripts/pagerduty_incident.py list-incidents --status triggered
python3 scripts/pagerduty_incident.py get-incident --incident-id Q1234567890
python3 scripts/pagerduty_incident.py acknowledge --incident-id Q1234567890
python3 scripts/pagerduty_incident.py resolve --incident-id Q1234567890
```

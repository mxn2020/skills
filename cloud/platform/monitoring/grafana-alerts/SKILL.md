---
name: grafana-alerts
id: OC-0052
version: 1.0.0
description: "Grafana Alert Manager - Silence or acknowledge alerts"
env:
  - GRAFANA_URL
  - GRAFANA_API_KEY
commands:
  - list-alerts
  - silence
  - acknowledge
  - list-silences
  - delete-silence
---

# Grafana Alert Manager

Manage Grafana alerts: list firing alerts, create silences, acknowledge, and remove silences.

## Prerequisites

- `GRAFANA_URL` – Base URL of your Grafana instance (e.g. `https://grafana.example.com`).
- `GRAFANA_API_KEY` – Grafana API key with alerting permissions.

## Commands

| Command          | Description                              |
|------------------|------------------------------------------|
| `list-alerts`    | List currently firing alerts             |
| `silence`        | Create a silence for a matcher           |
| `acknowledge`    | Acknowledge a firing alert               |
| `list-silences`  | List active silences                     |
| `delete-silence` | Delete a silence by ID                   |

## Usage

```bash
export GRAFANA_URL="https://grafana.example.com"
export GRAFANA_API_KEY="your-api-key"
python3 scripts/grafana_alerts.py list-alerts
python3 scripts/grafana_alerts.py silence --matcher "alertname=HighCPU" --duration 2h
python3 scripts/grafana_alerts.py acknowledge --alert-id abc123
python3 scripts/grafana_alerts.py list-silences
python3 scripts/grafana_alerts.py delete-silence --silence-id def456
```

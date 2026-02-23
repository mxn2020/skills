---
name: datadog-snapshotter
id: OC-0051
version: 1.0.0
description: "Datadog Dashboard Snapshotter - Get PNG of health metrics"
env:
  - DD_API_KEY
  - DD_APP_KEY
commands:
  - list-dashboards
  - snapshot
  - list-monitors
  - get-monitor
  - mute-monitor
---

# Datadog Dashboard Snapshotter

Capture dashboard snapshots, list monitors, and mute alerts via the Datadog API.

## Prerequisites

- `DD_API_KEY` – Datadog API key.
- `DD_APP_KEY` – Datadog application key.

## Commands

| Command           | Description                              |
|-------------------|------------------------------------------|
| `list-dashboards` | List all dashboards                      |
| `snapshot`        | Take a PNG snapshot of a metric graph    |
| `list-monitors`   | List all monitors                        |
| `get-monitor`     | Get details for a specific monitor       |
| `mute-monitor`    | Mute a monitor                           |

## Usage

```bash
export DD_API_KEY="your-api-key"
export DD_APP_KEY="your-app-key"
python3 scripts/datadog_snapshotter.py list-dashboards
python3 scripts/datadog_snapshotter.py snapshot --metric "avg:system.cpu.user{*}" --start 1h
python3 scripts/datadog_snapshotter.py list-monitors
python3 scripts/datadog_snapshotter.py mute-monitor --monitor-id 12345
```

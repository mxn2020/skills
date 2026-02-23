---
name: plausible-reporter
id: OC-0058
version: 1.0.0
description: "Plausible Analytics Reporter - Pull web analytics summaries"
env:
  - PLAUSIBLE_URL
  - PLAUSIBLE_API_KEY
commands:
  - realtime
  - aggregate
  - timeseries
  - breakdown
  - list-sites
---

# Plausible Analytics Reporter

Query Plausible Analytics for real-time visitors, aggregate stats, time series, and breakdowns.

## Prerequisites

- `PLAUSIBLE_URL` – Plausible instance URL (e.g. `https://plausible.io`).
- `PLAUSIBLE_API_KEY` – Plausible API key.

## Commands

| Command       | Description                              |
|---------------|------------------------------------------|
| `realtime`    | Get current real-time visitor count      |
| `aggregate`   | Get aggregate stats for a period         |
| `timeseries`  | Get time series data for a metric        |
| `breakdown`   | Break down stats by a property           |
| `list-sites`  | List sites in the account                |

## Usage

```bash
export PLAUSIBLE_URL="https://plausible.io"
export PLAUSIBLE_API_KEY="your-api-key"
python3 scripts/plausible_reporter.py realtime --site-id example.com
python3 scripts/plausible_reporter.py aggregate --site-id example.com --period 30d
python3 scripts/plausible_reporter.py timeseries --site-id example.com --period 7d
python3 scripts/plausible_reporter.py breakdown --site-id example.com --property visit:source
python3 scripts/plausible_reporter.py list-sites
```

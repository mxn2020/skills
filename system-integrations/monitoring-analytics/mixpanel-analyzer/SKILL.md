---
name: mixpanel-analyzer
id: OC-0054
version: 1.0.0
description: "Mixpanel Cohort Analyzer - Query retention and funnel data"
env:
  - MIXPANEL_PROJECT_ID
  - MIXPANEL_SERVICE_ACCOUNT
  - MIXPANEL_SECRET
commands:
  - query-events
  - retention
  - funnels
  - list-cohorts
  - export
---

# Mixpanel Cohort Analyzer

Query Mixpanel for event analytics, retention curves, funnel conversion, and cohort data.

## Prerequisites

- `MIXPANEL_PROJECT_ID` – Mixpanel project ID.
- `MIXPANEL_SERVICE_ACCOUNT` – Mixpanel service account username.
- `MIXPANEL_SECRET` – Mixpanel service account secret.

## Commands

| Command        | Description                              |
|----------------|------------------------------------------|
| `query-events` | Query event counts over a date range     |
| `retention`    | Get retention data for an event          |
| `funnels`      | Query funnel conversion data             |
| `list-cohorts` | List saved cohorts                       |
| `export`       | Export raw event data                    |

## Usage

```bash
export MIXPANEL_PROJECT_ID="12345"
export MIXPANEL_SERVICE_ACCOUNT="user.abc123.mp-service-account"
export MIXPANEL_SECRET="your-secret"
python3 scripts/mixpanel_analyzer.py query-events --event "Sign Up" --from-date 2024-01-01 --to-date 2024-01-31
python3 scripts/mixpanel_analyzer.py retention --event "Login" --from-date 2024-01-01 --to-date 2024-01-31
python3 scripts/mixpanel_analyzer.py funnels --funnel-id 67890
python3 scripts/mixpanel_analyzer.py list-cohorts
python3 scripts/mixpanel_analyzer.py export --from-date 2024-01-01 --to-date 2024-01-02
```

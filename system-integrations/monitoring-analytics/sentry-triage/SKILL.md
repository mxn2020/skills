---
name: sentry-triage
id: OC-0050
version: 1.0.0
description: "Sentry Error Triage - Fetch recent exceptions and assign to developers"
env:
  - SENTRY_AUTH_TOKEN
  - SENTRY_ORG
  - SENTRY_PROJECT
commands:
  - list-issues
  - get-issue
  - assign
  - resolve
  - list-events
---

# Sentry Error Triage

Fetch recent Sentry exceptions, inspect details, assign to developers, and resolve issues.

## Prerequisites

- `SENTRY_AUTH_TOKEN` – Sentry API auth token.
- `SENTRY_ORG` – Sentry organization slug.
- `SENTRY_PROJECT` – Sentry project slug.

## Commands

| Command       | Description                              |
|---------------|------------------------------------------|
| `list-issues` | List recent unresolved issues            |
| `get-issue`   | Get details for a specific issue         |
| `assign`      | Assign an issue to a developer           |
| `resolve`     | Mark an issue as resolved                |
| `list-events` | List recent events for an issue          |

## Usage

```bash
export SENTRY_AUTH_TOKEN="your-token"
export SENTRY_ORG="my-org"
export SENTRY_PROJECT="my-project"
python3 scripts/sentry_triage.py list-issues --limit 10
python3 scripts/sentry_triage.py get-issue --issue-id 12345
python3 scripts/sentry_triage.py assign --issue-id 12345 --user user@example.com
python3 scripts/sentry_triage.py resolve --issue-id 12345
python3 scripts/sentry_triage.py list-events --issue-id 12345
```

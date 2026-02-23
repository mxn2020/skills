---
name: posthog-flags
id: OC-0055
version: 1.0.0
description: "PostHog Feature Flag Manager - Toggle features for users/cohorts"
env:
  - POSTHOG_URL
  - POSTHOG_API_KEY
commands:
  - list-flags
  - create-flag
  - update-flag
  - delete-flag
  - evaluate
---

# PostHog Feature Flag Manager

Manage PostHog feature flags: list, create, update, delete, and evaluate flags for users.

## Prerequisites

- `POSTHOG_URL` – PostHog instance URL (e.g. `https://app.posthog.com`).
- `POSTHOG_API_KEY` – PostHog personal API key.

## Commands

| Command       | Description                              |
|---------------|------------------------------------------|
| `list-flags`  | List all feature flags                   |
| `create-flag` | Create a new feature flag                |
| `update-flag` | Update an existing feature flag          |
| `delete-flag` | Delete a feature flag                    |
| `evaluate`    | Evaluate a flag for a given user         |

## Usage

```bash
export POSTHOG_URL="https://app.posthog.com"
export POSTHOG_API_KEY="your-api-key"
python3 scripts/posthog_flags.py list-flags
python3 scripts/posthog_flags.py create-flag --key new-feature --rollout 50
python3 scripts/posthog_flags.py update-flag --flag-id 123 --active true
python3 scripts/posthog_flags.py delete-flag --flag-id 123
python3 scripts/posthog_flags.py evaluate --key new-feature --distinct-id user-42
```

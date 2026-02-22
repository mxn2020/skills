---
name: linear-issue-manager
id: OC-0127
version: 1.0.0
description: "Linear Issue Manager - Manage Linear issues, cycles, and assignments via GraphQL API"
env:
  - LINEAR_API_KEY
commands:
  - list-issues
  - create-issue
  - update-issue
  - list-cycles
  - assign-issue
---

# Linear Issue Manager

Manage Linear issues, cycles, and team assignments directly from the CLI using the Linear GraphQL API.

## Prerequisites

- `LINEAR_API_KEY` — Linear personal API key (Settings → API → Personal API keys)
- `pip install requests`

## Commands

| Command | Description |
|---------|-------------|
| `list-issues` | List issues for a team filtered by state |
| `create-issue` | Create a new issue in a team |
| `update-issue` | Update issue state or priority |
| `list-cycles` | List cycles (sprints) for a team |
| `assign-issue` | Assign an issue to a team member |

## Usage

```bash
# List active issues for a team
python linear_issue_manager.py list-issues --team-id TEAM_ID

# List issues with a specific state
python linear_issue_manager.py list-issues --team-id TEAM_ID --state "In Progress"

# Create a new issue
python linear_issue_manager.py create-issue --team-id TEAM_ID --title "Fix login bug" --description "Users cannot log in" --priority 2

# Update an issue
python linear_issue_manager.py update-issue --id ISSUE_ID --state "Done" --priority 1

# List cycles for a team
python linear_issue_manager.py list-cycles --team-id TEAM_ID

# Assign issue to a user
python linear_issue_manager.py assign-issue --id ISSUE_ID --assignee-id USER_ID
```

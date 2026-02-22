---
name: jira-ticket-handler
id: OC-0128
version: 1.0.0
description: "Jira Ticket Handler - Manage Jira tickets, sprints, and workflow transitions"
env:
  - JIRA_BASE_URL
  - JIRA_EMAIL
  - JIRA_API_TOKEN
commands:
  - list-issues
  - create-ticket
  - update-ticket
  - list-sprints
  - move-to-sprint
---

# Jira Ticket Handler

Manage Jira issues, sprints, and workflow directly from the CLI using the Jira REST API v3.

## Prerequisites

- `JIRA_BASE_URL` — Your Jira instance URL (e.g., `https://yourcompany.atlassian.net`)
- `JIRA_EMAIL` — Your Atlassian account email
- `JIRA_API_TOKEN` — API token (Atlassian account settings → Security → API tokens)
- `pip install requests`

## Commands

| Command | Description |
|---------|-------------|
| `list-issues` | List issues in a project with optional JQL filter |
| `create-ticket` | Create a new Jira ticket |
| `update-ticket` | Update ticket status or assignee |
| `list-sprints` | List sprints on an agile board |
| `move-to-sprint` | Move a ticket to a specific sprint |

## Usage

```bash
# List issues in a project
python jira_ticket_handler.py list-issues --project-key PROJ

# List with JQL filter
python jira_ticket_handler.py list-issues --project-key PROJ --jql "status = 'In Progress'"

# Create a ticket
python jira_ticket_handler.py create-ticket --project-key PROJ --summary "Fix login bug" --description "Users cannot log in on mobile"

# Create a Bug type ticket
python jira_ticket_handler.py create-ticket --project-key PROJ --summary "NPE in auth" --issue-type Bug

# Update ticket status
python jira_ticket_handler.py update-ticket --key PROJ-123 --status "In Progress"

# List sprints on a board
python jira_ticket_handler.py list-sprints --board-id 1

# Move ticket to sprint
python jira_ticket_handler.py move-to-sprint --ticket-key PROJ-123 --sprint-id 42
```

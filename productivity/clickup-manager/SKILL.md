---
name: clickup-manager
id: OC-0132
version: 1.0.0
description: "ClickUp Manager - Manage ClickUp tasks, spaces, and lists via REST API v2"
env:
  - CLICKUP_API_TOKEN
  - CLICKUP_WORKSPACE_ID
commands:
  - list-tasks
  - create-task
  - update-task
  - list-spaces
  - list-lists
---

# ClickUp Manager

Manage ClickUp tasks, spaces, and lists from the CLI using the ClickUp REST API v2.

## Prerequisites

- `CLICKUP_API_TOKEN` — ClickUp personal API token (Settings → Apps → API Token)
- `CLICKUP_WORKSPACE_ID` — Your workspace/team ID (needed for list-spaces)
- `pip install requests`

## Commands

| Command | Description |
|---------|-------------|
| `list-tasks` | List tasks in a list with optional status filter |
| `create-task` | Create a new task in a list |
| `update-task` | Update task status or priority |
| `list-spaces` | List all spaces in the workspace |
| `list-lists` | List all lists in a space |

## Usage

```bash
# List spaces in workspace
python clickup_manager.py list-spaces

# List lists in a space
python clickup_manager.py list-lists --space-id SPACE_ID

# List tasks in a list
python clickup_manager.py list-tasks --list-id LIST_ID

# Filter by status
python clickup_manager.py list-tasks --list-id LIST_ID --status-filter "in progress"

# Create a task
python clickup_manager.py create-task --list-id LIST_ID --name "Fix bug" --description "Details here" --priority 2

# Update a task
python clickup_manager.py update-task --task-id TASK_ID --status "complete" --priority 1
```

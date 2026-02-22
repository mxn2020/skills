---
name: todoist-sync
id: OC-0129
version: 1.0.0
description: "Todoist Sync - Manage Todoist tasks and projects via REST API v2"
env:
  - TODOIST_API_TOKEN
commands:
  - list-tasks
  - add-task
  - complete-task
  - list-projects
  - move-task
---

# Todoist Sync

Manage Todoist tasks and projects from the CLI using the Todoist REST API v2.

## Prerequisites

- `TODOIST_API_TOKEN` — Todoist API token (Settings → Integrations → Developer → API token)
- `pip install requests`

## Commands

| Command | Description |
|---------|-------------|
| `list-tasks` | List tasks, optionally filtered by project or filter string |
| `add-task` | Add a new task |
| `complete-task` | Mark a task as complete |
| `list-projects` | List all projects |
| `move-task` | Move a task to a different project |

## Usage

```bash
# List all tasks
python todoist_sync.py list-tasks

# List tasks in a specific project
python todoist_sync.py list-tasks --project-id 12345678

# Add a task
python todoist_sync.py add-task --content "Write report" --due-string "tomorrow" --priority 4

# Complete a task
python todoist_sync.py complete-task --id TASK_ID

# List all projects
python todoist_sync.py list-projects

# Move task to another project
python todoist_sync.py move-task --id TASK_ID --project-id NEW_PROJECT_ID
```

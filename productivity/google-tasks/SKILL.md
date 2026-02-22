---
name: google-tasks
id: OC-0131
version: 1.0.0
description: "Google Tasks - Manage Google Tasks lists and tasks via REST API"
env:
  - GOOGLE_TASKS_TOKEN
commands:
  - list-tasks
  - add-task
  - complete-task
  - list-lists
  - delete-task
---

# Google Tasks

Manage Google Tasks lists and individual tasks from the CLI using the Google Tasks API.

## Prerequisites

- `GOOGLE_TASKS_TOKEN` — OAuth 2.0 bearer access token with `tasks` scope
- `pip install requests`

## Commands

| Command | Description |
|---------|-------------|
| `list-tasks` | List tasks in a task list |
| `add-task` | Add a new task to a list |
| `complete-task` | Mark a task as completed |
| `list-lists` | List all task lists |
| `delete-task` | Delete a task from a list |

## Usage

```bash
# List all task lists
python google_tasks.py list-lists

# List tasks in the default list
python google_tasks.py list-tasks --list-id @default

# List tasks including completed
python google_tasks.py list-tasks --list-id LIST_ID --show-completed

# Add a task
python google_tasks.py add-task --list-id @default --title "Buy groceries" --notes "Milk, eggs" --due "2024-12-31T00:00:00.000Z"

# Complete a task
python google_tasks.py complete-task --list-id @default --task-id TASK_ID

# Delete a task
python google_tasks.py delete-task --list-id @default --task-id TASK_ID
```

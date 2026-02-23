---
name: notion-task-manager
id: OC-0130
version: 1.0.0
description: "Notion Task Manager - Manage Notion database tasks via REST API"
env:
  - NOTION_API_KEY
  - NOTION_DATABASE_ID
commands:
  - list-tasks
  - create-task
  - update-task
  - filter-tasks
  - archive-task
---

# Notion Task Manager

Manage tasks stored in a Notion database via the Notion REST API.

## Prerequisites

- `NOTION_API_KEY` — Notion integration token (notion.so/my-integrations)
- `NOTION_DATABASE_ID` — The ID of your Notion task database
- `pip install requests`

## Commands

| Command | Description |
|---------|-------------|
| `list-tasks` | List all tasks with optional status filter |
| `create-task` | Create a new task in the database |
| `update-task` | Update a task's status or title |
| `filter-tasks` | Filter tasks by a property value |
| `archive-task` | Archive (soft-delete) a task page |

## Usage

```bash
# List all tasks
python notion_task_manager.py list-tasks

# List tasks with status filter
python notion_task_manager.py list-tasks --status-filter "In Progress"

# Create a new task
python notion_task_manager.py create-task --title "Write docs" --status "Todo" --due-date "2024-12-31"

# Update a task
python notion_task_manager.py update-task --page-id PAGE_ID --status "Done"

# Filter tasks by property
python notion_task_manager.py filter-tasks --property "Priority" --value "High"

# Archive a task
python notion_task_manager.py archive-task --page-id PAGE_ID
```

---
name: obsidian-creator
id: OC-0154
version: 1.0.0
description: "Obsidian Note Creator - Write structured markdown notes directly into an Obsidian vault"
env:
  - OBSIDIAN_VAULT_PATH
commands:
  - create-note
  - create-daily
  - search-notes
  - append-to-note
  - list-notes
---

# Obsidian Note Creator

Create and manage structured Markdown notes in your Obsidian vault from the terminal. Supports frontmatter, backlinks, tags, and daily notes.

## Prerequisites

- Python 3.8+
- `OBSIDIAN_VAULT_PATH` — absolute path to your Obsidian vault directory

## Commands

| Command | Description |
|---------|-------------|
| `create-note` | Create a new note with optional frontmatter |
| `create-daily` | Create or open today's daily note |
| `search-notes` | Search notes by keyword |
| `append-to-note` | Append content to an existing note |
| `list-notes` | List notes in a folder |

## Usage

```bash
export OBSIDIAN_VAULT_PATH="/Users/you/Documents/MyVault"

# Create a new note
python3 scripts/obsidian_creator.py create-note --title "Meeting Notes" --content "Key points..." --tags "meetings,work" --folder "Work"

# Create today's daily note
python3 scripts/obsidian_creator.py create-daily --template "tasks,journal"

# Search for notes containing a keyword
python3 scripts/obsidian_creator.py search-notes --query "project Alpha"

# Append to an existing note
python3 scripts/obsidian_creator.py append-to-note --title "Meeting Notes" --content "## Follow-up\n- Send email"

# List all notes in a folder
python3 scripts/obsidian_creator.py list-notes --folder "Work"
```

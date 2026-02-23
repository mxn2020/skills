---
name: prompt-version-control
id: OC-0115
version: 1.0.0
description: "Prompt Version Control - Save, tag, and rollback prompt templates with git"
env: []
commands:
  - save
  - list
  - load
  - diff
  - tag
  - rollback
---

# Prompt Version Control

Version-control your AI prompt templates using a local git-backed store in `~/.openclaw/prompts/`.

## Prerequisites

- `git` installed

## Commands

| Command | Description |
|---------|-------------|
| `save` | Save a prompt with a name |
| `list` | List all saved prompts and versions |
| `load` | Load a specific prompt version |
| `diff` | Diff two versions of a prompt |
| `tag` | Tag a prompt version |
| `rollback` | Roll back to a previous version |

## Usage

```bash
python3 scripts/prompt_version_control.py save --name summarizer --file prompt.txt
python3 scripts/prompt_version_control.py list
python3 scripts/prompt_version_control.py load --name summarizer
python3 scripts/prompt_version_control.py diff --name summarizer --v1 HEAD~1 --v2 HEAD
python3 scripts/prompt_version_control.py tag --name summarizer --tag v1.0
python3 scripts/prompt_version_control.py rollback --name summarizer --version HEAD~1
```

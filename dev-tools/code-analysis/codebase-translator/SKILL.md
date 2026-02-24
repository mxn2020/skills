---
name: codebase-translator
id: OC-0196
version: 1.0.0
description: "Translate modules or entire small codebases from one language to another (e.g., JS to TS)."
env:
  - OPENAI_API_KEY
commands:
  - translate-file
  - translate-module
---

# Codebase Translator

Translate modules or entire small codebases from one language to another (e.g., JS to TS).

## Prerequisites
- A valid `OPENAI_API_KEY` environment variable.

## Commands
| Command            | Description                              |
|--------------------|------------------------------------------|
| `translate-file`   | Translate a single file to a target language |
| `translate-module` | Translate an entire directory module     |

## Usage
```bash
export OPENAI_API_KEY="sk-..."
python3 scripts/codebase_translator.py translate-file --source src/utils.js --target-lang typescript --output src/utils.ts
python3 scripts/codebase_translator.py translate-module --source src/api/ --target-lang python --output py-api/
```

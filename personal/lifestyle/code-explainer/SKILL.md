---
name: code-explainer
id: OC-0177
version: 1.0.0
description: "Code Explainer - Narrate what a code snippet does in plain English for non-developers"
env:
  - OPENAI_API_KEY
commands:
  - explain
  - eli5
  - annotate
  - complexity
---

# Code Explainer

Translate code into plain English for non-developers, generate line-by-line annotations, and analyze code complexity.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- `OPENAI_API_KEY` — for AI-powered explanations

## Commands

| Command | Description |
|---------|-------------|
| `explain` | Explain what a code snippet does |
| `eli5` | Explain Like I'm 5 — ultra-simple explanation |
| `annotate` | Add inline comments to code |
| `complexity` | Analyze code complexity and suggest improvements |

## Usage

```bash
export OPENAI_API_KEY="your_key"

# Explain a code file
python3 scripts/code_explainer.py explain --file script.py

# ELI5 explanation
python3 scripts/code_explainer.py eli5 --file script.py

# Add inline annotations
python3 scripts/code_explainer.py annotate --file script.py --output annotated.py

# Analyze complexity
python3 scripts/code_explainer.py complexity --file script.py
```

---
name: bias-safety-checker
id: OC-0120
version: 1.0.0
description: "Bias & Safety Checker - Pre-screen LLM outputs for bias, toxicity, and PII"
env:
  - OPENAI_API_KEY
commands:
  - check-text
  - check-file
  - batch-check
  - generate-report
---

# Bias & Safety Checker

Pre-screen LLM outputs for bias, toxicity, and PII.

## Prerequisites

- `OPENAI_API_KEY`

## Commands

| Command | Description |
|---------|-------------|
| `check-text` | ... |
| `check-file` | ... |
| `batch-check` | ... |
| `generate-report` | ... |

## Usage

```bash
python3 scripts/bias_safety_checker.py check-text
python3 scripts/bias_safety_checker.py check-file
python3 scripts/bias_safety_checker.py batch-check
```

---
name: eval-suite-runner
id: OC-0126
version: 1.0.0
description: "Eval Suite Runner - Run automated evals against a golden dataset to catch regressions"
env:
  - OPENAI_API_KEY
commands:
  - run
  - add-test
  - list-tests
  - compare-runs
---

# Eval Suite Runner

Run automated evals against a golden dataset to catch regressions.

## Prerequisites

- `OPENAI_API_KEY`

## Commands

| Command | Description |
|---------|-------------|
| `run` | ... |
| `add-test` | ... |
| `list-tests` | ... |
| `compare-runs` | ... |

## Usage

```bash
python3 scripts/eval_suite_runner.py run
python3 scripts/eval_suite_runner.py add-test
python3 scripts/eval_suite_runner.py list-tests
```

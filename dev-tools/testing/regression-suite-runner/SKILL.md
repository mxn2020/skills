---
name: regression-suite-runner
id: OC-0181
version: 1.0.0
description: "Regression Suite Runner - Execute skill interactions and diff output against golden master"
env: []
commands:
  - record
  - run
  - compare
  - list-suites
---

# Regression Suite Runner

Record golden master outputs for skills and run automated regression tests to catch unexpected changes.

## Prerequisites

- Python 3.8+

## Commands

| Command | Description |
|---------|-------------|
| `record` | Record a golden master output for a command |
| `run` | Run all regression tests for a skill |
| `compare` | Compare current output to golden master |
| `list-suites` | List all regression suites |

## Usage

```bash
# Record golden output for a command
python3 scripts/regression_suite_runner.py record --skill "timezone-converter" --command "convert --time '2024-01-01 09:00' --from-zone UTC --to-zones America/New_York"

# Run all tests for a skill
python3 scripts/regression_suite_runner.py run --skill "timezone-converter"

# Compare output to golden master
python3 scripts/regression_suite_runner.py compare --suite-id SUITE_ID

# List all suites
python3 scripts/regression_suite_runner.py list-suites
```

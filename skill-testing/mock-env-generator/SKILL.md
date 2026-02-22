---
name: mock-env-generator
id: OC-0179
version: 1.0.0
description: "Mock Environment Generator - Create sandboxed temp directories and files for safe testing"
env: []
commands:
  - create
  - teardown
  - list
  - scaffold
---

# Mock Environment Generator

Create isolated sandboxed environments with temporary directories, files, and mock configurations for safe skill testing.

## Prerequisites

- Python 3.8+

## Commands

| Command | Description |
|---------|-------------|
| `create` | Create a new mock environment |
| `teardown` | Clean up a mock environment |
| `list` | List active mock environments |
| `scaffold` | Generate scaffold files for a skill test |

## Usage

```bash
# Create a mock environment with test files
python3 scripts/mock_env_generator.py create --name "test-gmail" --files "inbox.json,sent.json"

# Scaffold test files for a skill
python3 scripts/mock_env_generator.py scaffold --skill "budget-tracker" --fixtures "transactions"

# List active environments
python3 scripts/mock_env_generator.py list

# Tear down an environment
python3 scripts/mock_env_generator.py teardown --name "test-gmail"
```

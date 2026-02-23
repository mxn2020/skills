---
name: api-response-mocker
id: OC-0180
version: 1.0.0
description: "API Response Mocker - Intercept outgoing API calls and return fixture data for offline testing"
env: []
commands:
  - start
  - add-fixture
  - list-fixtures
  - remove-fixture
  - verify-calls
---

# API Response Mocker

Run a local mock HTTP server that intercepts API calls and returns fixture responses, enabling offline testing of skills.

## Prerequisites

- Python 3.8+

## Commands

| Command | Description |
|---------|-------------|
| `start` | Start the mock server |
| `add-fixture` | Add a mock response fixture |
| `list-fixtures` | List all configured fixtures |
| `remove-fixture` | Remove a fixture |
| `verify-calls` | Check which API calls were made |

## Usage

```bash
# Start mock server on port 8765
python3 scripts/api_response_mocker.py start --port 8765

# Add a fixture for a specific endpoint
python3 scripts/api_response_mocker.py add-fixture --path "/api/users" --method GET --response '{"users": []}'

# List fixtures
python3 scripts/api_response_mocker.py list-fixtures

# Check what API calls were made to the mock
python3 scripts/api_response_mocker.py verify-calls

# Remove a fixture
python3 scripts/api_response_mocker.py remove-fixture --path "/api/users" --method GET
```

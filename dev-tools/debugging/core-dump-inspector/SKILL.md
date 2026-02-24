---
name: core-dump-inspector
id: OC-0198
version: 1.0.0
description: "Basic analysis of core dumps or crash logs to extract failure points and stack traces."
env: []
commands:
  - extract-trace
  - analyze-crash
---

# Core Dump Inspector

Basic analysis of core dumps or crash logs to extract failure points and stack traces.

## Prerequisites
- Access to a core dump file or application crash log.
- `gdb` or similar debugging tools may be required depending on the environment.

## Commands
| Command         | Description                              |
|-----------------|------------------------------------------|
| `extract-trace` | Extract the stack trace leading to the crash |
| `analyze-crash` | Provide a natural language summary of the crash |

## Usage
```bash
python3 scripts/core_dump_inspector.py extract-trace --core core.1234 --binary ./my_app
python3 scripts/core_dump_inspector.py analyze-crash --trace crash_trace.txt
```

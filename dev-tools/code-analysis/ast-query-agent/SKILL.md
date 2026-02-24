---
name: ast-query-agent
id: OC-0195
version: 1.0.0
description: "Query abstract syntax trees to find anti-patterns or specific code structures programmatically."
env: []
commands:
  - query-ast
  - detect-pattern
---

# AST Query Agent

Query abstract syntax trees to find anti-patterns or specific code structures programmatically.

## Prerequisites
- No specific environment variables required.
- Requires tree-sitter or similar AST parsing library (handled by script).

## Commands
| Command          | Description                              |
|------------------|------------------------------------------|
| `query-ast`      | Run a specific AST query against a file |
| `detect-pattern` | Scan a directory for known anti-patterns based on AST |

## Usage
```bash
python3 scripts/ast_query_agent.py query-ast --file src/main.js --query "function_declaration"
python3 scripts/ast_query_agent.py detect-pattern --dir src/
```

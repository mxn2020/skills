---
name: flamegraph-analyzer
id: OC-0197
version: 1.0.0
description: "Parse and analyze profiling flamegraphs to identify performance bottlenecks."
env: []
commands:
  - analyze
  - suggest-optimization
---

# Flamegraph Analyzer

Parse and analyze profiling flamegraphs to identify performance bottlenecks.

## Prerequisites
- An exported flamegraph or profiling data file (e.g., collapsed stack format).

## Commands
| Command                | Description                              |
|------------------------|------------------------------------------|
| `analyze`              | Identify the top bottlenecks from a flamegraph |
| `suggest-optimization` | Suggest code optimizations for identified bottlenecks |

## Usage
```bash
python3 scripts/flamegraph_analyzer.py analyze --input profile.collapsed
python3 scripts/flamegraph_analyzer.py suggest-optimization --bottleneck "App::render"
```

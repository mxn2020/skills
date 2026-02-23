---
name: performance-load-tester
id: OC-0184
version: 1.0.0
description: "Performance Load Tester - Run skills in parallel to test concurrency and resource usage bounds"
env: []
commands:
  - run
  - benchmark
  - report
---

# Performance Load Tester

Run skills in parallel with configurable concurrency and iterations to measure throughput, latency percentiles, and peak resource usage.

## Prerequisites

- Python 3.8+

## Commands

| Command | Description |
|---------|-------------|
| `run` | Execute a skill script N times across W parallel workers |
| `benchmark` | Run multiple concurrency levels and produce a comparison table |
| `report` | Display a saved performance report |

## Usage

```bash
# Run a skill with 10 concurrent workers, 50 total iterations
python3 scripts/performance_load_tester.py run --skill timezone-converter --cmd "convert --time '2024-01-01 09:00' --from-zone UTC --to-zones America/New_York" --workers 10 --iterations 50

# Benchmark a skill at concurrency levels 1, 5, 10, 20
python3 scripts/performance_load_tester.py benchmark --skill timezone-converter --cmd "convert --time '2024-01-01 09:00' --from-zone UTC --to-zones America/New_York" --levels 1,5,10,20

# Show a previously saved report
python3 scripts/performance_load_tester.py report --file perf_report.json
```

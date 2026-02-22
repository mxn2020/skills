---
name: embedding-drift-detector
id: OC-0125
version: 1.0.0
description: "Embedding Drift Detector - Alert when retrieved context chunks diverge significantly from the query"
env:
  - OPENAI_API_KEY
commands:
  - compute-drift
  - monitor-collection
  - set-threshold
  - generate-alert
---

# Embedding Drift Detector

Alert when retrieved context chunks diverge significantly from the query.

## Prerequisites

- `OPENAI_API_KEY`

## Commands

| Command | Description |
|---------|-------------|
| `compute-drift` | ... |
| `monitor-collection` | ... |
| `set-threshold` | ... |
| `generate-alert` | ... |

## Usage

```bash
python3 scripts/embedding_drift_detector.py compute-drift
python3 scripts/embedding_drift_detector.py monitor-collection
python3 scripts/embedding_drift_detector.py set-threshold
```

---
name: mongodb-monitor
version: 1.0.0
description: MongoDB Atlas Cluster Monitor (OC-0029). Check connections and slow queries on MongoDB Atlas. Use when user asks to monitor MongoDB clusters, check metrics, or find slow queries.
---

# MongoDB Atlas Cluster Monitor

Check connections, metrics, and slow queries on MongoDB Atlas clusters.

## Capabilities

1. **List Clusters**: View all clusters in a project.
2. **Get Metrics**: Retrieve cluster performance metrics.
3. **Slow Queries**: Identify slow-running queries.
4. **List Databases**: View databases in a cluster.
5. **Get Alerts**: Check active alerts for the project.

## Quick Start

```bash
# List clusters
python3 skills/cloud/data/databases/mongodb-monitor/scripts/manage.py list-clusters

# Get cluster metrics
python3 skills/cloud/data/databases/mongodb-monitor/scripts/manage.py get-metrics --cluster myCluster --period PT1H

# Find slow queries
python3 skills/cloud/data/databases/mongodb-monitor/scripts/manage.py slow-queries --cluster myCluster

# List databases
python3 skills/cloud/data/databases/mongodb-monitor/scripts/manage.py list-databases --cluster myCluster

# Get alerts
python3 skills/cloud/data/databases/mongodb-monitor/scripts/manage.py get-alerts
```

## Commands & Parameters

### `list-clusters`
Lists all clusters in the Atlas project.
- No required parameters.

### `get-metrics`
Gets performance metrics for a cluster.
- `--cluster`: Cluster name (required).
- `--metric`: Metric name (default: CONNECTIONS).
- `--period`: Time period in ISO 8601 (default: PT1H).
- `--granularity`: Data granularity (default: PT5M).

### `slow-queries`
Lists slow queries on a cluster.
- `--cluster`: Cluster name (required).
- `--duration`: Min duration in ms (default: 100).

### `list-databases`
Lists databases in a cluster.
- `--cluster`: Cluster name (required).

### `get-alerts`
Gets active alerts for the project.
- No required parameters.

## Dependencies
- `MONGODB_PUBLIC_KEY` environment variable (Atlas public API key).
- `MONGODB_PRIVATE_KEY` environment variable (Atlas private API key).
- `MONGODB_GROUP_ID` environment variable (Atlas project/group ID).
- Python `requests` library (`pip install requests`).

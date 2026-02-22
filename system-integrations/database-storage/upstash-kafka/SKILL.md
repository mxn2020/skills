---
name: upstash-kafka
version: 1.0.0
description: Upstash Kafka Producer (OC-0031). Send events to serverless Kafka topics. Use when user asks to produce or consume messages on Upstash Kafka.
---

# Upstash Kafka Producer

Send events to serverless Kafka topics and consume messages via the Upstash Kafka REST API.

## Capabilities

1. **List Topics**: View all Kafka topics.
2. **Produce**: Send messages to a topic.
3. **Consume**: Read messages from a topic.
4. **Create Topic**: Create a new topic.
5. **Get Topic**: Get topic details.

## Quick Start

```bash
# List topics
python3 skills/system-integrations/database-storage/upstash-kafka/scripts/manage.py list-topics

# Produce a message
python3 skills/system-integrations/database-storage/upstash-kafka/scripts/manage.py produce --topic events --message '{"type":"deploy","env":"production"}'

# Consume messages
python3 skills/system-integrations/database-storage/upstash-kafka/scripts/manage.py consume --topic events --group my-consumer --instance inst-1

# Create a topic
python3 skills/system-integrations/database-storage/upstash-kafka/scripts/manage.py create-topic --name events --partitions 3

# Get topic details
python3 skills/system-integrations/database-storage/upstash-kafka/scripts/manage.py get-topic --topic events
```

## Commands & Parameters

### `list-topics`
Lists all Kafka topics.
- No required parameters.

### `produce`
Produces a message to a topic.
- `--topic`: Topic name (required).
- `--message`: Message body (required).
- `--key`: Message key (optional).

### `consume`
Consumes messages from a topic.
- `--topic`: Topic name (required).
- `--group`: Consumer group name (required).
- `--instance`: Consumer instance name (required).
- `--timeout`: Timeout in ms (default: 5000).

### `create-topic`
Creates a new Kafka topic.
- `--name`: Topic name (required).
- `--partitions`: Number of partitions (default: 1).
- `--retention-ms`: Retention period in ms (default: 604800000).

### `get-topic`
Gets details of a topic.
- `--topic`: Topic name (required).

## Dependencies
- `UPSTASH_KAFKA_URL` environment variable (Upstash Kafka REST URL).
- `UPSTASH_KAFKA_USERNAME` environment variable.
- `UPSTASH_KAFKA_PASSWORD` environment variable.
- Python `requests` library (`pip install requests`).

---
name: mqtt-publisher
id: OC-0166
version: 1.0.0
description: "MQTT Publisher - Publish and subscribe to MQTT topics for IoT messaging"
env:
  - MQTT_BROKER_HOST
  - MQTT_PORT
  - MQTT_USERNAME
  - MQTT_PASSWORD
commands:
  - publish
  - subscribe-once
  - publish-batch
  - test-connection
  - list-topics
---

# MQTT Publisher

Publish and subscribe to MQTT topics for IoT device messaging. Supports single messages, batch publishing from JSON files, and connection testing.

## Prerequisites

- Python 3.8+
- `paho-mqtt` library (`pip install paho-mqtt`)
- Environment variables: `MQTT_BROKER_HOST`, `MQTT_PORT` (default: 1883), `MQTT_USERNAME` (optional), `MQTT_PASSWORD` (optional)

## Commands

| Command           | Parameters                                                                          | Description                                      |
| ----------------- | ----------------------------------------------------------------------------------- | ------------------------------------------------ |
| `publish`         | `--topic`, `--payload`, `--qos` (0/1/2), `--retain`                                | Publish a message to a topic                     |
| `subscribe-once`  | `--topic`, `--timeout` (default: 10)                                                | Subscribe and print the first message received   |
| `publish-batch`   | `--file` (JSON array of {topic, payload})                                           | Publish multiple messages from a JSON file       |
| `test-connection` | (none)                                                                              | Test connection to the MQTT broker               |
| `list-topics`     | `--prefix-filter`                                                                   | Note broker-side topic listing limitations       |

## Usage

```bash
export MQTT_BROKER_HOST="mqtt.example.com"
export MQTT_PORT="1883"
export MQTT_USERNAME="user"
export MQTT_PASSWORD="pass"

# Publish a message
python3 scripts/mqtt_publisher.py publish --topic home/living_room/light --payload '{"state": "on"}' --qos 1

# Subscribe and get one message
python3 scripts/mqtt_publisher.py subscribe-once --topic home/sensors/temp --timeout 15

# Publish batch from file
python3 scripts/mqtt_publisher.py publish-batch --file messages.json

# Test broker connection
python3 scripts/mqtt_publisher.py test-connection

# Info about topic listing
python3 scripts/mqtt_publisher.py list-topics --prefix-filter home/
```

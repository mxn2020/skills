---
name: home-assistant
id: OC-0165
version: 1.0.0
description: "Home Assistant - Control and query your Home Assistant smart home instance"
env:
  - HA_BASE_URL
  - HA_TOKEN
commands:
  - list-entities
  - get-state
  - call-service
  - turn-on
  - turn-off
  - toggle
  - list-scenes
  - activate-scene
---

# Home Assistant

Control and query your Home Assistant smart home instance from the terminal. List entities, read states, call services, and manage scenes.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- Environment variables: `HA_BASE_URL` (e.g. `http://homeassistant.local:8123`), `HA_TOKEN` (long-lived access token)

## Commands

| Command            | Parameters                                                                          | Description                                |
| ------------------ | ----------------------------------------------------------------------------------- | ------------------------------------------ |
| `list-entities`    | `--domain-filter` (optional, e.g. light/switch/climate)                             | List all entity states, optionally filtered |
| `get-state`        | `--entity-id`                                                                       | Get the current state of an entity         |
| `call-service`     | `--domain`, `--service`, `--entity-id`, `--data-json` (optional)                   | Call any Home Assistant service            |
| `turn-on`          | `--entity-id`                                                                       | Turn on an entity                          |
| `turn-off`         | `--entity-id`                                                                       | Turn off an entity                         |
| `toggle`           | `--entity-id`                                                                       | Toggle an entity on/off                    |
| `list-scenes`      | (none)                                                                              | List all available scenes                  |
| `activate-scene`   | `--scene-id`                                                                        | Activate a scene by entity ID              |

## Usage

```bash
export HA_BASE_URL="http://homeassistant.local:8123"
export HA_TOKEN="your-long-lived-access-token"

# List all light entities
python3 scripts/home_assistant.py list-entities --domain-filter light

# Get state of a specific entity
python3 scripts/home_assistant.py get-state --entity-id light.living_room

# Turn on a light
python3 scripts/home_assistant.py turn-on --entity-id light.living_room

# Turn off a switch
python3 scripts/home_assistant.py turn-off --entity-id switch.fan

# Toggle a light
python3 scripts/home_assistant.py toggle --entity-id light.bedroom

# Call a custom service
python3 scripts/home_assistant.py call-service --domain light --service turn_on --entity-id light.kitchen --data-json '{"brightness": 200}'

# List all scenes
python3 scripts/home_assistant.py list-scenes

# Activate a scene
python3 scripts/home_assistant.py activate-scene --scene-id scene.movie_night
```

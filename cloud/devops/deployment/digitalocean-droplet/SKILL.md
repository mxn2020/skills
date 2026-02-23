---
name: digitalocean-droplet
id: OC-0022
version: 1.0.0
description: "DigitalOcean Droplet Sniper - Create short-lived VPS"
env:
  - DIGITALOCEAN_TOKEN
commands:
  - list-droplets
  - create
  - destroy
  - get-droplet
  - list-snapshots
---

# DigitalOcean Droplet Sniper

Create, manage, and destroy DigitalOcean droplets.

## Prerequisites

- A valid `DIGITALOCEAN_TOKEN` environment variable.

## Commands

| Command          | Description                          |
|------------------|--------------------------------------|
| `list-droplets`  | List all droplets                    |
| `create`         | Create a new droplet                 |
| `destroy`        | Destroy a droplet                    |
| `get-droplet`    | Get droplet details                  |
| `list-snapshots` | List available snapshots             |

## Usage

```bash
export DIGITALOCEAN_TOKEN="your-token"
python3 scripts/digitalocean_droplet.py list-droplets
python3 scripts/digitalocean_droplet.py create --name temp-box --region nyc3 --size s-1vcpu-1gb --image ubuntu-22-04-x64
python3 scripts/digitalocean_droplet.py destroy --droplet-id 123456
```

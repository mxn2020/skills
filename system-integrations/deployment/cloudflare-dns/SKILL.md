---
name: cloudflare-dns
id: OC-0019
version: 1.0.0
description: "Cloudflare DNS Manager - Update records programmatically"
env:
  - CLOUDFLARE_API_TOKEN
commands:
  - list-zones
  - list-records
  - create-record
  - update-record
  - delete-record
---

# Cloudflare DNS Manager

Manage DNS zones and records via the Cloudflare API.

## Prerequisites

- A valid `CLOUDFLARE_API_TOKEN` environment variable.

## Commands

| Command         | Description                          |
|-----------------|--------------------------------------|
| `list-zones`    | List all DNS zones                   |
| `list-records`  | List records in a zone               |
| `create-record` | Create a new DNS record              |
| `update-record` | Update an existing DNS record        |
| `delete-record` | Delete a DNS record                  |

## Usage

```bash
export CLOUDFLARE_API_TOKEN="your-token"
python3 scripts/cloudflare_dns.py list-zones
python3 scripts/cloudflare_dns.py create-record --zone-id xxx --type A --name sub.example.com --content 1.2.3.4
python3 scripts/cloudflare_dns.py update-record --zone-id xxx --record-id yyy --content 5.6.7.8
```

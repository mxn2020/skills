---
name: discord-webhook
id: OC-0078
version: 1.0.0
description: "Discord Webhook Notifier - Push structured alerts and messages to Discord channels via webhooks"
env:
  - DISCORD_WEBHOOK_URL
commands:
  - send
  - send-embed
  - get-message
  - edit-message
  - delete-message
---

# Discord Webhook Notifier

Push structured alerts and messages to Discord channels via webhooks.

## Prerequisites

- A valid `DISCORD_WEBHOOK_URL` environment variable (the full webhook URL from Discord channel settings).

## Commands

| Command          | Description                                  |
|------------------|----------------------------------------------|
| `send`           | Send a plain text message                    |
| `send-embed`     | Send a rich embed message with fields        |
| `get-message`    | Retrieve a webhook message by ID             |
| `edit-message`   | Edit a previously sent webhook message       |
| `delete-message` | Delete a previously sent webhook message     |

## Usage

```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/123/abc"
python3 scripts/discord_webhook.py send --content "Deployment succeeded"
python3 scripts/discord_webhook.py send-embed --title "Build Status" --description "All checks passed" --color "00ff00" --field "Branch:main" --field "Duration:2m30s"
python3 scripts/discord_webhook.py get-message --message-id 1234567890
python3 scripts/discord_webhook.py edit-message --message-id 1234567890 --content "Updated message"
python3 scripts/discord_webhook.py delete-message --message-id 1234567890
```

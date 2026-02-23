---
name: slack-bot
id: OC-0077
version: 1.0.0
description: "Slack Bot Publisher - Post messages and manage channels via Bot API"
env:
  - SLACK_BOT_TOKEN
commands:
  - post-message
  - list-channels
  - list-members
  - upload-file
  - set-topic
---

# Slack Bot Publisher

Post messages, manage channels, and upload files via the Slack Bot API.

## Prerequisites

- A valid `SLACK_BOT_TOKEN` environment variable.

## Commands

| Command          | Description                          |
|------------------|--------------------------------------|
| `post-message`   | Post a message to a channel          |
| `list-channels`  | List available channels              |
| `list-members`   | List members of a channel            |
| `upload-file`    | Upload a file to a channel           |
| `set-topic`      | Set the topic of a channel           |

## Usage

```bash
export SLACK_BOT_TOKEN="xoxb-your-token"
python3 scripts/slack_bot.py list-channels
python3 scripts/slack_bot.py post-message --channel "#general" --text "Hello from the bot!"
python3 scripts/slack_bot.py list-members --channel C01ABCDEF
python3 scripts/slack_bot.py upload-file --channels "#general" --content "Log output here"
python3 scripts/slack_bot.py upload-file --channels "#general" --file ./report.csv --title "Weekly Report"
python3 scripts/slack_bot.py set-topic --channel C01ABCDEF --topic "Sprint 42 updates"
```

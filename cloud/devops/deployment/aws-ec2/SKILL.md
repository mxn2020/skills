---
name: aws-ec2
id: OC-0014
version: 1.0.0
description: "AWS EC2 Instance Control - Start/stop dev servers"
env:
  - AWS_ACCESS_KEY_ID
  - AWS_SECRET_ACCESS_KEY
  - AWS_DEFAULT_REGION
commands:
  - list-instances
  - start
  - stop
  - get-status
  - describe
---

# AWS EC2 Instance Control

Start, stop, describe, and monitor EC2 instances.

## Prerequisites

- AWS CLI configured or standard AWS environment variables set.

## Commands

| Command          | Description                          |
|------------------|--------------------------------------|
| `list-instances` | List all EC2 instances               |
| `start`          | Start a stopped instance             |
| `stop`           | Stop a running instance              |
| `get-status`     | Get instance status checks           |
| `describe`       | Describe a specific instance         |

## Usage

```bash
python3 scripts/aws_ec2.py list-instances
python3 scripts/aws_ec2.py start --instance-id i-0abc123
python3 scripts/aws_ec2.py stop --instance-id i-0abc123
```

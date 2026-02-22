---
name: aws-lambda
id: OC-0015
version: 1.0.0
description: "AWS Lambda Invoker - Trigger and monitor serverless functions"
env:
  - AWS_ACCESS_KEY_ID
  - AWS_SECRET_ACCESS_KEY
  - AWS_DEFAULT_REGION
commands:
  - list-functions
  - invoke
  - get-logs
  - get-function
  - update-code
---

# AWS Lambda Invoker

Invoke, inspect, update, and monitor AWS Lambda functions.

## Prerequisites

- AWS CLI configured or standard AWS environment variables set.

## Commands

| Command          | Description                          |
|------------------|--------------------------------------|
| `list-functions` | List all Lambda functions            |
| `invoke`         | Invoke a function                    |
| `get-logs`       | Fetch recent CloudWatch logs         |
| `get-function`   | Get function configuration           |
| `update-code`    | Update function code from a zip      |

## Usage

```bash
python3 scripts/aws_lambda.py list-functions
python3 scripts/aws_lambda.py invoke --function-name my-func --payload '{"key": "val"}'
python3 scripts/aws_lambda.py update-code --function-name my-func --zip-file ./deploy.zip
```

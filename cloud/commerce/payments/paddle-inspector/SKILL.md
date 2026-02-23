---
name: paddle-inspector
version: 1.0.0
description: "OC-0074: Paddle Subscription Inspector — Audit billing history, manage subscriptions, and list transactions."
---

# Paddle Subscription Inspector

Audit billing history, manage subscriptions (cancel, pause, resume), and list transactions through the Paddle API.

## Capabilities

1. **Subscription Management**: List, inspect, cancel, pause, and resume subscriptions.
2. **Transaction History**: List transactions for billing audits.

## Quick Start

```bash
# List subscriptions
python3 skills/cloud/commerce/payments/paddle-inspector/scripts/manage.py list-subscriptions

# Get subscription details
python3 skills/cloud/commerce/payments/paddle-inspector/scripts/manage.py get-subscription sub_01h1234

# Cancel a subscription
python3 skills/cloud/commerce/payments/paddle-inspector/scripts/manage.py cancel sub_01h1234

# Pause a subscription
python3 skills/cloud/commerce/payments/paddle-inspector/scripts/manage.py pause sub_01h1234

# Resume a paused subscription
python3 skills/cloud/commerce/payments/paddle-inspector/scripts/manage.py resume sub_01h1234

# List transactions
python3 skills/cloud/commerce/payments/paddle-inspector/scripts/manage.py list-transactions
```

## Commands & Parameters

### `list-subscriptions`
Lists subscriptions.
- `--status`: Filter by status (`active`, `canceled`, `paused`, `past_due`, `trialing`)
- `--limit`: Number of results (default: 10)

### `get-subscription`
Retrieves details of a specific subscription.
- `subscription_id`: Paddle subscription ID (required)

### `cancel`
Cancels a subscription at end of billing period.
- `subscription_id`: Paddle subscription ID (required)
- `--immediate`: Cancel immediately (flag)

### `pause`
Pauses a subscription at end of billing period.
- `subscription_id`: Paddle subscription ID (required)

### `resume`
Resumes a paused subscription.
- `subscription_id`: Paddle subscription ID (required)

### `list-transactions`
Lists transactions for billing audits.
- `--subscription-id`: Filter by subscription ID
- `--limit`: Number of results (default: 10)

## Environment Variables

| Variable          | Required | Description               |
|-------------------|----------|---------------------------|
| `PADDLE_API_KEY`  | Yes      | Paddle API authentication key |

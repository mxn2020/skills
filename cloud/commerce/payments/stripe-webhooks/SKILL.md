---
name: stripe-webhooks
version: 1.0.0
description: "OC-0070: Stripe Webhook Debugger — Inspect webhook events, manage endpoints, and replay failed deliveries."
---

# Stripe Webhook Debugger

Inspect webhook events, manage endpoints, and replay failed deliveries through the Stripe API.

## Capabilities

1. **Event Inspection**: List and view individual webhook events.
2. **Endpoint Management**: List existing endpoints or create new ones.
3. **Replay**: Retry delivery of a specific event to an endpoint.

## Quick Start

```bash
# List recent events
python3 skills/cloud/commerce/payments/stripe-webhooks/scripts/manage.py list-events

# Get details of a specific event
python3 skills/cloud/commerce/payments/stripe-webhooks/scripts/manage.py get-event evt_1234

# List webhook endpoints
python3 skills/cloud/commerce/payments/stripe-webhooks/scripts/manage.py list-endpoints

# Create a new endpoint
python3 skills/cloud/commerce/payments/stripe-webhooks/scripts/manage.py create-endpoint https://example.com/webhook --events invoice.paid customer.created

# Replay an event
python3 skills/cloud/commerce/payments/stripe-webhooks/scripts/manage.py replay evt_1234
```

## Commands & Parameters

### `list-events`
Lists recent webhook events.
- `--type`: Filter by event type (e.g. `invoice.paid`)
- `--limit`: Number of results (default: 10)

### `get-event`
Retrieves details of a specific event.
- `event_id`: Stripe event ID (required)

### `list-endpoints`
Lists configured webhook endpoints.
- `--limit`: Number of results (default: 10)

### `create-endpoint`
Creates a new webhook endpoint.
- `url`: Endpoint URL (required)
- `--events`: Space-separated list of event types to subscribe to

### `replay`
Retries delivery of an event by re-posting its payload to all enabled endpoints.
- `event_id`: Stripe event ID (required)

## Environment Variables

| Variable            | Required | Description          |
|---------------------|----------|----------------------|
| `STRIPE_SECRET_KEY` | Yes      | Stripe secret API key |

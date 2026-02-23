---
name: stripe-subscriptions
version: 1.0.0
description: "OC-0069: Stripe Subscription Manager — Cancel/refund subscriptions, manage products and prices via the Stripe API."
---

# Stripe Subscription Manager

Cancel or refund subscriptions, list products and prices through the Stripe API.

## Capabilities

1. **Subscription Management**: List, cancel, and refund subscriptions.
2. **Product Catalog**: List products and create new ones.
3. **Price Inspection**: List prices associated with products.

## Quick Start

```bash
# List active subscriptions
python3 skills/cloud/commerce/payments/stripe-subscriptions/scripts/manage.py list-subscriptions

# Cancel a subscription immediately
python3 skills/cloud/commerce/payments/stripe-subscriptions/scripts/manage.py cancel sub_1234 --immediate

# Refund the latest invoice on a subscription
python3 skills/cloud/commerce/payments/stripe-subscriptions/scripts/manage.py refund sub_1234

# List all products
python3 skills/cloud/commerce/payments/stripe-subscriptions/scripts/manage.py list-products

# Create a product
python3 skills/cloud/commerce/payments/stripe-subscriptions/scripts/manage.py create-product "Pro Plan"

# List prices
python3 skills/cloud/commerce/payments/stripe-subscriptions/scripts/manage.py list-prices
```

## Commands & Parameters

### `list-subscriptions`
Lists subscriptions from your Stripe account.
- `--status`: Filter by status (`active`, `canceled`, `past_due`, etc.)
- `--limit`: Number of results (default: 10)

### `cancel`
Cancels a subscription.
- `subscription_id`: Stripe subscription ID (required)
- `--immediate`: Cancel immediately instead of at period end (flag)

### `refund`
Refunds the latest invoice on a subscription.
- `subscription_id`: Stripe subscription ID (required)
- `--amount`: Partial refund amount in cents (optional, full refund by default)

### `list-products`
Lists products in your Stripe account.
- `--limit`: Number of results (default: 10)

### `create-product`
Creates a new product.
- `name`: Product name (required)
- `--description`: Product description

### `list-prices`
Lists prices.
- `--product`: Filter by product ID
- `--limit`: Number of results (default: 10)

## Environment Variables

| Variable            | Required | Description          |
|---------------------|----------|----------------------|
| `STRIPE_SECRET_KEY` | Yes      | Stripe secret API key |

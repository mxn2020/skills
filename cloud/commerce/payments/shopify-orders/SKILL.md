---
name: shopify-orders
version: 1.0.0
description: "OC-0073: Shopify Order Manager — Fetch, refund, or fulfill orders, and browse products and customers."
---

# Shopify Order Manager

Fetch, refund, or fulfill orders, list products, and browse customers through the Shopify Admin API.

## Capabilities

1. **Order Management**: List, inspect, refund, and fulfill orders.
2. **Product Catalog**: List products in the store.
3. **Customer Directory**: Browse customer records.

## Quick Start

```bash
# List recent orders
python3 skills/cloud/commerce/payments/shopify-orders/scripts/manage.py list-orders

# Get order details
python3 skills/cloud/commerce/payments/shopify-orders/scripts/manage.py get-order 1234567890

# Refund an order
python3 skills/cloud/commerce/payments/shopify-orders/scripts/manage.py refund 1234567890

# Fulfill an order
python3 skills/cloud/commerce/payments/shopify-orders/scripts/manage.py fulfill 1234567890 --tracking-number "1Z999AA10123456784"

# List products
python3 skills/cloud/commerce/payments/shopify-orders/scripts/manage.py list-products

# List customers
python3 skills/cloud/commerce/payments/shopify-orders/scripts/manage.py list-customers
```

## Commands & Parameters

### `list-orders`
Lists recent orders.
- `--status`: Filter by status (`open`, `closed`, `cancelled`, `any`; default: `any`)
- `--limit`: Number of results (default: 10)

### `get-order`
Retrieves details for a specific order.
- `order_id`: Shopify order ID (required)

### `refund`
Creates a full refund for an order.
- `order_id`: Shopify order ID (required)
- `--note`: Refund reason note

### `fulfill`
Creates a fulfillment for an order.
- `order_id`: Shopify order ID (required)
- `--tracking-number`: Shipment tracking number
- `--tracking-company`: Shipping carrier name

### `list-products`
Lists products in the store.
- `--limit`: Number of results (default: 10)

### `list-customers`
Lists customers.
- `--limit`: Number of results (default: 10)

## Environment Variables

| Variable               | Required | Description                         |
|------------------------|----------|-------------------------------------|
| `SHOPIFY_STORE`        | Yes      | Shopify store domain (e.g. `mystore.myshopify.com`) |
| `SHOPIFY_ACCESS_TOKEN` | Yes      | Shopify Admin API access token      |

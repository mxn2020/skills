---
name: revenuecat-lookup
version: 1.0.0
description: "OC-0072: RevenueCat Customer Lookup — Check in-app purchase status, offerings, entitlements, and subscriptions."
---

# RevenueCat Customer Lookup

Check in-app purchase status, list offerings and entitlements, and inspect subscriptions through the RevenueCat API.

## Capabilities

1. **Customer Lookup**: Retrieve a customer profile by app user ID.
2. **Offerings & Entitlements**: List available offerings and entitlements.
3. **Subscription Inspection**: View subscription details and product catalog.

## Quick Start

```bash
# Get customer info
python3 skills/system-integrations/commerce-payments/revenuecat-lookup/scripts/manage.py get-customer app_user_123

# List offerings
python3 skills/system-integrations/commerce-payments/revenuecat-lookup/scripts/manage.py list-offerings

# List entitlements for a customer
python3 skills/system-integrations/commerce-payments/revenuecat-lookup/scripts/manage.py list-entitlements app_user_123

# Get subscription details
python3 skills/system-integrations/commerce-payments/revenuecat-lookup/scripts/manage.py get-subscription app_user_123 --product-id prod_monthly

# List products
python3 skills/system-integrations/commerce-payments/revenuecat-lookup/scripts/manage.py list-products
```

## Commands & Parameters

### `get-customer`
Retrieves a customer profile.
- `app_user_id`: RevenueCat app user ID (required)

### `list-offerings`
Lists all offerings configured in your RevenueCat project.

### `list-entitlements`
Lists active entitlements for a customer.
- `app_user_id`: RevenueCat app user ID (required)

### `get-subscription`
Gets subscription details for a customer.
- `app_user_id`: RevenueCat app user ID (required)
- `--product-id`: Filter by product identifier

### `list-products`
Lists products configured in your RevenueCat project.
- `--limit`: Number of results (default: 10)

## Environment Variables

| Variable            | Required | Description                      |
|---------------------|----------|----------------------------------|
| `REVENUECAT_API_KEY`| Yes      | RevenueCat secret API key (V1)   |

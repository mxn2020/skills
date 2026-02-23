---
name: lemonsqueezy-license
version: 1.0.0
description: "OC-0071: Lemon Squeezy License Check — Verify license keys, manage activations, and list products."
---

# Lemon Squeezy License Check

Verify license keys, manage activations, and browse products through the Lemon Squeezy API.

## Capabilities

1. **License Validation**: Validate a license key and check its activation status.
2. **Activation Management**: Activate or deactivate license instances.
3. **Product Catalog**: List available products.

## Quick Start

```bash
# Validate a license key
python3 skills/cloud/commerce/payments/lemonsqueezy-license/scripts/manage.py validate-key "ABCD-1234-EFGH-5678"

# List all licenses
python3 skills/cloud/commerce/payments/lemonsqueezy-license/scripts/manage.py list-licenses

# Activate a license
python3 skills/cloud/commerce/payments/lemonsqueezy-license/scripts/manage.py activate "ABCD-1234-EFGH-5678" --instance-name "server-1"

# Deactivate a license instance
python3 skills/cloud/commerce/payments/lemonsqueezy-license/scripts/manage.py deactivate "ABCD-1234-EFGH-5678" --instance-id "ins_abc123"

# List products
python3 skills/cloud/commerce/payments/lemonsqueezy-license/scripts/manage.py list-products
```

## Commands & Parameters

### `validate-key`
Validates a license key.
- `license_key`: The license key to validate (required)

### `list-licenses`
Lists all licenses in your store.
- `--limit`: Number of results (default: 10)

### `activate`
Activates a license key for a specific instance.
- `license_key`: The license key (required)
- `--instance-name`: Name for this activation instance (required)

### `deactivate`
Deactivates a license key instance.
- `license_key`: The license key (required)
- `--instance-id`: The instance ID to deactivate (required)

### `list-products`
Lists products in your Lemon Squeezy store.
- `--limit`: Number of results (default: 10)

## Environment Variables

| Variable              | Required | Description                |
|-----------------------|----------|----------------------------|
| `LEMONSQUEEZY_API_KEY`| Yes      | Lemon Squeezy API key      |

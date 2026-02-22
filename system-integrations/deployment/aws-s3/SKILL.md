---
name: aws-s3
id: OC-0013
version: 1.0.0
description: "AWS S3 Bucket Explorer - Upload assets, presigned URLs"
env:
  - AWS_ACCESS_KEY_ID
  - AWS_SECRET_ACCESS_KEY
  - AWS_DEFAULT_REGION
commands:
  - list-buckets
  - list-objects
  - upload
  - download
  - presign
---

# AWS S3 Bucket Explorer

Manage S3 buckets, upload/download objects, and generate presigned URLs.

## Prerequisites

- AWS CLI configured or `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_DEFAULT_REGION` set.

## Commands

| Command        | Description                          |
|----------------|--------------------------------------|
| `list-buckets` | List all S3 buckets                  |
| `list-objects` | List objects in a bucket             |
| `upload`       | Upload a local file to S3            |
| `download`     | Download an S3 object locally        |
| `presign`      | Generate a presigned URL for an obj  |

## Usage

```bash
python3 scripts/aws_s3.py list-buckets
python3 scripts/aws_s3.py upload --bucket my-bucket --key assets/logo.png --file ./logo.png
python3 scripts/aws_s3.py presign --bucket my-bucket --key assets/logo.png --expires 3600
```

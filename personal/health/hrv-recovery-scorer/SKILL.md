---
name: hrv-recovery-scorer
id: OC-0148
version: 1.0.0
description: "HRV & Recovery Scorer - Parse Garmin/Polar data and recommend training load"
env:
  - GARMIN_EMAIL
  - GARMIN_PASSWORD
commands:
  - log-hrv
  - recovery-score
  - training-recommendation
  - trend
---

# HRV & Recovery Scorer

Track Heart Rate Variability (HRV) and recovery scores to optimize training load and prevent overtraining.

## Prerequisites

- Python 3.8+
- `requests` library (`pip install requests`)
- `GARMIN_EMAIL` / `GARMIN_PASSWORD` for Garmin Connect (optional)

## Commands

| Command | Description |
|---------|-------------|
| `log-hrv` | Manually log HRV measurement |
| `recovery-score` | Calculate recovery score from recent data |
| `training-recommendation` | Get training load recommendation |
| `trend` | Show HRV trend over time |

## Usage

```bash
# Log manual HRV reading (in ms)
python3 scripts/hrv_recovery_scorer.py log-hrv --hrv 65 --resting-hr 58 --notes "Good sleep"

# Calculate today's recovery score
python3 scripts/hrv_recovery_scorer.py recovery-score

# Get training recommendation
python3 scripts/hrv_recovery_scorer.py training-recommendation

# View HRV trend (last 14 days)
python3 scripts/hrv_recovery_scorer.py trend --days 14
```

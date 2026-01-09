# How On-Time Rate Regression Works

## Understanding "Regression" vs "Improvement"

### What is Regression?

**Regression** = A metric getting WORSE (decreasing for positive metrics like on-time rate)

**Improvement** = A metric getting BETTER (increasing for positive metrics)

### Current System Behavior

The system currently flags **ANY significant change** (both improvements and regressions) as "incidents". This is because:

1. **Anomaly Detection** detects significant changes regardless of direction
2. **Incident Creation** uses the word "regressed" for any change
3. **Severity** is calculated based on magnitude, not direction

---

## How On-Time Rate Can Regress

### Scenario 1: True Regression (Metric Gets Worse)

```
Baseline Period: On-time rate = 92% (0.92)
Current Period:  On-time rate = 78% (0.78)

Delta = 0.78 - 0.92 = -0.14 (-14 percentage points)
Delta % = -14 / 92 = -15.2%

This is a TRUE REGRESSION ✅
- On-time rate decreased
- More orders are arriving late
- Customer experience degraded
```

**What causes this:**
- Batching threshold increased → longer wait times
- Dasher availability dropped → delayed assignments
- Merchant prep-time increased → orders ready late
- ETA model became optimistic → promised times too short
- Weather/traffic issues → delivery delays

### Scenario 2: Improvement (Flagged as "Regression" - Current Bug)

```
Baseline Period: On-time rate = 20% (0.20)
Current Period:  On-time rate = 38% (0.38)

Delta = 0.38 - 0.20 = +0.18 (+18 percentage points)
Delta % = +18 / 20 = +90%

This is an IMPROVEMENT (not a regression!)
- On-time rate increased
- More orders arriving on time
- Customer experience improved
```

**Why it's flagged:**
- System detects ANY significant change (>5% threshold)
- Uses word "regressed" incorrectly
- Should say "changed" or "improved"

---

## How On-Time Rate is Calculated

### Formula

```python
# For each order:
on_time = (
    actual_eta >= promised_eta - threshold AND
    actual_eta <= promised_eta + threshold
)

# Overall rate:
on_time_rate = mean(on_time for all orders)
```

**Threshold**: ±10 minutes (configurable)

### Example Calculation

```python
# Order 1:
promised_eta = 12:00 PM
actual_eta = 11:55 AM
difference = -5 minutes
on_time = True ✅ (within ±10 minutes)

# Order 2:
promised_eta = 12:00 PM
actual_eta = 12:15 PM
difference = +15 minutes
on_time = False ❌ (outside ±10 minutes)

# Order 3:
promised_eta = 12:00 PM
actual_eta = 12:05 PM
difference = +5 minutes
on_time = True ✅ (within ±10 minutes)

# Overall:
on_time_rate = (True + False + True) / 3 = 2/3 = 0.67 (67%)
```

---

## How Regression Detection Works

### Step 1: Calculate Metrics for Both Periods

```python
baseline_metrics = calculate_cx_score(baseline_data)
# Result: {'on_time_rate': 0.92, ...}

current_metrics = calculate_cx_score(current_data)
# Result: {'on_time_rate': 0.78, ...}
```

### Step 2: Calculate Delta

```python
delta = current_value - baseline_value
delta_percent = (delta / baseline_value) * 100

# Example:
delta = 0.78 - 0.92 = -0.14
delta_percent = (-0.14 / 0.92) * 100 = -15.2%
```

### Step 3: Check Significance Threshold

```python
# For rates (like on-time rate):
delta_pct = abs((delta / baseline_value * 100))
if delta_pct < 5:  # Less than 5% change
    skip  # Not significant enough
else:
    flag_incident  # Significant change detected
```

### Step 4: Calculate Severity

```python
abs_delta_pct = abs(delta_percent)

if abs_delta_pct >= 20:
    severity = 'HIGH'
elif abs_delta_pct >= 10:
    severity = 'MEDIUM'
else:
    severity = 'LOW'
```

**Note**: Severity is based on **magnitude**, not direction!

---

## Why Your UI Shows Improvement as "Regression"

### The Issue

Your UI shows:
- Baseline: 0.20 (20%)
- Current: 0.38 (38%)
- Change: +0.18 (+87.4%)
- Labeled as: "regressed"

### What's Actually Happening

1. **Anomaly Detection** detected a significant change (>5% threshold)
2. **Incident Creation** used word "regressed" for ANY change
3. **Severity** calculated based on magnitude (87.4% is huge!)

### What Should Happen

The system should:
1. **Check direction** before using "regressed"
2. **For improvements**: Say "improved" or "changed significantly"
3. **For regressions**: Say "regressed"

---

## Fixing the "Regression" Label

### Current Code (Bug)

```python
# detection_pipeline.py line 147
description = f"{metric_name} regressed from {baseline_value:.2f} to {current_value:.2f}"
```

### Fixed Code

```python
# Check if it's actually a regression
if metric_name in ['on_time_rate', 'item_accuracy', 'cx_score']:
    # For these metrics, higher is better
    if current_value < baseline_value:
        description = f"{metric_name} regressed from {baseline_value:.2f} to {current_value:.2f}"
    else:
        description = f"{metric_name} improved from {baseline_value:.2f} to {current_value:.2f}"
elif metric_name in ['cancellation_rate', 'refund_rate', 'support_rate']:
    # For these metrics, lower is better
    if current_value > baseline_value:
        description = f"{metric_name} regressed from {baseline_value:.2f} to {current_value:.2f}"
    else:
        description = f"{metric_name} improved from {baseline_value:.2f} to {current_value:.2f}"
else:
    # For any other metric, just say changed
    description = f"{metric_name} changed from {baseline_value:.2f} to {current_value:.2f}"
```

---

## Real-World Examples

### Example 1: True Regression

**Scenario**: Batching threshold increased

```
Baseline: On-time rate = 92%
Current:  On-time rate = 78%

What happened:
- Orders wait longer before dasher assignment
- More orders arrive late
- Customer complaints increase

This is a TRUE REGRESSION ✅
```

### Example 2: Improvement (Currently Mislabeled)

**Scenario**: ETA model fixed, buffer time added

```
Baseline: On-time rate = 20%
Current:  On-time rate = 38%

What happened:
- ETA predictions became more accurate
- Buffer time prevents late deliveries
- More orders arrive on time

This is an IMPROVEMENT (not regression!)
```

### Example 3: No Change

**Scenario**: Normal operations

```
Baseline: On-time rate = 92%
Current:  On-time rate = 91%

Delta: -1 percentage point (-1.1%)

What happened:
- Small fluctuation within normal range
- Not significant enough to flag

No incident created ✅
```

---

## Summary

### How On-Time Rate Regresses

1. **True Regression**: Rate decreases (e.g., 92% → 78%)
   - Caused by: Policy changes, supply issues, merchant problems, etc.
   - Impact: More late orders, worse customer experience

2. **Improvement** (currently mislabeled): Rate increases (e.g., 20% → 38%)
   - Caused by: Fixes, optimizations, better models
   - Impact: More on-time orders, better customer experience
   - **Bug**: System calls this "regression" but it's actually improvement

### The Fix Needed

The system should:
- ✅ Detect significant changes (current behavior)
- ✅ Distinguish improvements from regressions (needs fix)
- ✅ Use correct language ("improved" vs "regressed")
- ✅ Still flag improvements for visibility (they're still anomalies!)

### Why Flag Improvements?

Even improvements should be flagged because:
- They indicate something changed (need to understand why)
- They might be temporary (need to sustain)
- They help identify what's working (can replicate)

But they should be labeled correctly as "improvements" not "regressions"!


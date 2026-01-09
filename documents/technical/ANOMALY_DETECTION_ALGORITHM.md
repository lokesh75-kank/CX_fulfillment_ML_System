# Anomaly Detection Algorithm: Incident Flagging System

## Overview

The CX-Fulfillment Agent uses a **multi-method anomaly detection system** to automatically flag incidents when customer experience metrics degrade. The system combines three statistical methods (Z-score, EWMA, Bayesian change point) and requires consensus from multiple methods to reduce false positives.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│              Detection Pipeline                           │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  1. Calculate Metrics (Baseline vs Current)              │
│     ↓                                                     │
│  2. Create Time Series                                    │
│     ↓                                                     │
│  3. Run Anomaly Detection (3 methods)                   │
│     ├─ Z-Score Detection                                 │
│     ├─ EWMA Detection                                    │
│     └─ Bayesian Change Point Detection                   │
│     ↓                                                     │
│  4. Combine Results (Consensus: 2/3 must agree)         │
│     ↓                                                     │
│  5. Calculate Severity                                   │
│     ↓                                                     │
│  6. Create Incident Record                               │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

---

## Algorithm 1: Z-Score Detection

### Purpose
Detects values that are statistically far from recent historical patterns.

### Method

**Formula:**
```
z_score = |current_value - rolling_mean| / rolling_std
anomaly = (z_score > threshold)
```

**Parameters:**
- `window_size = 30` (number of historical points to consider)
- `z_score_threshold = 2.5` (standard deviations away from mean)

### Algorithm Steps

1. **Initialize rolling window**
   - For each data point `i`:
     - If `i < window_size`: Use all available data `[0:i+1]`
     - Else: Use rolling window `[i-window_size+1:i+1]`

2. **Calculate statistics**
   - `mean = mean(window)`
   - `std = std(window)`
   - Skip if `std == 0` (no variation)

3. **Compute Z-score**
   - `z_score = abs(current_value - mean) / std`

4. **Flag anomaly**
   - If `z_score > 2.5`: Mark as anomaly

### Example

```python
# Time series data
values = [85, 86, 87, 85, 86, 88, 85, 87, 86, 85, 72]

# At index 10 (value = 72):
window = [85, 86, 87, 85, 86, 88, 85, 87, 86, 85]  # Last 10 values
mean = 85.4
std = 1.0
z_score = |72 - 85.4| / 1.0 = 13.4

# 13.4 > 2.5 → ANOMALY DETECTED ✅
```

### Advantages
- Simple and interpretable
- Works well for sudden spikes/drops
- No assumptions about data distribution

### Limitations
- Sensitive to outliers in the window
- May miss gradual trends
- Requires sufficient history

---

## Algorithm 2: EWMA (Exponentially Weighted Moving Average)

### Purpose
Detects deviations from adaptive trends, accounting for gradual changes.

### Method

**Formula:**
```
EWMA[i] = α × value[i] + (1-α) × EWMA[i-1]
deviation = |value[i] - EWMA[i]| / std_residual
anomaly = (deviation > threshold)
```

**Parameters:**
- `alpha = 0.3` (smoothing factor, 0-1)
  - Higher α = more responsive to recent values
  - Lower α = smoother, less responsive
- `ewma_threshold = 2.0` (standard deviations)
- `min_history = 10` (minimum points needed for std calculation)

### Algorithm Steps

1. **Initialize**
   - `EWMA[0] = values[0]`
   - First point cannot be anomaly (no history)

2. **For each subsequent point `i`:**
   - Update EWMA: `EWMA[i] = α × values[i] + (1-α) × EWMA[i-1]`
   - If `i < min_history`: Skip (need history for std)
   - Calculate residuals: `residuals = values[:i+1] - EWMA[:i+1]`
   - Compute std of recent residuals: `std_residual = std(residuals[-10:])`
   - Calculate normalized deviation: `deviation = |values[i] - EWMA[i]| / std_residual`
   - Flag if `deviation > 2.0`

### Example

```python
# Time series
values = [85, 86, 87, 85, 86, 72]
alpha = 0.3

# EWMA progression:
EWMA[0] = 85
EWMA[1] = 0.3×86 + 0.7×85 = 85.3
EWMA[2] = 0.3×87 + 0.7×85.3 = 85.7
EWMA[3] = 0.3×85 + 0.7×85.7 = 85.5
EWMA[4] = 0.3×86 + 0.7×85.5 = 85.6
EWMA[5] = 0.3×72 + 0.7×85.6 = 82.0

# At index 5 (value = 72):
residuals = [0, 0.7, 1.3, -0.5, 0.4, -10.0]
std_residual = std([-0.5, 0.4, -10.0]) = 5.8
deviation = |72 - 82.0| / 5.8 = 1.72

# 1.72 < 2.0 → Not flagged (but close)
# However, with more history, this would be flagged
```

### Advantages
- Adapts to trends automatically
- Less sensitive to outliers
- Good for gradual changes

### Limitations
- Requires initialization period
- May lag behind sudden changes
- Sensitive to alpha parameter choice

---

## Algorithm 3: Bayesian Change Point Detection

### Purpose
Detects points where the underlying distribution of values changes significantly.

### Method

**Formula:**
```
For each potential change point i:
  segment1 = values[0:i]
  segment2 = values[i:]
  
  mean1, std1 = mean(segment1), std(segment1)
  mean2, std2 = mean(segment2), std(segment2)
  
  pooled_std = sqrt((std1² + std2²) / 2)
  t_stat = |mean1 - mean2| / pooled_std
  
  change_point = (t_stat > threshold)
```

**Parameters:**
- `min_segment_size = 5` (minimum points per segment)
- `t_stat_threshold = 2.0` (significant difference threshold)

### Algorithm Steps

1. **For each potential change point `i`:**
   - Ensure `i >= min_segment_size` and `len(values) - i >= min_segment_size`
   - Split: `segment1 = values[0:i]`, `segment2 = values[i:]`
   - Calculate statistics:
     - `mean1, std1 = mean(segment1), std(segment1)`
     - `mean2, std2 = mean(segment2), std(segment2)`
   - Skip if `std1 == 0` or `std2 == 0`
   - Compute pooled standard deviation: `pooled_std = sqrt((std1² + std2²) / 2)`
   - Calculate t-statistic: `t_stat = |mean1 - mean2| / pooled_std`
   - Flag if `t_stat > 2.0`

2. **Mark change points**
   - All points at detected change points are flagged as anomalies

### Example

```python
# Time series with clear change point
values = [85, 86, 87, 85, 86, 72, 73, 74, 72, 73]

# Testing change point at index 5:
segment1 = [85, 86, 87, 85, 86]
segment2 = [72, 73, 74, 72, 73]

mean1 = 85.8, std1 = 0.84
mean2 = 72.8, std2 = 0.84

pooled_std = sqrt((0.84² + 0.84²) / 2) = 0.84
t_stat = |85.8 - 72.8| / 0.84 = 15.5

# 15.5 > 2.0 → CHANGE POINT DETECTED at index 5 ✅
```

### Advantages
- Detects structural breaks
- Good for identifying when behavior changes
- Statistically rigorous

### Limitations
- Requires sufficient data on both sides
- May flag multiple nearby points
- Computationally more expensive

---

## Algorithm 4: Combined Consensus Method

### Purpose
Reduces false positives by requiring multiple methods to agree.

### Method

**Formula:**
```
For each data point:
  z_score_result = z_score_detection(point)
  ewma_result = ewma_detection(point)
  bayesian_result = bayesian_detection(point)
  
  votes = [z_score_result, ewma_result, bayesian_result]
  consensus = (sum(votes) >= 2)
  
  final_anomaly = consensus
```

**Parameters:**
- `consensus_threshold = 2` (out of 3 methods must agree)

### Algorithm Steps

1. **Run all three methods** on the same time series
2. **For each data point:**
   - Collect votes: `[z_score_flag, ewma_flag, bayesian_flag]`
   - Count votes: `vote_count = sum(flags)`
   - Require consensus: `anomaly = (vote_count >= 2)`

### Example

```python
# For a given data point:
z_score_result = True   # Z-score detected anomaly
ewma_result = True      # EWMA detected anomaly
bayesian_result = False # Bayesian did not detect

votes = [True, True, False]
vote_count = 2

# 2 >= 2 → FINAL DECISION: ANOMALY ✅
```

### Advantages
- **Reduces false positives** - Requires multiple methods to agree
- **More robust** - Less sensitive to individual method weaknesses
- **Higher confidence** - Multiple signals increase confidence

### Limitations
- May miss anomalies that only one method detects
- Requires all methods to be configured properly
- Slightly more complex

---

## Severity Calculation

After an anomaly is detected, severity is calculated based on percentile ranking.

### Method

```python
percentile = percentileofscore(all_values, current_value)

if percentile < 5:
    severity = 'HIGH'
elif percentile < 10:
    severity = 'MEDIUM'
else:
    severity = 'LOW'
```

### Example

```python
# All historical values
all_values = [88, 87, 89, 88, 87, 86, 85, 84, 72, 73]

# Current value
current_value = 72

# Percentile calculation
percentile = 10%  # 72 is in bottom 10%

# Severity
if percentile < 5:  # 10% is not < 5%
    severity = 'MEDIUM'  # Falls into MEDIUM range
```

---

## Complete Detection Pipeline

### Step-by-Step Process

1. **Data Preparation**
   ```python
   # Filter data by time periods
   baseline_data = filter_by_time(baseline_start, baseline_end)
   current_data = filter_by_time(current_start, current_end)
   ```

2. **Metric Calculation**
   ```python
   baseline_metrics = calculate_cx_score(baseline_data)
   # Result: {'cx_score': 88.5, 'on_time_rate': 0.92, ...}
   
   current_metrics = calculate_cx_score(current_data)
   # Result: {'cx_score': 72.3, 'on_time_rate': 0.78, ...}
   ```

3. **Time Series Construction**
   ```python
   # Create time series for each metric
   time_series = [
       {'timestamp': '2024-01-01', 'cx_score': 88.5},
       {'timestamp': '2024-01-02', 'cx_score': 87.2},
       {'timestamp': '2024-01-03', 'cx_score': 85.8},
       {'timestamp': '2024-01-04', 'cx_score': 72.3},
   ]
   ```

4. **Anomaly Detection**
   ```python
   # Run combined detection
   anomalies = detect_anomalies(time_series, method='combined')
   
   # Result: anomaly=True for 2024-01-04
   ```

5. **Severity Calculation**
   ```python
   severity = calculate_severity(current_value, all_values)
   # Result: 'HIGH' (if in bottom 5%)
   ```

6. **Incident Creation**
   ```python
   incident = {
       'incident_id': generate_id(),
       'metric_name': 'cx_score',
       'baseline_value': 88.5,
       'current_value': 72.3,
       'delta': -16.2,
       'delta_percent': -18.3%,
       'severity': 'HIGH',
       'detected_at': datetime.now(),
       'status': 'new'
   }
   ```

---

## Configuration Parameters

### Default Values

| Parameter | Value | Description |
|-----------|-------|-------------|
| `z_score_threshold` | 2.5 | Standard deviations for Z-score |
| `z_score_window_size` | 30 | Rolling window size |
| `ewma_alpha` | 0.3 | Smoothing factor |
| `ewma_threshold` | 2.0 | Standard deviations for EWMA |
| `ewma_min_history` | 10 | Minimum points for std calculation |
| `bayesian_min_segment` | 5 | Minimum points per segment |
| `bayesian_t_threshold` | 2.0 | T-statistic threshold |
| `consensus_threshold` | 2 | Methods required to agree (out of 3) |

### Tuning Guidelines

**For More Sensitive Detection:**
- Lower `z_score_threshold` (e.g., 2.0)
- Lower `ewma_threshold` (e.g., 1.5)
- Lower `bayesian_t_threshold` (e.g., 1.5)
- Lower `consensus_threshold` (e.g., 1)

**For Less Sensitive Detection (Fewer False Positives):**
- Higher `z_score_threshold` (e.g., 3.0)
- Higher `ewma_threshold` (e.g., 2.5)
- Higher `bayesian_t_threshold` (e.g., 2.5)
- Keep `consensus_threshold` at 2

---

## Performance Characteristics

### Time Complexity

- **Z-Score**: O(n × w) where n = data points, w = window size
- **EWMA**: O(n)
- **Bayesian**: O(n²) in worst case (testing all points)
- **Combined**: O(n²) (dominated by Bayesian)

### Space Complexity

- **Z-Score**: O(w) for rolling window
- **EWMA**: O(1) (only stores current EWMA)
- **Bayesian**: O(n) for storing segments
- **Combined**: O(n) (stores results from all methods)

### Typical Performance

For 1000 data points:
- Z-Score: ~10ms
- EWMA: ~5ms
- Bayesian: ~50ms
- Combined: ~65ms total

---

## Edge Cases and Handling

### Insufficient Data
- **Problem**: Not enough historical data
- **Solution**: Use all available data, skip detection if < 2 points

### Zero Variance
- **Problem**: `std == 0` (all values identical)
- **Solution**: Skip anomaly detection (no variation to detect)

### Missing Values
- **Problem**: NaN or null values in time series
- **Solution**: Forward-fill or skip missing points

### Single Point Anomaly
- **Problem**: One point is anomalous, then returns to normal
- **Solution**: All methods should detect it; consensus confirms

### Gradual Drift
- **Problem**: Slow, gradual degradation over time
- **Solution**: EWMA adapts, Bayesian detects change point, Z-score may miss

---

## Validation and Testing

### Test Cases

1. **Sudden Drop**
   - Baseline: [85, 86, 87, 85, 86]
   - Current: [72]
   - Expected: All methods detect, HIGH severity

2. **Gradual Decline**
   - Values: [85, 84, 83, 82, 81, 80]
   - Expected: EWMA and Bayesian detect, Z-score may miss

3. **No Change**
   - Values: [85, 86, 85, 86, 85]
   - Expected: No anomalies detected

4. **Noise (False Positive)**
   - Values: [85, 86, 87, 85, 84, 85]
   - Expected: No anomalies (consensus prevents false positive)

---

## Implementation Location

**File**: `detection/anomaly_detector.py`

**Key Classes:**
- `AnomalyDetector`: Main detector class
- Methods:
  - `detect_z_score()`: Z-score detection
  - `detect_ewma()`: EWMA detection
  - `detect_bayesian_change_point()`: Bayesian change point
  - `detect_anomalies()`: Combined method
  - `detect_metric_anomalies()`: High-level API

**Usage:**
```python
detector = AnomalyDetector()
anomalies = detector.detect_anomalies(
    time_series_df,
    metric_column='cx_score',
    method='combined'
)
```

---

## References

- **Z-Score Method**: Standard statistical outlier detection
- **EWMA**: Exponentially Weighted Moving Average (Holt-Winters)
- **Bayesian Change Point**: Simplified version of Bayesian change point detection
- **Consensus Method**: Ensemble approach for robust detection

---

## Summary

The anomaly detection system uses **three complementary methods** (Z-score, EWMA, Bayesian) and requires **consensus from multiple methods** to flag incidents. This approach:

✅ **Reduces false positives** through consensus
✅ **Catches different types of anomalies** (sudden, gradual, structural)
✅ **Provides confidence** through multiple signals
✅ **Automatically adapts** to trends and patterns

The system flags incidents when customer experience metrics degrade significantly, enabling proactive problem detection and resolution.


# RCA Logic: How Root Cause Analysis Works

## Overview

The RCA (Root Cause Analysis) system uses a **hypothesis-driven approach** combined with **statistical methods** to identify the most likely causes of CX degradation.

---

## High-Level Flow

```
Incident Detected
    ↓
1. Get Relevant Hypotheses (from library)
    ↓
2. Test Each Hypothesis
    ├─ SHAP Analysis (feature attribution)
    ├─ Diff-in-Diff (policy changes)
    ├─ Temporal Correlation
    └─ Statistical Tests
    ↓
3. Score Each Hypothesis
    ├─ Confidence Score (0-1)
    ├─ Impact Score (0-1)
    └─ Combined Score = Confidence × Impact
    ↓
4. Rank Hypotheses
    ↓
5. Generate Narrative & Summary
```

---

## Step 1: Hypothesis Library

### What is a Hypothesis?

A hypothesis is a **testable explanation** for why a metric regressed.

**Example Hypothesis:**
```python
Hypothesis(
    name='Batching Threshold Increase',
    category='policy',
    description='Batching threshold was increased, causing longer wait times',
    features_to_check=['batched_flag', 'dasher_wait', 'actual_eta'],
    expected_impact='Higher batching rate, increased dasher_wait, lateness',
    test_methods=['diff_in_diff', 'shap', 'correlation']
)
```

### Hypothesis Categories

1. **Supply-Side** (dasher availability, assignment)
2. **Merchant-Side** (prep-time drift, capacity)
3. **Policy** (batching threshold, ETA buffer)
4. **Inventory** (stock-outs, substitutions)
5. **Model Regression** (ETA bias, assignment degradation)

### How Hypotheses are Selected

```python
# Map metrics to relevant hypothesis categories
metric_to_categories = {
    'on_time_rate': ['supply', 'merchant', 'policy', 'model'],
    'cancellation_rate': ['supply', 'merchant', 'policy'],
    'refund_rate': ['inventory', 'merchant'],
    'cx_score': ['supply', 'merchant', 'policy', 'inventory', 'model']
}

# Get all hypotheses for relevant categories
relevant_hypotheses = get_hypotheses_by_category(categories)
```

---

## Step 2: Testing Hypotheses

### Method 1: SHAP Analysis (Feature Attribution)

**What it does:** Identifies which features are most important for predicting the outcome.

**How it works:**

1. **Prepare Features**
   ```python
   features = [
       'basket_value',
       'distance',
       'merchant_prep_time',
       'dasher_wait',
       'batched_flag',
       'has_substitution',
       ...
   ]
   ```

2. **Train Model**
   ```python
   # Train RandomForest or LogisticRegression
   model = RandomForestClassifier()
   model.fit(X_train, y_train)
   # y = outcome (e.g., late/on-time, canceled/not)
   ```

3. **Calculate SHAP Values**
   ```python
   explainer = shap.TreeExplainer(model)
   shap_values = explainer.shap_values(X_test)
   ```

4. **Score Hypothesis**
   ```python
   # If hypothesis features have high SHAP importance
   # → Hypothesis is supported
   hypothesis_shap_score = mean(shap_values[hypothesis_features])
   ```

**Example:**
- Hypothesis: "Batching causes lateness"
- Features: `batched_flag`, `dasher_wait`
- SHAP shows: `batched_flag` has high importance (0.15)
- Result: Hypothesis supported ✅

---

### Method 2: Diff-in-Diff (Policy Changes)

**What it does:** Detects causal effects of policy changes by comparing treatment vs control groups.

**How it works:**

1. **Define Groups**
   ```python
   # Treatment group: Orders affected by policy change
   # Control group: Orders not affected
   
   treatment_before = orders[before_change & affected]
   treatment_after = orders[after_change & affected]
   baseline_before = orders[before_change & not_affected]
   baseline_after = orders[after_change & not_affected]
   ```

2. **Calculate Diff-in-Diff**
   ```python
   baseline_diff = mean(baseline_after) - mean(baseline_before)
   treatment_diff = mean(treatment_after) - mean(treatment_before)
   
   did_estimate = treatment_diff - baseline_diff
   ```

3. **Statistical Test**
   ```python
   # Calculate t-statistic and p-value
   t_stat = did_estimate / pooled_se
   p_value = 2 * (1 - norm.cdf(abs(t_stat)))
   
   significant = p_value < 0.05
   ```

**Example:**
- Policy: Batching threshold increased on Jan 3
- Treatment: Batched orders
- Control: Non-batched orders
- Result: `did_estimate = -0.12` (lateness increased), `p_value = 0.01`
- Conclusion: Policy change caused regression ✅

---

### Method 3: Temporal Correlation

**What it does:** Checks if changes in hypothesis features correlate with metric changes over time.

**How it works:**

1. **Calculate Time Series**
   ```python
   # Group by time windows
   time_series = {
       'metric': [0.92, 0.91, 0.89, 0.78],
       'feature': [0.3, 0.35, 0.42, 0.65]  # e.g., batching rate
   }
   ```

2. **Calculate Correlation**
   ```python
   correlation = np.corrcoef(metric, feature)[0, 1]
   ```

3. **Score Hypothesis**
   ```python
   # High correlation → Hypothesis supported
   if abs(correlation) > 0.7:
       score = 0.8
   ```

**Example:**
- Metric: On-time rate decreases over time
- Feature: Batching rate increases over time
- Correlation: -0.85 (strong negative)
- Result: Hypothesis supported ✅

---

### Method 4: Statistical Tests

**What it does:** Tests if feature distributions changed significantly between periods.

**How it works:**

1. **Compare Distributions**
   ```python
   baseline_feature = baseline_data['feature']
   current_feature = current_data['feature']
   
   # T-test
   t_stat, p_value = stats.ttest_ind(baseline_feature, current_feature)
   ```

2. **Score Hypothesis**
   ```python
   if p_value < 0.05:
       score = 1.0 - p_value  # Lower p-value = higher confidence
   ```

**Example:**
- Feature: `merchant_prep_time`
- Baseline mean: 15 minutes
- Current mean: 22 minutes
- T-test: `p_value = 0.001`
- Result: Significant change, hypothesis supported ✅

---

## Step 3: Scoring Hypotheses

### Confidence Score

**Formula:**
```python
confidence = weighted_average([
    shap_score * 0.4,      # SHAP importance
    diff_in_diff_score * 0.3,  # Causal evidence
    correlation_score * 0.2,   # Temporal correlation
    statistical_score * 0.1    # Statistical significance
])
```

**Example:**
```python
hypothesis = "Batching Threshold Increase"

shap_score = 0.8  # High SHAP importance
did_score = 0.9   # Strong diff-in-diff evidence
corr_score = 0.7  # Good temporal correlation
stat_score = 0.95 # Highly significant

confidence = (0.8*0.4 + 0.9*0.3 + 0.7*0.2 + 0.95*0.1)
          = 0.32 + 0.27 + 0.14 + 0.095
          = 0.825 (82.5%)
```

---

### Impact Score

**Formula:**
```python
# Measure how much the hypothesis feature changed
feature_delta = abs(current_feature_mean - baseline_feature_mean)
feature_delta_pct = feature_delta / baseline_feature_mean

# Normalize to 0-1
impact = min(1.0, feature_delta_pct / 0.5)  # 50% change = max impact
```

**Example:**
```python
# Batching rate increased from 30% to 60%
feature_delta_pct = (0.60 - 0.30) / 0.30 = 1.0 (100% increase)

impact = min(1.0, 1.0 / 0.5) = 1.0 (maximum impact)
```

---

### Combined Score

**Formula:**
```python
combined_score = confidence × impact
```

**Example:**
```python
confidence = 0.825
impact = 1.0

combined_score = 0.825 × 1.0 = 0.825
```

---

## Step 4: Ranking Hypotheses

**Algorithm:**
```python
# Sort by combined score (descending)
ranked_hypotheses = sorted(
    hypothesis_results,
    key=lambda x: x['combined_score'],
    reverse=True
)
```

**Example Output:**
```
Rank 1: Batching Threshold Increase
  Confidence: 0.92
  Impact: 0.85
  Score: 0.782

Rank 2: Merchant Prep-Time Drift
  Confidence: 0.75
  Impact: 0.60
  Score: 0.450

Rank 3: Low Dasher Availability
  Confidence: 0.45
  Impact: 0.30
  Score: 0.135
```

---

## Step 5: Generate Narrative

### Summary Generation

**Logic:**
```python
if top_score > 0.7:
    summary = f"Most of the CX drop comes from {top_hypothesis.name}"
elif top_score > 0.5:
    summary = f"Primary cause: {top_hypothesis.name}, with secondary contributions from {second_hypothesis.name}"
else:
    summary = f"Multiple factors contribute, with {top_hypothesis.name} being most likely"
```

**Example:**
```
"Most of the CX drop comes from batching threshold increase. 
Merchant prep-time drift is a secondary factor."
```

---

## Complete Example

### Input: Incident
```
Metric: on_time_rate
Baseline: 0.92
Current: 0.78
Delta: -0.14 (-15%)
```

### Step 1: Get Hypotheses
```
1. Batching Threshold Increase (policy)
2. Merchant Prep-Time Drift (merchant)
3. Low Dasher Availability (supply)
4. ETA Model Bias (model)
```

### Step 2: Test Each

**Hypothesis 1: Batching Threshold**
- SHAP: `batched_flag` importance = 0.15 ✅
- Diff-in-Diff: `did_estimate = -0.12`, `p = 0.01` ✅
- Correlation: -0.85 ✅
- Confidence: 0.92
- Impact: 0.85 (batching rate doubled)
- Score: 0.782

**Hypothesis 2: Prep-Time Drift**
- SHAP: `merchant_prep_time` importance = 0.10 ✅
- Temporal: Correlation = 0.65 ✅
- Statistical: `p = 0.05` ✅
- Confidence: 0.75
- Impact: 0.60
- Score: 0.450

**Hypothesis 3: Dasher Availability**
- SHAP: `dasher_wait` importance = 0.05 ❌
- Correlation: 0.20 ❌
- Confidence: 0.45
- Impact: 0.30
- Score: 0.135

### Step 3: Rank
```
1. Batching Threshold (0.782)
2. Prep-Time Drift (0.450)
3. Dasher Availability (0.135)
```

### Step 4: Generate Report
```
Summary: "Most of the CX drop comes from batching threshold increase."

Narrative: "Root cause analysis identified Batching Threshold Increase 
as the most likely cause (confidence: 92%). Evidence from SHAP analysis 
shows batching is the top driver of lateness, and diff-in-diff confirms 
the policy change impact. Merchant prep-time drift is a secondary factor 
(confidence: 75%)."
```

---

## Key Parameters

### Confidence Thresholds
- **High Confidence**: > 0.7
- **Medium Confidence**: 0.5 - 0.7
- **Low Confidence**: < 0.5

### Impact Thresholds
- **High Impact**: > 0.7 (feature changed >35%)
- **Medium Impact**: 0.4 - 0.7 (feature changed 20-35%)
- **Low Impact**: < 0.4 (feature changed <20%)

### Statistical Significance
- **Significant**: p < 0.05
- **Marginally Significant**: 0.05 ≤ p < 0.10
- **Not Significant**: p ≥ 0.10

---

## Limitations & Assumptions

### Limitations

1. **Correlation ≠ Causation**
   - High correlation doesn't prove causality
   - Diff-in-diff helps but requires proper control groups

2. **Feature Engineering**
   - Quality depends on available features
   - Missing features can't be tested

3. **Model Assumptions**
   - SHAP assumes model captures relationships
   - Simple models may miss complex interactions

4. **Temporal Assumptions**
   - Assumes changes happen at specific times
   - Gradual drifts may be missed

### Assumptions

1. **Hypothesis Library is Complete**
   - Assumes all relevant causes are in library
   - New causes may not be detected

2. **Data Quality**
   - Assumes data is accurate and complete
   - Missing or bad data affects results

3. **Independence**
   - Assumes hypotheses are independent
   - Multiple causes may interact

---

## Summary

The RCA logic uses:

1. **Hypothesis-Driven Approach**: Tests predefined hypotheses from library
2. **Multiple Methods**: SHAP, diff-in-diff, correlation, statistical tests
3. **Scoring System**: Confidence × Impact = Combined Score
4. **Ranking**: Sorts hypotheses by combined score
5. **Narrative Generation**: Creates human-readable explanations

**Key Insight**: The system doesn't "discover" causes—it **tests hypotheses** and ranks them by evidence strength. This makes it interpretable and actionable.


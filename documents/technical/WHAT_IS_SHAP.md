# What is SHAP?

## Overview

**SHAP** stands for **SHapley Additive exPlanations**. It's a method for explaining machine learning model predictions by attributing the contribution of each feature to the final prediction.

---

## The Problem SHAP Solves

When a machine learning model makes a prediction, you often want to know:
- **Why** did the model predict this?
- **Which features** were most important?
- **How much** did each feature contribute?

**Example:**
```
Model predicts: Order will be LATE (probability: 0.85)

Why?
- Batching flag: +0.30 (increased probability by 30%)
- Dasher wait time: +0.25 (increased probability by 25%)
- Merchant prep time: +0.20 (increased probability by 20%)
- Distance: +0.10 (increased probability by 10%)
```

SHAP provides these attributions.

---

## The Core Concept

### Shapley Values (from Game Theory)

SHAP is based on **Shapley values** from cooperative game theory:

**Question:** How do you fairly distribute the "payout" (prediction) among the "players" (features)?

**Answer:** Each feature gets credit equal to its **average marginal contribution** across all possible feature combinations.

### Mathematical Definition

For a feature `i`, the SHAP value is:

```
SHAP_i = Σ [ (|S|! × (n - |S| - 1)!) / n! ] × [f(S ∪ {i}) - f(S)]
```

Where:
- `S` = subset of features (without feature `i`)
- `n` = total number of features
- `f(S)` = model prediction with features in `S`
- `f(S ∪ {i})` = model prediction with features in `S` plus feature `i`

**In simple terms:** SHAP value = average of how much the prediction changes when feature `i` is added to all possible feature combinations.

---

## How SHAP Works (Step by Step)

### Step 1: Train a Model

```python
# Features
X = [
    ['batched', 'distance', 'prep_time', 'dasher_wait'],
    ['not_batched', 'distance', 'prep_time', 'dasher_wait'],
    ...
]

# Outcome (what we're predicting)
y = [1, 0, 1, 0, ...]  # 1 = late, 0 = on-time

# Train model
model = RandomForestClassifier()
model.fit(X, y)
```

### Step 2: Create SHAP Explainer

```python
import shap

explainer = shap.TreeExplainer(model)  # For tree-based models
# or
explainer = shap.LinearExplainer(model)  # For linear models
```

### Step 3: Calculate SHAP Values

```python
# For a specific prediction
shap_values = explainer.shap_values(X_sample)

# Result:
# shap_values = {
#     'batched': 0.30,
#     'distance': 0.10,
#     'prep_time': 0.20,
#     'dasher_wait': 0.25
# }
```

### Step 4: Interpret Results

```python
# Base prediction (average)
base_value = 0.5  # 50% chance of being late

# For a specific order:
prediction = base_value + sum(shap_values.values())
prediction = 0.5 + 0.30 + 0.10 + 0.20 + 0.25 = 1.35 → 85% late

# Feature contributions:
# batched: +30% (most important!)
# dasher_wait: +25%
# prep_time: +20%
# distance: +10%
```

---

## Example: Why is an Order Late?

### Input Data
```python
order = {
    'batched': True,
    'distance': 5.2 miles,
    'prep_time': 18 minutes,
    'dasher_wait': 8 minutes
}
```

### Model Prediction
```python
prediction = model.predict_proba(order)
# Result: 85% chance of being late
```

### SHAP Values
```python
shap_values = explainer.shap_values(order)

# Result:
{
    'batched': +0.30,      # Batching increased late probability by 30%
    'dasher_wait': +0.25,  # Wait time increased late probability by 25%
    'prep_time': +0.20,    # Prep time increased late probability by 20%
    'distance': +0.10       # Distance increased late probability by 10%
}
```

### Interpretation

**Why is this order late?**
1. **Batching** is the biggest factor (+30%)
2. **Dasher wait time** is second (+25%)
3. **Prep time** contributes (+20%)
4. **Distance** has minor impact (+10%)

**Conclusion:** Batching is the primary driver of lateness for this order.

---

## How SHAP is Used in RCA

### In Our System

1. **Train Model**
   ```python
   # Predict: Will order be late?
   model = RandomForestClassifier()
   model.fit(features, is_late)
   ```

2. **Calculate Feature Importance**
   ```python
   shap_values = explainer.shap_values(all_orders)
   
   # Average SHAP values across all orders
   avg_shap = {
       'batched_flag': 0.15,
       'dasher_wait': 0.12,
       'merchant_prep_time': 0.10,
       'distance': 0.08
   }
   ```

3. **Test Hypothesis**
   ```python
   hypothesis = "Batching causes lateness"
   hypothesis_features = ['batched_flag', 'dasher_wait']
   
   # Check if hypothesis features have high SHAP importance
   hypothesis_shap_score = avg_shap['batched_flag']  # 0.15
   
   if hypothesis_shap_score > 0.10:
       # Hypothesis supported ✅
       confidence += 0.4
   ```

---

## Key Properties of SHAP

### 1. **Additivity**
```
prediction = base_value + Σ(SHAP_i for all features i)
```

The SHAP values sum to the difference between prediction and base value.

### 2. **Efficiency**
```
Σ(SHAP_i) = prediction - base_value
```

All contributions add up exactly.

### 3. **Symmetry**
If two features contribute equally, they get equal SHAP values.

### 4. **Dummy Feature**
Features that don't affect prediction get SHAP value = 0.

---

## Types of SHAP Explainers

### 1. **TreeExplainer** (Used in Our System)
- For tree-based models (RandomForest, XGBoost, etc.)
- Fast and exact
- Best for our use case

### 2. **LinearExplainer**
- For linear models (LogisticRegression, etc.)
- Very fast
- Exact for linear models

### 3. **KernelExplainer**
- Model-agnostic (works with any model)
- Slower (uses sampling)
- More general but computationally expensive

### 4. **DeepExplainer**
- For neural networks
- Fast for deep learning models

---

## Advantages of SHAP

### ✅ **Interpretable**
- Clear feature attributions
- Easy to understand "why"

### ✅ **Theoretically Grounded**
- Based on game theory (Shapley values)
- Has mathematical guarantees

### ✅ **Consistent**
- Same feature gets same attribution in similar contexts
- Reliable across predictions

### ✅ **Model-Agnostic**
- Works with any model type
- Can compare different models

---

## Limitations of SHAP

### ⚠️ **Computational Cost**
- Can be slow for many features
- TreeExplainer helps (faster than KernelExplainer)

### ⚠️ **Assumes Model is Correct**
- SHAP explains the model, not reality
- If model is wrong, SHAP is wrong

### ⚠️ **Feature Interactions**
- SHAP averages over interactions
- May miss complex feature interactions

### ⚠️ **Requires Data**
- Needs sufficient data to be reliable
- Small datasets may give noisy results

---

## Real-World Example in Our System

### Scenario: On-Time Rate Dropped

**Question:** Why did on-time rate drop?

**Step 1: Train Model**
```python
# Features: batched_flag, dasher_wait, prep_time, distance
# Outcome: is_late (1 = late, 0 = on-time)

model.fit(features, is_late)
```

**Step 2: Calculate SHAP**
```python
shap_values = explainer.shap_values(current_orders)

# Average SHAP importance:
avg_importance = {
    'batched_flag': 0.15,      # High importance!
    'dasher_wait': 0.12,
    'merchant_prep_time': 0.08,
    'distance': 0.05
}
```

**Step 3: Test Hypothesis**
```python
hypothesis = "Batching Threshold Increase"

# Check if batching has high importance
if avg_importance['batched_flag'] > 0.10:
    # Hypothesis supported ✅
    shap_score = 0.8  # High confidence
```

**Step 4: Combine with Other Evidence**
```python
confidence = (
    shap_score * 0.4 +        # SHAP: 0.8 × 0.4 = 0.32
    diff_in_diff_score * 0.3 + # Diff-in-Diff: 0.9 × 0.3 = 0.27
    correlation_score * 0.2 +  # Correlation: 0.7 × 0.2 = 0.14
    statistical_score * 0.1     # Statistical: 0.95 × 0.1 = 0.095
)
# Total confidence = 0.825 (82.5%)
```

**Result:** Batching is the most likely cause (82.5% confidence)

---

## Summary

**SHAP** = Method to explain model predictions by attributing contribution to each feature

**Key Points:**
- Based on Shapley values from game theory
- Provides feature importance scores
- Used in RCA to test hypotheses
- Shows which features drive predictions

**In Our System:**
- Trains model to predict outcomes (late/on-time, canceled/not)
- Calculates SHAP values for each feature
- Uses SHAP importance to test hypotheses
- Combines with other methods (diff-in-diff, correlation) for final confidence

**Bottom Line:** SHAP answers "which features matter most?" by quantifying each feature's contribution to the model's prediction.


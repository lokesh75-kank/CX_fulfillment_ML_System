# System Capabilities: What Can CX-Fulfillment Agent Detect?

## Overview

**CX-Fulfillment Agent is NOT limited to batching threshold monitoring.** It's a **general-purpose customer experience monitoring and root cause analysis system** that can detect **ANY** type of CX degradation, regardless of the root cause.

---

## What the System Monitors

### CX Metrics (What We Track)

1. **On-time Delivery Rate** - Are orders arriving on time?
2. **Item Accuracy** - Are customers getting the right items?
3. **Cancellation Rate** - How many orders are being canceled?
4. **Refund Rate** - How often are refunds issued?
5. **Support Contact Rate** - How many customers need support?
6. **Rating Proxy** - What are customers rating us?
7. **Overall CX Score** - Weighted composite of all metrics

### Detection Capabilities

The system automatically detects:
- **Metric regressions** (any metric dropping)
- **Anomalies** (unusual patterns)
- **Cohort-specific issues** (specific regions, categories, times)
- **Trend changes** (sudden shifts in performance)

---

## Root Causes the System Can Detect

### 1. Policy Changes
**Examples:**
- Batching threshold changes
- ETA buffer adjustments
- Minimum order value changes
- Delivery fee changes
- Promotional policy changes

**How it detects:** Diff-in-diff analysis, policy change flags

---

### 2. Supply-Side Issues
**Examples:**
- Dasher availability drops
- Dasher wait times increase
- Assignment algorithm changes
- Dasher routing issues
- Peak hour capacity constraints

**How it detects:** SHAP analysis on assignment features, temporal correlation

---

### 3. Merchant-Side Issues
**Examples:**
- Prep-time drift (merchants taking longer)
- Merchant capacity issues
- Store closure/opening
- Menu changes
- Inventory management changes

**How it detects:** Prep-time analysis, merchant-level slicing, SHAP on merchant features

---

### 4. Inventory Issues
**Examples:**
- Stock-out rate increases
- Substitution rate spikes
- Missing items increase
- SKU availability drops
- Inventory model regression

**How it detects:** Inventory event analysis, item-level metrics, SHAP on inventory features

---

### 5. Model Regressions
**Examples:**
- ETA model bias increases
- Assignment model degradation
- Pricing model issues
- Search ranking problems
- Recommendation model drift

**How it detects:** Model prediction vs actual analysis, feature drift detection, SHAP attribution

---

### 6. External Factors
**Examples:**
- Weather events
- Traffic conditions
- Holiday effects
- Regional events
- Market changes

**How it detects:** Temporal correlation, external data integration, cohort analysis

---

### 7. Operational Issues
**Examples:**
- System outages
- API latency increases
- Database performance issues
- Integration failures
- Deployment issues

**How it detects:** Error rate analysis, latency metrics, system health correlation

---

## Real-World Scenarios

### Scenario 1: Batching Threshold Change
**What happened:** Policy team increased batching threshold from 2 to 4
**Detection:** System detects on-time rate drop, cancellation increase
**Root Cause:** RCA identifies batching threshold change (92% confidence)
**Fix:** Reduce batching threshold recommendation

---

### Scenario 2: Dasher Shortage
**What happened:** Peak hour dasher availability drops 30%
**Detection:** System detects on-time rate drop, assignment time increase
**Root Cause:** RCA identifies supply-side issue (85% confidence)
**Fix:** Increase dasher incentives, adjust assignment algorithm

---

### Scenario 3: Merchant Prep-Time Drift
**What happened:** Popular restaurant chain starts taking 20% longer to prepare orders
**Detection:** System detects ETA misses, on-time rate drop for specific merchants
**Root Cause:** RCA identifies merchant prep-time drift (88% confidence)
**Fix:** Adjust ETA model for affected merchants, add buffer time

---

### Scenario 4: Inventory Model Regression
**What happened:** Inventory model starts showing items as in-stock when they're not
**Detection:** System detects substitution rate spike, refund rate increase
**Root Cause:** RCA identifies inventory model issue (90% confidence)
**Fix:** Retrain inventory model, add confidence thresholds

---

### Scenario 5: ETA Model Bias
**What happened:** ETA model becomes overly optimistic
**Detection:** System detects consistent ETA misses, customer complaints
**Root Cause:** RCA identifies ETA model bias (87% confidence)
**Fix:** Retrain ETA model, add buffer time, adjust predictions

---

### Scenario 6: Regional Weather Event
**What happened:** Heavy rain in SF causes delivery delays
**Detection:** System detects on-time rate drop specifically in SF
**Root Cause:** RCA identifies external factor (weather correlation)
**Fix:** Adjust ETAs for weather, communicate delays to customers

---

### Scenario 7: System Outage
**What happened:** Payment API has intermittent failures
**Detection:** System detects cancellation rate spike, support rate increase
**Root Cause:** RCA identifies operational issue (payment failures)
**Fix:** Fix payment API, add retry logic, communicate to customers

---

## How the System Works (General Process)

### Step 1: Continuous Monitoring
- System monitors ALL CX metrics continuously
- Compares current period vs baseline period
- Runs anomaly detection algorithms

### Step 2: Incident Detection
- When ANY metric regresses significantly, creates incident
- Identifies affected cohorts (region, category, time, etc.)
- Calculates severity based on impact

### Step 3: Root Cause Analysis
- Tests multiple hypotheses (not just batching!)
- Uses SHAP, diff-in-diff, correlation analysis
- Ranks causes by confidence and impact

### Step 4: Recommendations
- Generates actionable fixes for ANY root cause
- Quantifies tradeoffs (CX vs efficiency)
- Provides experiment plans

---

## Key Points

### ✅ What the System IS:
- **General-purpose CX monitoring** - Monitors all CX metrics
- **Multi-cause detection** - Can detect ANY root cause
- **Automated** - Runs continuously, no manual setup per cause
- **Evidence-backed** - Uses statistical methods, not guesswork
- **Actionable** - Provides recommendations for any issue

### ❌ What the System is NOT:
- **NOT limited to batching** - Just one example scenario
- **NOT limited to policy changes** - Detects many cause types
- **NOT manual** - Fully automated detection and analysis
- **NOT reactive** - Proactive detection before customers complain

---

## Why Batching Example?

The batching threshold example is used because:
1. **Common scenario** - Policy changes happen frequently
2. **Clear cause-effect** - Easy to understand and explain
3. **Quantifiable** - Clear tradeoffs (CX vs efficiency)
4. **Realistic** - Happens in real operations

But the system works for **ANY** CX degradation, regardless of cause.

---

## Example: Different Root Causes Detected

| Root Cause Type | Example | Detection Method | Confidence |
|----------------|---------|------------------|------------|
| **Policy Change** | Batching threshold increase | Diff-in-diff | 92% |
| **Supply-Side** | Dasher availability drop | SHAP + correlation | 85% |
| **Merchant** | Prep-time drift | Temporal analysis | 88% |
| **Inventory** | Stock-out rate increase | Event analysis | 90% |
| **Model** | ETA bias increase | Prediction vs actual | 87% |
| **External** | Weather event | Correlation | 75% |
| **Operational** | API outage | Error analysis | 95% |

---

## Bottom Line

**CX-Fulfillment Agent is a general-purpose system** that:
- Monitors **all** CX metrics
- Detects **any** type of degradation
- Identifies **any** root cause
- Provides recommendations for **any** issue

The batching threshold example is just **one scenario** - the system works for **everything** that affects customer experience.


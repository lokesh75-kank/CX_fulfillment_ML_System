# Demo Scenario Script

## Overview

This document outlines the exact demo scenario that will be scripted and executed to demonstrate the CX-Fulfillment Agent's capabilities. The scenario simulates a real-world incident: a policy change that causes CX degradation.

## Scenario Setup

### Timeline

- **Jan 1-2**: Baseline period (normal operations)
- **Jan 3**: Policy change implemented (batching threshold increased)
- **Jan 4**: Regression begins (detected by tool)
- **Jan 4-5**: Full regression period
- **Jan 4 morning**: Tool detects incident
- **Jan 4 afternoon**: RCA completed, recommendations generated

### Policy Change Details

**Change**: Batching threshold increased from 2 orders to 4 orders for grocery stores during peak hours (6-8pm)

**Expected Impact**:
- More orders batched together
- Longer dasher wait times
- Higher lateness rate
- More cancellations (due to cold food / long waits)
- Prep-time drift (correlated, not causal)

**Affected Cohort**: 
- Category: Grocery
- Region: SF
- Time-of-day: Dinner (6-8pm)
- Basket size: All sizes

## Step-by-Step Demo Flow

### Step 1: Baseline View (Jan 1-2)

**Action**: Open Dashboard, show baseline metrics

**What to Show**:
- CX Score: ~85-90 (healthy)
- On-time rate: ~92%
- Cancellation rate: ~3%
- No active incidents

**Narrative**:
> "Here's our baseline. CX Score is healthy at 85-90, on-time rate is strong at 92%. No incidents detected. This is normal operations."

---

### Step 2: Policy Change (Jan 3)

**Action**: Show data generation with policy change flag

**What to Show**:
- Highlight that policy change occurred on Jan 3
- Show batching rate increased (from ~30% to ~60% for affected cohort)
- Metrics still look okay (lag effect)

**Narrative**:
> "On Jan 3, we increased the batching threshold for grocery stores during peak hours. This was intended to improve efficiency. Notice the batching rate increased from 30% to 60%."

---

### Step 3: Regression Begins (Jan 4)

**Action**: Show Jan 4 morning data

**What to Show**:
- CX Score drops to ~72 (from ~88)
- On-time rate drops to ~78% (from ~92%)
- Cancellation rate increases to ~8% (from ~3%)
- Incident detected automatically

**Narrative**:
> "The next morning, Jan 4, we see a significant drop. CX Score fell from 88 to 72. On-time rate dropped from 92% to 78%. Cancellation rate doubled. The tool automatically detected this as an incident."

---

### Step 4: Incident Detection

**Action**: Show Incident Detail page

**What to Show**:
- Incident card with:
  - Severity: High
  - Detected: Jan 4, 8:00 AM
  - Metric: CX Score
  - Drop: -16 points
- Top regressing slices:
  1. Grocery + SF + Dinner (6-8pm) - **-18 points**
  2. Grocery + SF + All times - **-12 points**
  3. All categories + SF + Dinner - **-8 points**

**Narrative**:
> "The tool identified the top regressing slice: Grocery stores in SF during dinner hours. This slice dropped 18 points. The incident was detected within hours of the regression starting."

---

### Step 5: Root Cause Analysis

**Action**: Show RCA Report page

**What to Show**:
- Ranked root causes:

  1. **Batching Threshold Increase** (Confidence: 0.92, Impact: High)
     - Evidence:
       - Batching rate increased 2x in affected slice
       - SHAP attribution: `batched_flag` is top feature for lateness
       - Diff-in-diff: Significant increase in lateness after Jan 3
       - Correlation: `dasher_wait` increased 3x for batched orders

  2. **Merchant Prep-Time Drift** (Confidence: 0.75, Impact: Medium)
     - Evidence:
       - Prep time increased 15% in affected stores
       - SHAP attribution: `merchant_prep_time` is second feature
       - Temporal correlation with batching (stores under pressure)

  3. **Inventory Mismatch** (Confidence: 0.35, Impact: Low)
     - Evidence:
       - Minor decrease in `in_stock_prob`
       - Small increase in substitutions
       - Not significant enough to explain drop

**Narrative**:
> "The RCA agent tested multiple hypotheses. The top cause is clearly the batching threshold increase, with 92% confidence. The evidence is strong: batching rate doubled, SHAP shows it's the top driver of lateness, and we see a clear before/after difference. Prep-time drift is secondary - stores are under pressure from batching, causing prep times to increase. Inventory is not a significant factor."

---

### Step 6: Recommendations

**Action**: Show Recommendations page

**What to Show**:
- Ranked recommendations:

  1. **Reduce Batching Threshold for Fragile SKUs During Peak Hours**
     - Expected Impact:
       - CX Score: +12 points
       - On-time rate: +8 percentage points
       - Cancellation rate: -4 percentage points
       - Tradeoff: Dasher efficiency -5% (fewer orders per trip)
     - Confidence: 0.88
     - Implementation: Policy change, 1 day rollout

  2. **Increase ETA Buffer for Stores with Prep-Time Drift**
     - Expected Impact:
       - CX Score: +4 points
       - On-time rate: +3 percentage points
       - Tradeoff: Customer wait time +2 minutes average
     - Confidence: 0.72
     - Implementation: Model update, 2 days rollout

  3. **Suppress Low-Confidence SKUs from Search**
     - Expected Impact:
       - Refund rate: -1 percentage point
       - Substitution rate: -2 percentage points
       - Tradeoff: Selection coverage -3%
     - Confidence: 0.65
     - Implementation: Search filter, 1 day rollout

**Narrative**:
> "Based on the root causes, the tool recommends three actions. The top recommendation is to reduce batching for fragile SKUs during peak hours. This would recover 12 points of CX Score and improve on-time rate by 8 points, but at a cost of 5% dasher efficiency. The second recommendation addresses prep-time drift by increasing ETA buffers. The third is a smaller optimization for inventory issues."

---

### Step 7: Experiment Plan

**Action**: Click "Generate Experiment Plan", show markdown export

**What to Show**:
- Complete experiment plan with:
  - Hypothesis
  - Primary/secondary metrics
  - Guardrails
  - Unit of randomization
  - Duration and sample size
  - Rollout plan
  - Monitoring checklist

**Narrative**:
> "The tool auto-generates a complete experiment plan. This includes the hypothesis, success metrics, guardrails to watch, how we'll randomize, how long to run it, and a monitoring checklist. This is ready to share with stakeholders and engineering teams."

---

### Step 8: What-If Simulation

**Action**: Show tradeoff visualization

**What to Show**:
- Interactive chart showing:
  - X-axis: CX Score improvement
  - Y-axis: Efficiency impact
  - Points for each recommendation
  - Confidence intervals

**Narrative**:
> "The what-if simulator shows the tradeoffs visually. Recommendation 1 gives the biggest CX improvement but also the biggest efficiency hit. This helps us make informed decisions about which actions to prioritize."

---

## Demo Script (2-Minute Version)

### Opening (10 seconds)
> "I'm going to show you the CX-Fulfillment Agent, a tool that detects CX degradation early and helps us fix it quickly."

### Baseline (15 seconds)
> "Here's our baseline - CX Score at 88, everything healthy. On Jan 3, we increased batching thresholds to improve efficiency."

### Detection (20 seconds)
> "The next morning, Jan 4, CX Score dropped to 72. The tool automatically detected this as an incident and identified the top regressing slice: Grocery in SF during dinner hours."

### RCA (30 seconds)
> "The RCA agent tested hypotheses and found the root cause: batching threshold increase with 92% confidence. Prep-time drift is secondary. The evidence is clear from SHAP analysis and diff-in-diff."

### Recommendations (30 seconds)
> "The tool recommends reducing batching for fragile SKUs, which would recover 12 points of CX Score but cost 5% efficiency. It also suggests increasing ETA buffers for prep-time drift."

### Experiment Plan (15 seconds)
> "Finally, it auto-generates a complete experiment plan with metrics, guardrails, and rollout strategy - ready to share with stakeholders."

---

## Technical Implementation

### Data Generation Script

```python
# scripts/demo_scenario.py

def generate_demo_scenario():
    # Jan 1-2: Baseline
    baseline_data = generate_normal_operations(
        start_date="2024-01-01",
        end_date="2024-01-02",
        cx_score_target=88
    )
    
    # Jan 3: Policy change
    policy_change_data = generate_with_policy_change(
        date="2024-01-03",
        change_type="batching_threshold",
        threshold_old=2,
        threshold_new=4,
        affected_cohort={
            "category": "grocery",
            "region": "SF",
            "time_of_day": "dinner"
        }
    )
    
    # Jan 4-5: Regression
    regression_data = generate_regression(
        start_date="2024-01-04",
        end_date="2024-01-05",
        cx_score_target=72,
        affected_cohort={
            "category": "grocery",
            "region": "SF",
            "time_of_day": "dinner"
        },
        root_causes=["batching", "prep_time_drift"]
    )
    
    return combine_data([baseline_data, policy_change_data, regression_data])
```

### Validation Checks

Before demo, verify:
- [ ] Incident is detected on Jan 4
- [ ] Top slice is "Grocery + SF + Dinner"
- [ ] RCA identifies batching as top cause (confidence > 0.9)
- [ ] Recommendations include batching reduction
- [ ] Experiment plan is complete and professional

---

## Key Talking Points

### Why This Matters
- **Early Detection**: Caught regression within hours, not days
- **Accurate RCA**: Identified exact cause with high confidence
- **Actionable**: Recommendations with quantified tradeoffs
- **Operational**: Experiment plan ready to execute

### What Makes It Credible
- **System-level thinking**: Not just a model, but a workflow
- **CX-first**: Customer experience is the primary metric
- **Causal reasoning**: Uses SHAP, diff-in-diff, not just correlation
- **Tradeoffs**: Acknowledges efficiency vs CX tension
- **Real-world**: Matches how high-performing ML orgs operate

### DoorDash-Specific Context
- **Marketplace dynamics**: Efficiency vs customer trust
- **Multi-sided platform**: Dashers, merchants, customers all matter
- **Operational reality**: Oncall engineers need tools like this
- **Experiment culture**: A/B testing is core to decision-making

---

## Demo Preparation Checklist

### Before Demo
- [ ] Generate demo dataset
- [ ] Verify incident detection works
- [ ] Verify RCA identifies correct causes
- [ ] Verify recommendations are generated
- [ ] Verify experiment plan is complete
- [ ] Test all UI pages load correctly
- [ ] Prepare 2-minute narrative

### During Demo
- [ ] Start with baseline (show healthy state)
- [ ] Show policy change (explain intent)
- [ ] Show regression (emphasize automatic detection)
- [ ] Show RCA (emphasize confidence and evidence)
- [ ] Show recommendations (emphasize tradeoffs)
- [ ] Show experiment plan (emphasize completeness)

### After Demo
- [ ] Answer questions about methodology
- [ ] Explain scalability considerations
- [ ] Discuss future enhancements

---

## Success Metrics for Demo

### Technical
- ✅ Incident detected within 24 hours of regression
- ✅ Top slice correctly identified
- ✅ Root cause identified with >90% confidence
- ✅ Recommendations have quantified impact
- ✅ Experiment plan is complete

### Presentation
- ✅ Clear narrative flow
- ✅ Emphasizes CX-first approach
- ✅ Shows tradeoffs clearly
- ✅ Demonstrates operational value
- ✅ Feels realistic and credible


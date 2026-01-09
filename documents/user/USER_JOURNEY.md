# User Journey: ML Engineer Experience

## Overview

This document walks through the complete user journey for the primary persona (ML Engineer) using the CX-Fulfillment Agent. It follows a realistic scenario from incident detection through resolution.

---

## Scenario: Policy Change Causes CX Regression

**Context**: A batching threshold policy change was deployed on Jan 3. By Jan 4 morning, CX metrics have degraded significantly.

**User**: ML Engineer (Fulfillment team)
**Goal**: Detect, diagnose, and fix the CX regression quickly

---

## Journey Map

### Phase 1: Discovery (Morning Routine)

#### Step 1: Morning Check-in
**Time**: 8:00 AM, Jan 4
**Action**: User opens the CX-Fulfillment Agent dashboard

**What User Sees**:
```
┌─────────────────────────────────────────────────────────┐
│  CX-Fulfillment Agent Dashboard                          │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  CX Score Trend (Last 7 Days)                           │
│  ┌──────────────────────────────────────────────┐      │
│  │  90 ┤                                        │      │
│  │  85 ┤                                        │      │
│  │  80 ┤                                        │      │
│  │  75 ┤                    ⚠️                  │      │
│  │  70 ┤              ──────┘                  │      │
│  │     └───────────────────────────────────────│      │
│  │     Jan 1  Jan 2  Jan 3  Jan 4              │      │
│  └──────────────────────────────────────────────┘      │
│                                                          │
│  Active Incidents (2)                                    │
│  ┌──────────────────────────────────────────────┐      │
│  │ 🔴 HIGH  | Grocery SF - CX Score -18         │      │
│  │    Detected: 2 hours ago                     │      │
│  │    Status: New                               │      │
│  ├──────────────────────────────────────────────┤      │
│  │ 🟡 MED   | Convenience NYC - On-time -5%     │      │
│  │    Detected: 1 hour ago                      │      │
│  │    Status: Investigating                     │      │
│  └──────────────────────────────────────────────┘      │
│                                                          │
│  Quick Stats                                             │
│  • Overall CX Score: 72 (↓ 16 from baseline)           │
│  • On-time Rate: 78% (↓ 14%)                           │
│  • Cancellation Rate: 8% (↑ 5%)                        │
└─────────────────────────────────────────────────────────┘
```

**User's Reaction**:
> "Oh no, we have a high-severity incident. CX Score dropped 18 points in Grocery SF. This is significant. Let me investigate."

**User Action**: Clicks on the high-severity incident

---

### Phase 2: Investigation (Incident Detail)

#### Step 2: Incident Detail View
**Time**: 8:05 AM
**Action**: User reviews incident details

**What User Sees**:
```
┌─────────────────────────────────────────────────────────┐
│  Incident: Grocery SF - CX Score Regression             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Incident Details                                        │
│  • Detected: Jan 4, 2024 6:00 AM                       │
│  • Severity: HIGH                                        │
│  • Metric: CX Score                                      │
│  • Drop: -18 points (from 88 to 70)                     │
│  • Time Window: Jan 4, 6:00 AM - 8:00 AM                │
│                                                          │
│  Metric Breakdown                                        │
│  ┌──────────────────────────────────────────────┐      │
│  │ Metric          | Before | After | Change     │      │
│  ├──────────────────────────────────────────────┤      │
│  │ On-time Rate    | 92%    | 78%   | -14% ⚠️   │      │
│  │ Cancellation    | 3%     | 8%    | +5% ⚠️    │      │
│  │ Refund Rate     | 2%     | 4%    | +2%       │      │
│  │ Item Accuracy   | 96%    | 94%   | -2%       │      │
│  │ Support Rate    | 1%     | 3%    | +2%       │      │
│  └──────────────────────────────────────────────┘      │
│                                                          │
│  Top Regressing Slices                                   │
│  ┌──────────────────────────────────────────────┐      │
│  │ Rank | Slice                    | Drop | Sig │      │
│  ├──────────────────────────────────────────────┤      │
│  │  1   | Grocery + SF + Dinner     | -18  | ***│      │
│  │      | (6-8pm)                   |      |    │      │
│  ├──────────────────────────────────────────────┤      │
│  │  2   | Grocery + SF + All times  | -12  | ** │      │
│  ├──────────────────────────────────────────────┤      │
│  │  3   | All + SF + Dinner         | -8   | *  │      │
│  └──────────────────────────────────────────────┘      │
│                                                          │
│  [View RCA Report]  [View Recommendations]             │
└─────────────────────────────────────────────────────────┘
```

**User's Analysis**:
> "The top slice is Grocery SF during dinner hours (6-8pm). That's a very specific cohort. On-time rate dropped 14%, cancellations doubled. This looks like a delivery timing issue. Let me see what the RCA says."

**User Action**: Clicks "View RCA Report"

---

### Phase 3: Root Cause Analysis

#### Step 3: RCA Report
**Time**: 8:10 AM
**Action**: User reviews automated root cause analysis

**What User Sees**:
```
┌─────────────────────────────────────────────────────────┐
│  Root Cause Analysis Report                              │
│  Incident: Grocery SF - CX Score Regression             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Ranked Root Causes                                      │
│                                                          │
│  ┌──────────────────────────────────────────────┐      │
│  │ 1. Batching Threshold Increase                │      │
│  │    Confidence: 92% | Impact: HIGH             │      │
│  ├──────────────────────────────────────────────┤      │
│  │ Evidence:                                      │      │
│  │ • Batching rate increased 2x (30% → 60%)      │      │
│  │ • SHAP attribution: batched_flag is top       │      │
│  │   driver of lateness (0.42 importance)        │      │
│  │ • Diff-in-diff: Significant increase after     │      │
│  │   Jan 3 policy change (p < 0.001)             │      │
│  │ • Correlation: dasher_wait increased 3x for    │      │
│  │   batched orders (300s → 900s)                │      │
│  │                                                │      │
│  │ Timeline:                                      │      │
│  │ • Policy change: Jan 3, 12:00 AM              │      │
│  │ • Regression start: Jan 4, 6:00 PM           │      │
│  │ • Lag: ~30 hours (expected for peak hours)    │      │
│  └──────────────────────────────────────────────┘      │
│                                                          │
│  ┌──────────────────────────────────────────────┐      │
│  │ 2. Merchant Prep-Time Drift                   │      │
│  │    Confidence: 75% | Impact: MEDIUM           │      │
│  ├──────────────────────────────────────────────┤      │
│  │ Evidence:                                      │      │
│  │ • Prep time increased 15% in affected stores  │      │
│  │ • SHAP attribution: merchant_prep_time is    │      │
│  │   2nd driver (0.28 importance)                │      │
│  │ • Temporal correlation with batching (stores  │      │
│  │   under pressure from increased batching)     │      │
│  │ • Not sufficient to explain full drop alone  │      │
│  └──────────────────────────────────────────────┘      │
│                                                          │
│  ┌──────────────────────────────────────────────┐      │
│  │ 3. Inventory Mismatch                         │      │
│  │    Confidence: 35% | Impact: LOW             │      │
│  ├──────────────────────────────────────────────┤      │
│  │ Evidence:                                      │      │
│  │ • Minor decrease in in_stock_prob (0.85→0.80) │      │
│  │ • Small increase in substitutions (+1%)       │      │
│  │ • Not significant enough to explain drop      │      │
│  └──────────────────────────────────────────────┘      │
│                                                          │
│  Summary                                                │
│  "Most of the CX drop comes from batching threshold     │
│  increase. Prep-time drift is secondary and likely      │
│  correlated with batching pressure."                    │
│                                                          │
│  [View Recommendations]  [Export Report]               │
└─────────────────────────────────────────────────────────┘
```

**User's Analysis**:
> "Perfect! The RCA is very clear. Batching threshold increase is the primary cause with 92% confidence. The evidence is strong - SHAP shows it's the top driver, diff-in-diff confirms the policy change impact, and dasher wait times tripled. Prep-time drift is secondary, probably because stores are struggling with the increased batching. This makes sense - we increased batching from 2 to 4 orders, and during peak dinner hours, that's causing significant delays."

**User Action**: Clicks "View Recommendations"

---

### Phase 4: Recommendations & Decision

#### Step 4: Recommendations
**Time**: 8:15 AM
**Action**: User reviews actionable recommendations

**What User Sees**:
```
┌─────────────────────────────────────────────────────────┐
│  Recommendations                                        │
│  Incident: Grocery SF - CX Score Regression             │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Ranked Recommendations                                 │
│                                                          │
│  ┌──────────────────────────────────────────────┐      │
│  │ 1. Reduce Batching Threshold for Fragile     │      │
│  │    SKUs During Peak Hours                    │      │
│  │    Confidence: 88%                           │      │
│  ├──────────────────────────────────────────────┤      │
│  │ Expected Impact:                              │      │
│  │ • CX Score: +12 points (70 → 82)             │      │
│  │ • On-time Rate: +8% (78% → 86%)             │      │
│  │ • Cancellation Rate: -4% (8% → 4%)          │      │
│  │                                                │      │
│  │ Tradeoff:                                     │      │
│  │ • Dasher Efficiency: -5% (fewer orders/trip)│      │
│  │                                                │      │
│  │ Implementation:                               │      │
│  │ • Policy change: Reduce threshold from 4→2  │      │
│  │ • Scope: Grocery stores, SF region, 6-8pm   │      │
│  │ • Complexity: Low (1 day rollout)           │      │
│  │                                                │      │
│  │ [Generate Experiment Plan]                    │      │
│  └──────────────────────────────────────────────┘      │
│                                                          │
│  ┌──────────────────────────────────────────────┐      │
│  │ 2. Increase ETA Buffer for Stores with       │      │
│  │    Prep-Time Drift                           │      │
│  │    Confidence: 72%                           │      │
│  ├──────────────────────────────────────────────┤      │
│  │ Expected Impact:                              │      │
│  │ • CX Score: +4 points (70 → 74)             │      │
│  │ • On-time Rate: +3% (78% → 81%)             │      │
│  │                                                │      │
│  │ Tradeoff:                                     │      │
│  │ • Customer Wait Time: +2 minutes average     │      │
│  │                                                │      │
│  │ Implementation:                               │      │
│  │ • Model update: Add buffer to promised_eta  │      │
│  │ • Scope: Stores with prep-time drift         │      │
│  │ • Complexity: Medium (2 days rollout)        │      │
│  └──────────────────────────────────────────────┘      │
│                                                          │
│  Tradeoff Visualization                                 │
│  ┌──────────────────────────────────────────────┐      │
│  │        Efficiency Impact                      │      │
│  │            ↑                                  │      │
│  │            │                                  │      │
│  │            │  Rec 2                           │      │
│  │            │                                  │      │
│  │            │         Rec 1                    │      │
│  │            │                                  │      │
│  │            └──────────────────→               │      │
│  │                    CX Improvement             │      │
│  └──────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────┘
```

**User's Decision Process**:
> "Recommendation 1 is clear - reduce batching threshold. It has the biggest impact (+12 CX points) and addresses the root cause directly. The efficiency tradeoff (-5%) is acceptable given the severity. Recommendation 2 is secondary - it helps with prep-time drift but won't solve the main issue. I'll go with Rec 1 and generate an experiment plan."

**User Action**: Clicks "Generate Experiment Plan" on Recommendation 1

---

### Phase 5: Experiment Planning

#### Step 5: Experiment Plan Generation
**Time**: 8:20 AM
**Action**: User generates and reviews experiment plan

**What User Sees**:
```
┌─────────────────────────────────────────────────────────┐
│  Experiment Plan: Reduce Batching for Fragile SKUs    │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Hypothesis                                              │
│  Reducing batching threshold from 4 to 2 for fragile    │
│  SKUs during peak hours (6-8pm) in Grocery SF will      │
│  improve CX Score by recovering on-time rate and        │
│  reducing cancellations, with acceptable efficiency     │
│  tradeoff.                                              │
│                                                          │
│  Primary Metrics                                         │
│  • CX Score (target: +12 points)                        │
│  • On-time Rate (target: +8%)                           │
│  • Cancellation Rate (target: -4%)                      │
│                                                          │
│  Secondary Metrics                                       │
│  • Refund Rate                                          │
│  • Support Contact Rate                                 │
│  • Item Accuracy                                        │
│                                                          │
│  Guardrails                                              │
│  • Dasher Efficiency: Alert if drops > 10%              │
│  • Order Volume: Alert if drops > 5%                   │
│  • Other Regions: Monitor for spillover effects         │
│                                                          │
│  Unit of Randomization                                  │
│  Store-level (randomize 50% of Grocery stores in SF)    │
│                                                          │
│  Duration & Sample Size                                 │
│  • Minimum: 7 days                                      │
│  • Recommended: 14 days                                 │
│  • Expected sample: ~5,000 orders (treatment)           │
│  • Power: 80% to detect 5% lift in on-time rate        │
│                                                          │
│  Rollout Plan                                           │
│  Phase 1: 10% stores (Day 1-3)                         │
│  Phase 2: 50% stores (Day 4-7)                         │
│  Phase 3: 100% stores (Day 8-14)                       │
│                                                          │
│  Monitoring Checklist                                   │
│  ☐ Daily CX Score check (target: +12 points)           │
│  ☐ Daily on-time rate check (target: +8%)               │
│  ☐ Daily cancellation rate check (target: -4%)          │
│  ☐ Daily dasher efficiency check (guardrail: <10% drop) │
│  ☐ Hourly alerts if metrics regress                    │
│  ☐ Rollback plan: Revert if guardrails breached        │
│                                                          │
│  [Export as Markdown]  [Share with Team]               │
└─────────────────────────────────────────────────────────┘
```

**User's Review**:
> "This experiment plan looks solid. It has all the key elements: clear hypothesis, primary/secondary metrics, guardrails, randomization strategy, and monitoring. The 14-day duration with phased rollout is reasonable. I'll export this and share it with the team."

**User Action**: Clicks "Export as Markdown", saves file, shares with team

---

### Phase 6: Execution & Monitoring

#### Step 6: Daily Monitoring (Over Next 2 Weeks)
**Time**: Daily, 8:00 AM
**Action**: User checks experiment progress

**What User Sees** (Day 3 of experiment):
```
┌─────────────────────────────────────────────────────────┐
│  Experiment: Reduce Batching for Fragile SKUs          │
│  Status: Phase 1 (10% rollout) - Day 3                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Progress vs Targets                                    │
│  ┌──────────────────────────────────────────────┐      │
│  │ Metric          | Target | Current | Status  │      │
│  ├──────────────────────────────────────────────┤      │
│  │ CX Score        | +12    | +8      | 🟡 On   │      │
│  │ On-time Rate    | +8%    | +6%     | 🟡 On   │      │
│  │ Cancellation    | -4%    | -3%     | 🟢 Good │      │
│  │ Dasher Eff.     | <10%   | -4%     | 🟢 Good │      │
│  └──────────────────────────────────────────────┘      │
│                                                          │
│  "Early results are positive. CX Score improving,       │
│  guardrails not breached. Proceeding to Phase 2."      │
│                                                          │
│  [View Full Report]  [Adjust Plan]                     │
└─────────────────────────────────────────────────────────┘
```

**User's Assessment**:
> "Good progress. We're seeing about 67% of the target impact already, which is promising. Guardrails are fine. Let's proceed to Phase 2."

---

### Phase 7: Resolution

#### Step 7: Experiment Complete
**Time**: 2 weeks later
**Action**: User reviews final results

**What User Sees**:
```
┌─────────────────────────────────────────────────────────┐
│  Experiment Results: Reduce Batching for Fragile SKUs  │
│  Status: Complete - All Phases Rolled Out              │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Final Results                                          │
│  ┌──────────────────────────────────────────────┐      │
│  │ Metric          | Target | Actual | Status   │      │
│  ├──────────────────────────────────────────────┤      │
│  │ CX Score        | +12    | +14    | ✅ Exceed│      │
│  │ On-time Rate    | +8%    | +9%    | ✅ Exceed│      │
│  │ Cancellation    | -4%    | -5%    | ✅ Exceed│      │
│  │ Dasher Eff.     | <10%   | -6%    | ✅ Within│      │
│  └──────────────────────────────────────────────┘      │
│                                                          │
│  Impact Summary                                         │
│  • CX Score recovered from 70 to 84 (+14 points)       │
│  • On-time rate improved from 78% to 87%                │
│  • Cancellation rate reduced from 8% to 3%              │
│  • Efficiency tradeoff acceptable (-6%)                  │
│                                                          │
│  Recommendation: Make permanent                         │
│                                                          │
│  [Mark as Resolved]  [Create Follow-up]                │
└─────────────────────────────────────────────────────────┘
```

**User's Conclusion**:
> "Excellent! The experiment exceeded targets. CX Score recovered 14 points (even better than the 12 point target), and all metrics improved. The efficiency tradeoff is acceptable. I'll mark this incident as resolved and make the change permanent."

**User Action**: Clicks "Mark as Resolved", updates policy permanently

---

## Journey Summary

### Timeline
- **8:00 AM**: Incident detected automatically
- **8:05 AM**: User investigates incident details
- **8:10 AM**: Reviews RCA report (identifies root cause)
- **8:15 AM**: Reviews recommendations (selects best action)
- **8:20 AM**: Generates experiment plan
- **8:25 AM**: Shares plan with team, starts experiment
- **Daily**: Monitors experiment progress
- **2 weeks later**: Experiment complete, incident resolved

### Key Outcomes

1. **Speed**: From detection to action in < 30 minutes
2. **Accuracy**: Root cause identified with 92% confidence
3. **Actionability**: Clear recommendation with quantified tradeoffs
4. **Execution**: Complete experiment plan ready to run
5. **Resolution**: CX Score recovered, incident resolved

### User Value Delivered

- **Faster debugging**: Automated detection and RCA
- **Safer decisions**: Quantified tradeoffs before shipping
- **Clear justification**: Evidence-backed recommendations
- **Operational efficiency**: Experiment plans ready to execute

---

## Alternative Journey: False Positive

### Scenario: Minor Fluctuation (Not a Real Incident)

**Time**: 8:00 AM
**Action**: User sees low-severity incident

**What User Sees**:
```
┌─────────────────────────────────────────────────────────┐
│  Active Incidents (1)                                    │
│  ┌──────────────────────────────────────────────┐      │
│  │ 🟢 LOW   | Retail LA - CX Score -3          │      │
│  │    Detected: 1 hour ago                       │      │
│  │    Status: New                                │      │
│  └──────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────┘
```

**User Action**: Clicks to investigate

**RCA Report Shows**:
- Confidence: 45% (low)
- Evidence: Weak correlation, within normal variance
- Recommendation: "Monitor, no action needed"

**User Decision**: 
> "This is just normal variance. The RCA confidence is low and evidence is weak. I'll mark this as 'monitoring' and move on."

**Outcome**: User doesn't waste time on false positives

---

## Key User Journey Principles

### 1. Speed
- Detection happens automatically
- RCA is instant (no manual SQL queries)
- Recommendations are ready immediately

### 2. Clarity
- Clear visualizations at each step
- Evidence-backed conclusions
- Quantified tradeoffs

### 3. Actionability
- Recommendations are specific and implementable
- Experiment plans are complete
- No ambiguity about next steps

### 4. Trust
- High confidence scores when evidence is strong
- Low confidence scores when evidence is weak
- Transparent about limitations

### 5. Efficiency
- User goes from problem to solution in < 30 minutes
- No manual data gathering
- No back-and-forth with other teams

---

## User Journey Metrics

### Time Savings
- **Before**: 2-3 days (detection → investigation → RCA → decision)
- **After**: < 30 minutes (automated detection → instant RCA → ready-to-execute plan)

### Accuracy
- **Before**: Manual analysis, prone to bias
- **After**: Systematic hypothesis testing, confidence scores

### Actionability
- **Before**: Recommendations are vague ("reduce batching")
- **After**: Specific actions with quantified impact ("reduce batching threshold from 4→2, expect +12 CX points, -5% efficiency")

---

## Conclusion

The user journey demonstrates how the CX-Fulfillment Agent transforms the ML Engineer's workflow from reactive debugging to proactive optimization. The tool enables:

1. **Early detection** (before customers complain)
2. **Fast diagnosis** (automated RCA)
3. **Informed decisions** (quantified tradeoffs)
4. **Rapid execution** (ready-to-run experiments)

This is exactly how a high-performing ML organization operates day-to-day.


# Persona Plan — CX Fulfillment Agent

## Overview

This document defines the target users (personas) for the CX-Fulfillment Agent, their needs, and how the system will serve them. The persona strategy prioritizes depth over breadth, focusing on the primary user while providing appropriate access for secondary users.

---

## Primary Persona (Full Build)

### 🧠 Machine Learning Engineer (Fulfillment / Inventory / Search AI)

#### Why This Persona

- **Closest to ML, optimization, and policy decisions**
- **Owns debugging, rollback, retraining, and experimentation**
- **Primary consumer of root-cause and causal signals**
- **Most impacted by CX regressions**

This persona is the primary user because they are directly responsible for:
- Model performance and policy decisions
- Debugging CX issues when they arise
- Making tradeoff decisions between efficiency and customer experience
- Designing and running experiments to fix issues

#### Core Problems

1. **CX regressions discovered too late**
   - By the time issues are noticed, significant damage is done
   - Need early detection and alerting

2. **Hard to connect customer pain → model / policy change**
   - Difficult to trace customer complaints to specific model or policy changes
   - Need clear attribution and causal links

3. **Slow root-cause analysis (SQL + Slack loops)**
   - Current process involves manual SQL queries and team discussions
   - Need automated, systematic root-cause analysis

4. **Fear of shipping fixes without understanding tradeoffs**
   - Hesitation to make changes without clear impact estimates
   - Need quantified tradeoffs (CX vs efficiency)

#### What This Persona Sees (Fully Implemented)

##### 1. Incident Feed
- **CX regressions by cohort** (category, region, time)
- **Severity indicators**
- **Time of detection**
- **Quick status (new, investigating, resolved)**

**UI Location**: Dashboard page

##### 2. Incident Detail View
- **Metric deltas** (lateness, refunds, ratings proxy)
- **Top regressing slices** with statistical significance
- **Temporal trends** (before/after comparison)
- **Drilldown capabilities** (click slice to see details)

**UI Location**: `/incidents/[id]` page

##### 3. Root Cause Analysis
- **Ranked causes** (batching, prep time, inventory, ETA bias)
- **Confidence scores** for each hypothesis
- **Evidence**:
  - Feature shifts (SHAP attribution)
  - Counterfactual checks (diff-in-diff)
  - Temporal correlations
- **Narrative explanation** of why each cause is likely

**UI Location**: `/rca/[id]` page

##### 4. Recommendations
- **Actionable fixes** with:
  - Expected CX impact (quantified)
  - Expected efficiency impact (quantified)
  - Confidence intervals
  - Implementation complexity
- **Tradeoff visualization** (CX improvement vs efficiency cost)
- **Ranked by expected net benefit**

**UI Location**: `/recommendations/[id]` page

##### 5. Experiment Generator
- **Auto-generated experiment plan** with:
  - Hypothesis statement
  - Primary/secondary metrics
  - Guardrails
  - Unit of randomization
  - Duration + sample size
  - Rollout checklist
  - Monitoring plan
- **Markdown export** ready for sharing

**UI Location**: Export button on recommendations page

#### Key Outputs for This Persona

1. **Faster debugging**
   - Incident detected within hours, not days
   - Root cause identified automatically
   - Evidence aggregated and presented clearly

2. **Safer ML changes**
   - Tradeoffs quantified before shipping
   - Guardrails defined upfront
   - Experiment plans ready to execute

3. **Clear CX justification for decisions**
   - Data-driven recommendations
   - Evidence-backed root causes
   - Quantified impact estimates

#### Workflow Example

```
1. Morning: Check incident feed
   → See new incident: "CX Score dropped 16 points in Grocery SF"
   
2. Click incident → View detail
   → Top slice: "Grocery + SF + Dinner (6-8pm)" dropped 18 points
   → Metrics: On-time rate -8%, Cancellation rate +5%
   
3. View RCA report
   → Top cause: Batching threshold increase (92% confidence)
   → Evidence: SHAP shows batched_flag is top driver, diff-in-diff confirms
   
4. View recommendations
   → Top rec: Reduce batching for fragile SKUs
   → Impact: CX Score +12, Efficiency -5%
   → Tradeoff: Acceptable for this severity
   
5. Generate experiment plan
   → Export markdown
   → Share with team
   → Start experiment
```

---

## Secondary Persona (Partial Support)

### 📦 Product Manager (Fulfillment / CX / Inventory)

#### Why Partial

- **Needs insight, not raw ML signals**
- **Consumes summaries derived from MLE outputs**
- **Not responsible for debugging or technical fixes**
- **Needs business context and prioritization**

#### Core Problems

1. **Hard to prioritize CX issues**
   - Which issues matter most?
   - What's the business impact?

2. **Unclear tradeoffs between efficiency and customer trust**
   - When is efficiency cost worth CX improvement?
   - How to communicate tradeoffs to stakeholders?

3. **Over-reliance on lagging signals (ratings, tickets)**
   - By the time ratings drop, damage is done
   - Need leading indicators

#### What This Persona Sees (Read-Only)

##### 1. CX Summary Page
- **"What broke?"**
  - High-level incident summary
  - Affected cohorts
  - Severity indicators
  
- **"Why customers are unhappy?"**
  - Top root causes (simplified)
  - Business impact explanation
  
- **"What we recommend?"**
  - Top 2-3 recommendations
  - Expected outcomes (business language)

**UI Location**: `/summary` page (read-only view)

##### 2. Tradeoff View
- **CX improvement vs efficiency cost**
  - Visual chart showing tradeoffs
  - Business-friendly labels
  - Impact on key metrics (ratings, retention)

**UI Location**: Part of summary page or separate `/tradeoffs` page

##### 3. Impact Projection
- **Expected rating lift**
- **Expected refund reduction**
- **Expected retention improvement**
- **Time to impact**

**UI Location**: Part of summary page

#### Implementation Approach

- **Generated report** (dashboard or markdown)
- **No separate logic or workflows**
- **Derived from MLE outputs**
- **Simplified language, business context**

#### Access Pattern

- **Read-only access** to summary views
- **No access to**:
  - Raw RCA evidence
  - Technical implementation details
  - Experiment plan generation
  - Direct incident management

#### Workflow Example

```
1. Weekly review: Check CX Summary
   → See: "3 active incidents, 1 high severity"
   
2. Click high severity incident
   → Summary: "Grocery SF dinner hours - CX Score -18"
   → Root cause: "Batching policy change"
   → Recommendation: "Reduce batching → CX +12, Efficiency -5%"
   
3. Review tradeoff
   → Decide: Acceptable tradeoff for this severity
   → Approve recommendation
   
4. Track impact
   → Monitor projected rating/retention improvements
```

---

## Tertiary Personas (Conceptual Only)

### 🚚 Operations / Merchant Strategy

#### Needs

- **Identify merchants and cohorts causing CX pain**
- **Apply operational fixes** (SLA enforcement, coaching)
- **Target interventions** where they'll have most impact

#### How They'd Use Outputs

- **Merchant-level CX risk reports**
  - Which stores have highest CX risk?
  - What are the specific issues?
  
- **Targeted interventions**
  - SLA adjustments for high-risk stores
  - Merchant coaching on prep-time management
  - Inventory support for stores with stock issues

#### Status

- **Documented only (no UI)**
- **Future enhancement**: Could add merchant-level dashboards
- **For MVP**: Focus on MLE persona, document Ops use cases

#### Example Use Case (Future)

```
Ops team receives weekly report:
- Top 10 stores by CX risk
- Specific issues per store (prep time, inventory, etc.)
- Recommended interventions
- Expected impact
```

---

### 👩‍💼 Engineering Manager / Tech Lead

#### Needs

- **System health visibility**
  - Overall CX trends
  - Incident frequency and severity
  
- **Team velocity insights**
  - Time to diagnose issues
  - Time to resolution
  - Experiment throughput
  
- **Confidence in ML decisions**
  - Are we making data-driven decisions?
  - Are tradeoffs being considered?

#### How They'd Use Outputs

- **Weekly CX health summary**
  - Overall CX Score trends
  - Incident count and trends
  - Top issues by category
  
- **Time-to-diagnosis metrics**
  - Average time from incident to RCA
  - Average time from RCA to experiment
  - Improvement over time
  
- **Experiment throughput**
  - Number of experiments generated
  - Success rate of recommendations
  - Impact delivered

#### Status

- **Documented only (no UI)**
- **Future enhancement**: Manager dashboard
- **For MVP**: Focus on MLE persona, document manager needs

#### Example Use Case (Future)

```
EM dashboard shows:
- CX Score trend (last 30 days)
- Incidents this week: 5 (down from 8 last week)
- Avg time to diagnose: 2 hours (down from 6 hours)
- Experiments run: 12 this month
- Avg CX improvement: +8 points per experiment
```

---

### 🧑‍💼 Leadership

#### Needs

- **High-level trust and accountability**
  - Are we maintaining CX standards?
  - Are we responding quickly to issues?
  
- **Business impact**
  - How do CX issues affect business metrics?
  - What's the ROI of CX improvements?

#### How They'd Use Outputs

- **Aggregated CX trend reports**
  - Monthly CX Score trends
  - Regional/category breakdowns
  - Comparison to targets
  
- **Risk alerts**
  - High-severity incidents
  - Escalation triggers
  - Business impact estimates

#### Status

- **Documented only**
- **Future enhancement**: Executive dashboard
- **For MVP**: Focus on MLE persona, document leadership needs

#### Example Use Case (Future)

```
Monthly leadership report:
- CX Score: 85 (target: 88) - 3 points below target
- High-severity incidents: 2 (both resolved)
- Top issue: Batching policy (fixed, +12 points recovered)
- Business impact: Estimated +2% retention from fixes
```

---

## Persona Scope Summary

| Persona | Build Level | Notes |
|---------|------------|-------|
| **ML Engineer** | **Full** | Primary user - all features implemented |
| **Product Manager** | **Partial** | Read-only summaries, derived from MLE outputs |
| **Ops / Merchant Strategy** | **Conceptual** | Documented only, no UI |
| **EM / Tech Lead** | **Conceptual** | Documented only, no UI |
| **Leadership** | **Conceptual** | Documented only, no UI |

---

## Why This Persona Strategy is Strong

### 1. Matches How DoorDash Internal Tools Actually Launch
- Start with one primary persona
- Expand based on usage and feedback
- Avoid over-engineering for users who don't exist yet

### 2. Optimizes for Depth, Not UI Sprawl
- Focus on making MLE experience excellent
- Rather than making 5 personas' experiences mediocre
- Quality over quantity

### 3. Shows Ownership, Prioritization, and Scope Discipline
- Clear decision on who this is for
- Explicit tradeoffs (PM gets summaries, not full access)
- Realistic about what can be built in 14 days

### 4. Keeps Demo Focused and Compelling
- Demo from MLE perspective (primary user)
- Show depth of features
- Mention other personas as "future enhancements"

### 5. Credible for DoorDash Interview
- Shows understanding of internal tool development
- Demonstrates product thinking
- Balances ambition with realism

---

## One-Liner for Interviews

> "I designed the system primarily for ML engineers who own fulfillment and CX outcomes, while exposing derived summaries for product partners. Other personas are supported conceptually to keep scope tight and execution deep."

---

## Implementation Notes

### For MVP (14 Days)

**Build**:
- Full MLE experience (all features)
- PM summary page (read-only, derived)

**Document**:
- Ops use cases
- EM dashboard concept
- Leadership reporting concept

**Future Enhancements** (Out of Scope):
- Merchant-level dashboards
- Manager analytics
- Executive reporting
- Role-based access control

### UI Access Patterns

**MLE (Full Access)**:
- Dashboard
- Incident detail
- RCA reports
- Recommendations
- Experiment plan generation

**PM (Read-Only)**:
- Summary page
- Tradeoff view
- Impact projections
- No edit/export capabilities

**Others (Conceptual)**:
- Documented in README
- Mentioned in demo
- Not built in MVP

---

## Persona Validation

### Questions to Answer

1. **Does MLE persona have everything they need?**
   - ✅ Early detection
   - ✅ Root cause analysis
   - ✅ Recommendations with tradeoffs
   - ✅ Experiment plans

2. **Is PM persona appropriately served?**
   - ✅ Business-friendly summaries
   - ✅ Tradeoff visualization
   - ✅ Impact projections
   - ✅ No technical complexity

3. **Are other personas documented?**
   - ✅ Ops use cases documented
   - ✅ EM needs documented
   - ✅ Leadership needs documented

4. **Is scope realistic?**
   - ✅ Focus on one primary persona
   - ✅ One secondary persona (read-only)
   - ✅ Others documented, not built

---

## Demo Strategy by Persona

### MLE Demo (Primary)
- Full walkthrough of all features
- Show incident detection → RCA → recommendations → experiment plan
- Emphasize speed and accuracy

### PM Demo (Secondary)
- Show summary page
- Explain how it's derived from MLE outputs
- Show tradeoff visualization
- Mention it's read-only

### Other Personas (Mention Only)
- "We've documented use cases for Ops, EM, and Leadership"
- "These would be future enhancements"
- "For MVP, we focused on depth for the primary user"

---

## Success Metrics by Persona

### MLE
- Time to diagnose: < 2 hours (from incident to RCA)
- Time to action: < 1 day (from RCA to experiment)
- Accuracy: RCA identifies correct cause > 90% of time

### PM
- Clarity: Can understand tradeoffs without technical background
- Actionability: Can make prioritization decisions from summaries
- Timeliness: Summaries available within 1 hour of incident

### Others (Future)
- Ops: Merchant risk reports reduce CX issues by X%
- EM: Team velocity metrics improve by Y%
- Leadership: CX Score trends visible and actionable

---

## Notes

- **Start with MLE**: This is the primary user, build for them first
- **PM summaries are derived**: No separate logic, just different presentation
- **Others are documented**: Shows product thinking without scope creep
- **Future is clear**: Easy to extend to other personas later
- **Demo stays focused**: One primary persona, one compelling story


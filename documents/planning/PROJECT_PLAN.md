# CX-Fulfillment Agent: Project Execution Plan

## Project Overview

**Goal**: Build an agentic debugging + optimization workbench that detects CX degradation early, explains root causes, recommends fixes with quantified tradeoffs, and auto-generates experiment plans.

**Key Differentiators**:
- System-level ML (not just a model)
- CX-first approach
- Causal reasoning + optimization tradeoffs
- Agentic but grounded (not "LLM vibes")
- Real-world operational workflow

---

## Target Personas

**Primary Persona**: Machine Learning Engineer (Fulfillment/Inventory/Search AI)
- Full build - all features implemented
- Owns debugging, rollback, retraining, and experimentation
- Primary consumer of root-cause and causal signals

**Secondary Persona**: Product Manager (Fulfillment/CX/Inventory)
- Partial support - read-only summaries
- Consumes derived insights, not raw ML signals
- Needs business context and prioritization

**Tertiary Personas**: Operations, Engineering Manager, Leadership
- Conceptual only - documented use cases
- Future enhancements, not in MVP scope

**Rationale**: Focus on depth for primary user (MLE) rather than breadth across many personas. This matches how DoorDash internal tools actually launch and demonstrates scope discipline.

See [PERSONA_PLAN.md](../user/PERSONA_PLAN.md) for detailed persona specifications, workflows, and access patterns.

---

## Technical Architecture

### Stack Decision: **FastAPI + React/Next.js**
- **Rationale**: Best look, professional, scalable, matches DoorDash tech stack
- **Alternative considered**: Streamlit (faster but less polished)

### Component Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Frontend (Next.js)                    │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐ │
│  │Dashboard │  │Incidents │  │   RCA    │  │   Recs   │ │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘ │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  Backend API (FastAPI)                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │Data Pipeline │  │Detection     │  │RCA Agent     │  │
│  │              │  │Engine        │  │              │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │Metrics Layer │  │What-if       │  │Experiment    │  │
│  │              │  │Simulator     │  │Generator     │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Data Layer (Parquet/CSV)                    │
│  orders | deliveries | items | inventory | support |    │
│  ratings | synthetic_generator                           │
└─────────────────────────────────────────────────────────┘
```

---

## Detailed Execution Plan (14 Days)

### **Day 1-2: Dataset Generator + Schemas + Metrics**

#### Day 1 Tasks:
- [ ] Design data schemas for all tables
- [ ] Create synthetic data generator with realistic patterns
- [ ] Implement temporal relationships (orders → deliveries → items)
- [ ] Add realistic noise and correlations

#### Day 2 Tasks:
- [ ] Implement CX Metrics layer
  - [ ] CX Score calculation (weighted index)
  - [ ] On-time rate / ETA error
  - [ ] Item accuracy metrics
  - [ ] Cancellation/refund/support rates
  - [ ] Rating proxy
- [ ] Implement cohort slicing (store, category, region, time-of-day, basket size)
- [ ] Generate baseline dataset (30 days of data)

**Deliverables**:
- `data/generators/` - Synthetic data generation scripts
- `data/schemas/` - Schema definitions
- `metrics/cx_metrics.py` - Metrics calculation engine
- `data/raw/` - Generated baseline dataset

---

### **Day 3-4: Incident Detection + Slicing Engine**

#### Day 3 Tasks:
- [ ] Implement anomaly detection algorithms
  - [ ] Z-score based detection
  - [ ] EWMA (Exponentially Weighted Moving Average)
  - [ ] Simple Bayesian change point (optional)
- [ ] Create detection pipeline for CX Score + key metrics
- [ ] Implement hourly/daily aggregation

#### Day 4 Tasks:
- [ ] Build slicing engine
  - [ ] Multi-dimensional cohort analysis
  - [ ] Top regressing slice identification
  - [ ] Statistical significance testing
- [ ] Create incident data structure
- [ ] Build incident ranking/scoring system

**Deliverables**:
- `detection/anomaly_detector.py`
- `detection/slicing_engine.py`
- `detection/incident_manager.py`

---

### **Day 5-7: RCA Agent (Root Cause Analysis)**

#### Day 5 Tasks:
- [ ] Design hypothesis library
  - [ ] Supply-side hypotheses (dasher availability)
  - [ ] Merchant-side (prep-time drift)
  - [ ] Policy (batching threshold)
  - [ ] Inventory (in-stock probability)
  - [ ] Model regression (ETA bias)
- [ ] Implement SHAP-based feature attribution
  - [ ] Train simple models (logistic for late/cancel/refund)
  - [ ] Extract SHAP values per slice

#### Day 6 Tasks:
- [ ] Implement causal-style checks
  - [ ] Diff-in-diff on policy change flags
  - [ ] Correlation analysis with temporal lags
  - [ ] Attribution scoring
- [ ] Build hypothesis testing framework

#### Day 7 Tasks:
- [ ] Create RCA report generator
  - [ ] Rank causes by confidence + impact
  - [ ] Generate narrative explanations
  - [ ] Evidence aggregation
- [ ] Integrate with incident detection

**Deliverables**:
- `rca/hypothesis_library.py`
- `rca/shap_analyzer.py`
- `rca/causal_checks.py`
- `rca/report_generator.py`

---

### **Day 8-9: What-if Simulator + Recommendations**

#### Day 8 Tasks:
- [ ] Design recommendation engine
  - [ ] Action templates (reduce batching, increase ETA buffer, etc.)
  - [ ] Impact estimation logic
- [ ] Implement counterfactual simulation
  - [ ] Rule-based what-if scenarios
  - [ ] Tradeoff calculation (CX vs efficiency)

#### Day 9 Tasks:
- [ ] Build recommendation ranking
  - [ ] Expected impact scoring
  - [ ] Confidence intervals
  - [ ] Tradeoff visualization
- [ ] Create recommendation report format

**Deliverables**:
- `recommendations/action_engine.py`
- `recommendations/whatif_simulator.py`
- `recommendations/tradeoff_calculator.py`

---

### **Day 10-12: UI + Exports**

#### Day 10 Tasks:
- [ ] Set up Next.js project structure
- [ ] Create API routes in FastAPI
  - [ ] `/api/incidents`
  - [ ] `/api/rca/{incident_id}`
  - [ ] `/api/recommendations/{incident_id}`
- [ ] Build Dashboard page
  - [ ] CX Score trend visualization
  - [ ] Incident list

#### Day 11 Tasks:
- [ ] Build Incident detail page
  - [ ] Top regressing slices visualization
  - [ ] Drilldown capabilities
- [ ] Build RCA report page
  - [ ] Ranked causes display
  - [ ] Evidence visualization

#### Day 12 Tasks:
- [ ] Build Recommendations page
  - [ ] Actions with impact estimates
  - [ ] Tradeoff charts
- [ ] Implement Experiment Plan generator
  - [ ] Markdown export
  - [ ] Template with all sections
- [ ] Add export functionality

**Deliverables**:
- `frontend/` - Next.js application
- `backend/api/` - FastAPI endpoints
- `backend/exports/` - Experiment plan generator

---

### **Day 13-14: Polish + Demo Scenario + README**

#### Day 13 Tasks:
- [ ] Create demo scenario script
  - [ ] Simulate policy change (batching threshold increase on Jan 3)
  - [ ] Generate data showing regression
  - [ ] Verify detection works
  - [ ] Verify RCA identifies causes
  - [ ] Verify recommendations are generated
- [ ] Polish UI/UX
- [ ] Add error handling

#### Day 14 Tasks:
- [ ] Write comprehensive README
  - [ ] Why CX metrics matter
  - [ ] Marketplace tradeoffs explanation
  - [ ] Screenshots
  - [ ] 2-minute demo flow
- [ ] Create demo video script
- [ ] Final testing and bug fixes
- [ ] Documentation cleanup

**Deliverables**:
- `scripts/demo_scenario.py`
- `README.md`
- `documents/DEMO_SCRIPT.md`

---

## Component Specifications

### 1. Data Model

#### Tables:

**orders**
- `order_id` (str, PK)
- `user_id` (str)
- `store_id` (str)
- `category` (str: grocery/convenience/retail)
- `basket_value` (float)
- `promised_eta` (datetime)
- `order_time` (datetime)
- `region` (str)

**deliveries**
- `order_id` (str, FK)
- `actual_eta` (datetime)
- `dasher_wait` (int, seconds)
- `merchant_prep_time` (int, seconds)
- `distance` (float, miles)
- `batched_flag` (bool)
- `canceled_flag` (bool)
- `delivery_time` (datetime)

**items**
- `item_id` (str, PK)
- `order_id` (str, FK)
- `sku_id` (str)
- `ordered_qty` (int)
- `substituted_flag` (bool)
- `missing_flag` (bool)
- `refund_amount` (float)

**inventory_events**
- `event_id` (str, PK)
- `sku_id` (str)
- `store_id` (str)
- `event_time` (datetime)
- `in_stock_prob` (float, 0-1)
- `oos_flag` (bool)

**support_events**
- `ticket_id` (str, PK)
- `order_id` (str, FK)
- `issue_type` (str)
- `ticket_created` (datetime)

**ratings**
- `rating_id` (str, PK)
- `order_id` (str, FK)
- `stars` (int, 1-5)
- `free_text` (str, optional)
- `rating_time` (datetime)

### 2. CX Metrics Layer

**CX Score** (weighted index, 0-100):
```
CX Score = (
    0.30 * OnTimeScore +
    0.25 * ItemAccuracyScore +
    0.15 * CancellationScore +
    0.15 * RefundScore +
    0.10 * SupportScore +
    0.05 * RatingScore
)
```

**Sub-metrics**:
- On-time rate: % of orders within promised_eta ± 5min
- ETA error: mean absolute error (actual_eta - promised_eta)
- Item accuracy: 1 - (substituted_rate + missing_rate)
- Cancellation rate: % of canceled orders
- Refund rate: % of orders with refund_amount > 0
- Support-contact rate: % of orders with support tickets
- Rating proxy: mean stars (normalized)

**Cohort Cuts**:
- Store-level
- Category (grocery/convenience/retail)
- Region
- Time-of-day (breakfast/lunch/dinner/late-night)
- Basket size (small/medium/large)

### 3. Incident Detection

**Methods**:
1. **Z-score**: `z = (x - μ) / σ`, flag if |z| > 2.5
2. **EWMA**: `EWMA_t = α * x_t + (1-α) * EWMA_{t-1}`, flag if deviation > threshold
3. **Bayesian Change Point** (optional): Detect structural breaks

**Detection Targets**:
- CX Score (primary)
- On-time rate
- Cancellation rate
- Refund rate

**Output**: List of incidents with:
- Timestamp
- Metric affected
- Severity score
- Top regressing slices

### 4. Root Cause Agent

**Hypothesis Library**:

1. **Supply-side**: Low dasher availability
   - Check: dasher_wait time trends
   - Evidence: Correlation with lateness

2. **Merchant-side**: Prep-time drift
   - Check: merchant_prep_time vs historical baseline
   - Evidence: SHAP attribution, temporal correlation

3. **Policy**: Batching threshold increased
   - Check: batched_flag rate changes
   - Evidence: Diff-in-diff around policy change date

4. **Inventory**: In-stock probability dropped
   - Check: in_stock_prob trends
   - Evidence: Correlation with substitutions/refunds

5. **Model regression**: ETA model bias
   - Check: ETA error trends
   - Evidence: Systematic over/under-estimation

**Methods**:
- SHAP values from logistic models (late/cancel/refund)
- Diff-in-diff analysis
- Temporal correlation analysis
- Attribution scoring

**Output**: Ranked list of causes with:
- Hypothesis
- Confidence score
- Impact estimate
- Evidence summary

### 5. Recommendation Engine

**Action Templates**:

1. **Reduce batching threshold**
   - Impact: Lateness ↓, Cancellations ↓, Efficiency ↓
   - Simulation: If batched_flag → False, estimate latency reduction

2. **Increase ETA buffer**
   - Impact: On-time rate ↑, Customer wait time ↑
   - Simulation: Add buffer to promised_eta, recalculate on-time rate

3. **Suppress low-confidence SKUs**
   - Impact: Refunds ↓, Substitutions ↓, Selection coverage ↓
   - Simulation: Filter SKUs with in_stock_prob < threshold

**What-if Simulation**:
- Rule-based counterfactuals
- Estimate metric changes
- Calculate tradeoffs (CX improvement vs efficiency cost)

**Output**: Ranked recommendations with:
- Action description
- Expected impact (quantified)
- Tradeoffs
- Confidence interval

### 6. Experiment Plan Generator

**Template Sections**:

1. **Hypothesis**
   - Clear statement of what we're testing

2. **Primary/Secondary Metrics**
   - Primary: CX Score, On-time rate
   - Secondary: Cancellation rate, Refund rate
   - Guardrails: Efficiency metrics (dasher utilization, order volume)

3. **Unit of Randomization**
   - Store-level, Region-level, or Time-window based

4. **Duration + Sample Size**
   - Heuristic: 80% power, 5% lift detection
   - Minimum: 7 days, recommended: 14 days

5. **Rollout Plan**
   - Phased rollout (10% → 50% → 100%)
   - Monitoring checkpoints

6. **Monitoring Checklist**
   - Daily metric checks
   - Alert thresholds
   - Rollback criteria

**Output**: Markdown document ready for export

---

## Demo Scenario Script

### Setup (Day 13)

**Scenario**: Policy change causes CX degradation

1. **Generate baseline data** (Jan 1-2): Normal operations
2. **Simulate policy change** (Jan 3): Increase batching threshold
3. **Generate regression data** (Jan 4-5): 
   - Grocery peak hours (6-8pm) start showing:
     - Increased lateness
     - More cancellations
     - Prep-time drift (correlated)
4. **Detection** (Jan 4 morning): Tool flags incident
5. **RCA** (Jan 4): Identifies:
   - Batching as primary cause (high confidence)
   - Prep-time drift as secondary
6. **Recommendations** (Jan 4):
   - Reduce batching for fragile SKUs during peak
   - Adjust prep-time model for affected stores
7. **Experiment Plan**: Auto-generated with all sections

**Key Points to Demonstrate**:
- Early detection (same day)
- Accurate root cause identification
- Actionable recommendations
- Quantified tradeoffs
- Professional experiment plan

---

## File Structure

```
Doordash_CX_fullfilment_ML_system/
├── documents/
│   ├── PROJECT_PLAN.md (this file)
│   └── DEMO_SCRIPT.md
├── data/
│   ├── generators/
│   │   ├── __init__.py
│   │   ├── order_generator.py
│   │   ├── delivery_generator.py
│   │   ├── item_generator.py
│   │   └── synthetic_data_generator.py
│   ├── schemas/
│   │   └── schema_definitions.py
│   └── raw/
│       ├── orders.parquet
│       ├── deliveries.parquet
│       └── ...
├── metrics/
│   ├── __init__.py
│   ├── cx_metrics.py
│   └── cohort_slicer.py
├── detection/
│   ├── __init__.py
│   ├── anomaly_detector.py
│   ├── slicing_engine.py
│   └── incident_manager.py
├── rca/
│   ├── __init__.py
│   ├── hypothesis_library.py
│   ├── shap_analyzer.py
│   ├── causal_checks.py
│   └── report_generator.py
├── recommendations/
│   ├── __init__.py
│   ├── action_engine.py
│   ├── whatif_simulator.py
│   └── tradeoff_calculator.py
├── backend/
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── incidents.py
│   │   ├── rca.py
│   │   └── recommendations.py
│   └── exports/
│       └── experiment_plan_generator.py
├── frontend/
│   ├── pages/
│   │   ├── dashboard.tsx
│   │   ├── incidents/[id].tsx
│   │   ├── rca/[id].tsx
│   │   └── recommendations/[id].tsx
│   ├── components/
│   │   ├── CXScoreChart.tsx
│   │   ├── IncidentList.tsx
│   │   └── ...
│   └── ...
├── scripts/
│   └── demo_scenario.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Success Criteria

### Technical
- [ ] Synthetic data generator produces realistic patterns
- [ ] CX metrics calculated correctly across all cohorts
- [ ] Incident detection catches regressions within 24 hours
- [ ] RCA agent identifies correct root causes (validated on demo scenario)
- [ ] Recommendations have quantified impact estimates
- [ ] Experiment plans are complete and professional

### User Experience
- [ ] Dashboard loads in < 2 seconds
- [ ] All pages are responsive and intuitive
- [ ] Visualizations are clear and informative
- [ ] Export functionality works seamlessly

### Credibility
- [ ] Demo scenario feels realistic
- [ ] Tradeoffs are clearly explained
- [ ] Experiment plans match DoorDash standards
- [ ] README explains "why" not just "what"

---

## Risk Mitigation

### Potential Issues:

1. **Synthetic data too simple**
   - Mitigation: Add realistic correlations, temporal patterns, noise

2. **RCA not accurate enough**
   - Mitigation: Use multiple methods (SHAP + diff-in-diff), validate on known scenarios

3. **UI takes too long**
   - Mitigation: Start with FastAPI + simple React, add polish incrementally

4. **What-if simulation too simplistic**
   - Mitigation: Use rule-based but make rules realistic, add confidence intervals

---

## Next Steps

1. **Immediate**: Review and approve this plan
2. **Day 1 Start**: Begin with data model design and generator
3. **Daily Check-ins**: Track progress against day-by-day plan
4. **Mid-point Review** (Day 7): Validate RCA agent on test scenarios
5. **Final Review** (Day 13): Run full demo scenario end-to-end

---

## Notes

- Keep MVP simple but credible
- Focus on "feels real" over "is perfect"
- Prioritize demo scenario working flawlessly
- README is critical for DoorDash credibility
- Tradeoffs explanation is the differentiator


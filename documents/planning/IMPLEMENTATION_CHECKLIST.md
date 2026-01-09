# Implementation Checklist

## Quick Reference for Daily Development

This checklist breaks down the 14-day plan into actionable tasks with acceptance criteria.

---

## Day 1: Data Schemas + Generator Foundation

### Tasks
- [ ] Create `data/schemas/schema_definitions.py` with all table schemas
- [ ] Create `data/generators/order_generator.py`
  - [ ] Generate realistic order patterns
  - [ ] Include temporal relationships
  - [ ] Add category/region/time-of-day distributions
- [ ] Create `data/generators/delivery_generator.py`
  - [ ] Correlate with orders
  - [ ] Implement batching logic
  - [ ] Add prep-time and distance calculations
- [ ] Create `data/generators/item_generator.py`
  - [ ] Generate items per order
  - [ ] Add substitution/missing logic
- [ ] Create `data/generators/synthetic_data_generator.py`
  - [ ] Orchestrate all generators
  - [ ] Save to Parquet format

### Acceptance Criteria
- [ ] Can generate 30 days of data
- [ ] All foreign keys are valid
- [ ] Temporal relationships are correct
- [ ] Data looks realistic (spot check)

### Files to Create
```
data/
├── schemas/
│   └── schema_definitions.py
├── generators/
│   ├── __init__.py
│   ├── order_generator.py
│   ├── delivery_generator.py
│   ├── item_generator.py
│   └── synthetic_data_generator.py
```

---

## Day 2: Metrics Layer + Cohort Slicing

### Tasks
- [ ] Create `metrics/cx_metrics.py`
  - [ ] Implement CX Score calculation (weighted index)
  - [ ] Implement on-time rate
  - [ ] Implement ETA error
  - [ ] Implement item accuracy
  - [ ] Implement cancellation rate
  - [ ] Implement refund rate
  - [ ] Implement support-contact rate
  - [ ] Implement rating proxy
- [ ] Create `metrics/cohort_slicer.py`
  - [ ] Implement store-level slicing
  - [ ] Implement category slicing
  - [ ] Implement region slicing
  - [ ] Implement time-of-day slicing
  - [ ] Implement basket-size slicing
  - [ ] Implement multi-dimensional slicing
- [ ] Generate baseline dataset (30 days)
- [ ] Calculate metrics for all cohorts

### Acceptance Criteria
- [ ] CX Score is between 0-100
- [ ] All sub-metrics calculate correctly
- [ ] Cohort slicing works for all dimensions
- [ ] Can aggregate metrics by any cohort combination

### Files to Create
```
metrics/
├── __init__.py
├── cx_metrics.py
└── cohort_slicer.py
```

---

## Day 3: Anomaly Detection

### Tasks
- [ ] Create `detection/anomaly_detector.py`
  - [ ] Implement Z-score detection
  - [ ] Implement EWMA detection
  - [ ] Implement Bayesian change point (optional)
  - [ ] Add configurable thresholds
- [ ] Create `detection/incident_manager.py`
  - [ ] Define incident data structure
  - [ ] Implement incident creation
  - [ ] Implement incident ranking/scoring
- [ ] Test detection on known anomalies

### Acceptance Criteria
- [ ] Detects anomalies in CX Score
- [ ] Detects anomalies in key metrics
- [ ] Creates incident records
- [ ] Ranks incidents by severity

### Files to Create
```
detection/
├── __init__.py
├── anomaly_detector.py
└── incident_manager.py
```

---

## Day 4: Slicing Engine

### Tasks
- [ ] Create `detection/slicing_engine.py`
  - [ ] Implement top regressing slice identification
  - [ ] Add statistical significance testing
  - [ ] Implement slice comparison
  - [ ] Add visualization data preparation
- [ ] Integrate with incident manager
- [ ] Test on demo scenario data

### Acceptance Criteria
- [ ] Identifies top regressing slices correctly
- [ ] Calculates significance scores
- [ ] Handles multi-dimensional slices
- [ ] Returns data ready for visualization

### Files to Create
```
detection/
└── slicing_engine.py
```

---

## Day 5: Hypothesis Library + SHAP Setup

### Tasks
- [ ] Create `rca/hypothesis_library.py`
  - [ ] Define hypothesis templates
  - [ ] Implement supply-side hypothesis
  - [ ] Implement merchant-side hypothesis
  - [ ] Implement policy hypothesis
  - [ ] Implement inventory hypothesis
  - [ ] Implement model regression hypothesis
- [ ] Create `rca/shap_analyzer.py`
  - [ ] Train logistic models (late/cancel/refund)
  - [ ] Extract SHAP values
  - [ ] Aggregate SHAP by slice
- [ ] Test SHAP on sample data

### Acceptance Criteria
- [ ] All hypothesis types are defined
- [ ] SHAP values are calculated correctly
- [ ] Can attribute features to outcomes
- [ ] Works on slice-level data

### Files to Create
```
rca/
├── __init__.py
├── hypothesis_library.py
└── shap_analyzer.py
```

---

## Day 6: Causal Checks

### Tasks
- [ ] Create `rca/causal_checks.py`
  - [ ] Implement diff-in-diff analysis
  - [ ] Implement temporal correlation
  - [ ] Implement attribution scoring
  - [ ] Add confidence calculation
- [ ] Test on demo scenario (policy change)

### Acceptance Criteria
- [ ] Diff-in-diff detects policy changes
- [ ] Temporal correlations are calculated
- [ ] Confidence scores are reasonable
- [ ] Works with known scenarios

### Files to Create
```
rca/
└── causal_checks.py
```

---

## Day 7: RCA Report Generator

### Tasks
- [ ] Create `rca/report_generator.py`
  - [ ] Implement hypothesis ranking
  - [ ] Generate narrative explanations
  - [ ] Aggregate evidence
  - [ ] Format report output
- [ ] Integrate all RCA components
- [ ] Test end-to-end RCA on demo scenario

### Acceptance Criteria
- [ ] Ranks causes by confidence × impact
- [ ] Generates readable narrative
- [ ] Includes evidence for each cause
- [ ] Identifies correct root cause in demo

### Files to Create
```
rca/
└── report_generator.py
```

---

## Day 8: Recommendation Engine

### Tasks
- [ ] Create `recommendations/action_engine.py`
  - [ ] Define action templates
  - [ ] Implement action parameterization
  - [ ] Add action ranking logic
- [ ] Create `recommendations/whatif_simulator.py`
  - [ ] Implement counterfactual rules
  - [ ] Simulate batching reduction
  - [ ] Simulate ETA buffer increase
  - [ ] Simulate SKU suppression
- [ ] Test simulations on demo scenario

### Acceptance Criteria
- [ ] Generates actions for top causes
- [ ] Simulations produce reasonable estimates
- [ ] Impact estimates are quantified
- [ ] Works with demo scenario

### Files to Create
```
recommendations/
├── __init__.py
├── action_engine.py
└── whatif_simulator.py
```

---

## Day 9: Tradeoff Calculator

### Tasks
- [ ] Create `recommendations/tradeoff_calculator.py`
  - [ ] Calculate CX vs efficiency tradeoffs
  - [ ] Generate confidence intervals
  - [ ] Format tradeoff data for visualization
- [ ] Integrate with recommendation engine
- [ ] Test tradeoff calculations

### Acceptance Criteria
- [ ] Tradeoffs are calculated correctly
- [ ] Confidence intervals are included
- [ ] Data format supports visualization
- [ ] Tradeoffs are realistic

### Files to Create
```
recommendations/
└── tradeoff_calculator.py
```

---

## Day 10: Backend API Setup

### Tasks
- [ ] Create `backend/api/main.py` (FastAPI app)
- [ ] Create `backend/api/incidents.py`
  - [ ] `GET /api/incidents` - List incidents
  - [ ] `GET /api/incidents/{id}` - Get incident details
- [ ] Create `backend/api/rca.py`
  - [ ] `GET /api/incidents/{id}/rca` - Get RCA report
- [ ] Create `backend/api/recommendations.py`
  - [ ] `GET /api/incidents/{id}/recommendations` - Get recommendations
- [ ] Create `backend/api/metrics.py`
  - [ ] `GET /api/metrics/cx-score` - Get CX Score time series
- [ ] Test all endpoints

### Acceptance Criteria
- [ ] All endpoints return correct data
- [ ] Error handling works
- [ ] Response times are acceptable (<2s)
- [ ] API documentation is generated

### Files to Create
```
backend/
├── api/
│   ├── __init__.py
│   ├── main.py
│   ├── incidents.py
│   ├── rca.py
│   ├── recommendations.py
│   └── metrics.py
```

---

## Day 11: Frontend - Dashboard + Incident View

### Tasks
- [ ] Set up Next.js project
- [ ] Create Dashboard page (`pages/dashboard.tsx`)
  - [ ] CX Score trend chart
  - [ ] Incident list
  - [ ] Quick stats cards
- [ ] Create Incident detail page (`pages/incidents/[id].tsx`)
  - [ ] Incident metadata
  - [ ] Top slices visualization
  - [ ] Metric breakdown
- [ ] Add API integration
- [ ] Style with Tailwind CSS

### Acceptance Criteria
- [ ] Dashboard loads and displays data
- [ ] Charts render correctly
- [ ] Incident detail page works
- [ ] UI is responsive

### Files to Create
```
frontend/
├── pages/
│   ├── dashboard.tsx
│   └── incidents/
│       └── [id].tsx
├── components/
│   ├── CXScoreChart.tsx
│   └── IncidentList.tsx
└── ...
```

---

## Day 12: Frontend - RCA + Recommendations + Export

### Tasks
- [ ] Create RCA report page (`pages/rca/[id].tsx`)
  - [ ] Ranked causes display
  - [ ] Evidence visualization
  - [ ] Confidence scores
- [ ] Create Recommendations page (`pages/recommendations/[id].tsx`)
  - [ ] Actions with impact
  - [ ] Tradeoff charts
  - [ ] Export button
- [ ] Create `backend/exports/experiment_plan_generator.py`
  - [ ] Generate markdown experiment plan
  - [ ] Include all required sections
- [ ] Add export functionality

### Acceptance Criteria
- [ ] RCA page displays correctly
- [ ] Recommendations page shows tradeoffs
- [ ] Experiment plan exports as markdown
- [ ] All pages are functional

### Files to Create
```
frontend/
├── pages/
│   ├── rca/
│   │   └── [id].tsx
│   └── recommendations/
│       └── [id].tsx
backend/
└── exports/
    └── experiment_plan_generator.py
```

---

## Day 13: Demo Scenario Script

### Tasks
- [ ] Create `scripts/demo_scenario.py`
  - [ ] Generate baseline data (Jan 1-2)
  - [ ] Simulate policy change (Jan 3)
  - [ ] Generate regression data (Jan 4-5)
  - [ ] Verify detection works
  - [ ] Verify RCA identifies causes
  - [ ] Verify recommendations generated
- [ ] Run full demo scenario end-to-end
- [ ] Fix any issues
- [ ] Polish UI/UX

### Acceptance Criteria
- [ ] Demo scenario generates correctly
- [ ] Incident detected on Jan 4
- [ ] RCA identifies batching as top cause
- [ ] Recommendations are generated
- [ ] Everything works end-to-end

### Files to Create
```
scripts/
└── demo_scenario.py
```

---

## Day 14: README + Final Polish

### Tasks
- [ ] Write comprehensive README.md
  - [ ] Project overview
  - [ ] Why CX metrics matter
  - [ ] Marketplace tradeoffs explanation
  - [ ] Installation instructions
  - [ ] Usage guide
  - [ ] Screenshots
  - [ ] Demo flow description
- [ ] Add screenshots to README
- [ ] Create `documents/DEMO_SCRIPT.md` (already done)
- [ ] Final testing
- [ ] Bug fixes
- [ ] Code cleanup

### Acceptance Criteria
- [ ] README is comprehensive and professional
- [ ] Screenshots are included
- [ ] Installation works from scratch
- [ ] Demo scenario runs successfully
- [ ] Code is clean and documented

### Files to Create
```
README.md
```

---

## Daily Standup Questions

Use these questions each day to track progress:

1. **What did I complete yesterday?**
2. **What am I working on today?**
3. **Any blockers?**
4. **On track for 14-day deadline?**

---

## Testing Strategy

### Unit Tests (as you go)
- Test each function with known inputs
- Verify calculations are correct
- Test edge cases

### Integration Tests (Day 7, 10, 13)
- Test RCA end-to-end
- Test API endpoints
- Test full demo scenario

### Manual Testing (Day 13-14)
- Run demo scenario
- Verify UI works
- Check all pages load
- Test export functionality

---

## Common Issues & Solutions

### Issue: Data generation too slow
**Solution**: Use vectorized operations, generate in chunks, save intermediate results

### Issue: SHAP takes too long
**Solution**: Sample data for SHAP, use faster SHAP implementations, cache results

### Issue: Frontend not connecting to backend
**Solution**: Check CORS settings, verify API endpoints, check network tab

### Issue: Metrics don't match expectations
**Solution**: Verify formulas, check data quality, add debug logging

### Issue: RCA not identifying correct cause
**Solution**: Tune confidence thresholds, add more evidence sources, validate on known scenarios

---

## Progress Tracking

### Week 1 (Days 1-7): Core Logic
- [ ] Day 1: Data generator
- [ ] Day 2: Metrics
- [ ] Day 3: Detection
- [ ] Day 4: Slicing
- [ ] Day 5: SHAP
- [ ] Day 6: Causal
- [ ] Day 7: RCA report

### Week 2 (Days 8-14): UI + Polish
- [ ] Day 8: Recommendations
- [ ] Day 9: Tradeoffs
- [ ] Day 10: API
- [ ] Day 11: Frontend pages 1-2
- [ ] Day 12: Frontend pages 3-4
- [ ] Day 13: Demo scenario
- [ ] Day 14: README + polish

---

## Success Criteria Summary

### Must Have (MVP)
- [x] Synthetic data generator works
- [ ] CX metrics calculate correctly
- [ ] Incident detection works
- [ ] RCA identifies correct causes
- [ ] Recommendations generated
- [ ] Experiment plan exports
- [ ] UI displays all pages
- [ ] Demo scenario works end-to-end

### Nice to Have (Polish)
- [ ] Interactive visualizations
- [ ] Real-time updates
- [ ] More sophisticated anomaly detection
- [ ] Additional hypothesis types
- [ ] Performance optimizations

---

## Notes

- **Focus on MVP first**: Get core functionality working before polish
- **Test as you go**: Don't wait until the end to test
- **Demo scenario is critical**: Make sure it works perfectly
- **README matters**: This is what DoorDash will see first
- **Tradeoffs are key**: This is the differentiator


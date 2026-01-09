# CX-Fulfillment Agent

An agentic debugging + optimization workbench that detects CX degradation early, explains root causes, recommends fixes with quantified tradeoffs, and auto-generates experiment plans.

## 🔗 Repository

**GitHub**: [https://github.com/lokesh75-kank/CX_fulfillment_ML_System.git](https://github.com/lokesh75-kank/CX_fulfillment_ML_System.git)

**🌐 Landing Page**: [View Live Site](https://lokesh75-kank.github.io/CX_fulfillment_ML_System/)

## Overview

When customer experience degrades (late orders, wrong items, substitutions, cancellations), the CX-Fulfillment Agent:

- **Detects it early** - Automated anomaly detection on CX metrics
- **Explains root causes** - Agentic root cause analysis with hypothesis testing
- **Recommends fixes** - Actionable recommendations with quantified tradeoffs (CX vs efficiency)
- **Generates experiment plans** - Auto-generated PRD-style experiment writeups

## Key Features

### 🎯 CX-First Approach
- Single top-line CX Score + decompositions
- On-time rate, item accuracy, cancellation rate, refund rate, support rate
- Cohort analysis (store, category, region, time-of-day, basket size)

### 🔍 Early Detection
- Daily/hourly anomaly detection on CX Score + key metrics
- Auto-identifies "top regressing slices"
- Z-score / EWMA / Bayesian change point detection

### 🧠 Root Cause Agent
- Hypothesis library (supply-side, merchant-side, policy, inventory, model regression)
- SHAP-based feature attribution
- Causal checks (diff-in-diff, temporal correlation)
- Ranked causes with confidence scores

### 💡 Recommendations & What-If Simulator
- Actionable fixes with expected impact
- Quantified tradeoffs (CX improvement vs efficiency cost)
- Counterfactual simulation
- Confidence intervals

### 📋 Experiment Plan Generator
- Auto-generated experiment plans
- Hypothesis, metrics, guardrails
- Unit of randomization, duration, sample size
- Rollout & monitoring checklist

## Tech Stack

- **Backend**: FastAPI + Python
- **Frontend**: Next.js + React + TypeScript
- **Data**: Parquet files (synthetic dataset)
- **ML**: SHAP, scikit-learn, pandas
- **Detection**: Z-score, EWMA, Bayesian change point

## Project Structure

```
Doordash_CX_fullfilment_ML_system/
├── documents/          # Planning and design documents
│   ├── planning/      # Project plans and checklists
│   ├── technical/     # Architecture and data specs
│   └── user/          # Personas, journeys, demo scripts
├── data/              # Synthetic data generators
├── metrics/           # CX metrics calculation
├── detection/         # Incident detection engine
├── rca/              # Root cause analysis agent
├── recommendations/   # Recommendation engine
├── backend/          # FastAPI backend
└── frontend/         # Next.js frontend
```

## Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn

### Installation

```bash
# Clone the repository
git clone https://github.com/lokesh75-kank/CX_fulfillment_ML_System.git
cd CX_fulfillment_ML_System

# Install Python dependencies
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
```

### Running the Application

```bash
# Start backend (from project root)
uvicorn backend.api.main:app --reload

# Start frontend (from frontend directory)
npm run dev
```

## Documentation

Comprehensive planning and design documents are available in the [`documents/`](./documents/) folder:

- **[Planning Documents](./documents/planning/)** - Project execution plan and implementation checklist
- **[Technical Documents](./documents/technical/)** - Architecture and data schema specifications
- **[User Documents](./documents/user/)** - Personas, user journeys, and demo scripts

See [`documents/README.md`](./documents/README.md) for complete documentation index.

## Demo Scenario

The system includes a realistic demo scenario simulating a policy change (batching threshold increase) that causes CX degradation:

1. **Jan 1-2**: Baseline (normal operations)
2. **Jan 3**: Policy change deployed
3. **Jan 4**: Regression detected automatically
4. **Jan 4**: RCA identifies root cause (batching threshold)
5. **Jan 4**: Recommendations generated
6. **Jan 4**: Experiment plan created
7. **2 weeks later**: Issue resolved

See [`documents/user/DEMO_SCRIPT.md`](./documents/user/DEMO_SCRIPT.md) for detailed demo walkthrough.

## Target Users

### Primary Persona: ML Engineer
- Full access to all features
- Owns debugging, rollback, retraining, and experimentation
- Primary consumer of root-cause and causal signals

### Secondary Persona: Product Manager
- Read-only summaries
- Business-friendly tradeoff visualizations
- Impact projections

See [`documents/user/PERSONA_PLAN.md`](./documents/user/PERSONA_PLAN.md) for detailed persona specifications.

## Key Differentiators

- **System-level ML** - Not just a model, but a complete operational workflow
- **CX-first** - Customer experience is the primary metric
- **Causal reasoning** - SHAP + diff-in-diff for credible root cause analysis
- **Agentic but grounded** - Not "LLM vibes", but systematic hypothesis testing
- **Real-world operational** - Matches how high-performing ML orgs operate

## Development Timeline

- **14 days** total
- **Week 1**: Core logic (data, metrics, detection, RCA)
- **Week 2**: UI, recommendations, demo, polish

See [`documents/planning/PROJECT_PLAN.md`](./documents/planning/PROJECT_PLAN.md) for detailed execution plan.

## License

MIT License - See [LICENSE](./LICENSE) file for details.

## Contributing

This is a portfolio project demonstrating ML system design, causal reasoning, and operational ML workflows.

## Contact

- **GitHub**: [lokesh75-kank](https://github.com/lokesh75-kank)
- **Repository**: [CX_fulfillment_ML_System](https://github.com/lokesh75-kank/CX_fulfillment_ML_System)

---

**Built with ❤️ for demonstrating ML system design and operational excellence**


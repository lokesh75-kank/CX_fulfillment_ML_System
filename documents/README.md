# CX-Fulfillment Agent: Planning Documents

This folder contains comprehensive planning documents for building the CX-Fulfillment Agent project.

**Repository**: [https://github.com/lokesh75-kank/CX_fulfillment_ML_System.git](https://github.com/lokesh75-kank/CX_fulfillment_ML_System.git)

**Main README**: [../README.md](../README.md)

## Document Organization

Documents are organized into three categories:

- **📋 Planning** (`planning/`) - Project execution plans and checklists
- **🔧 Technical** (`technical/`) - Architecture and data specifications
- **👤 User** (`user/`) - Personas, user journeys, and demo scripts

---

## Document Overview

### Planning Documents

#### 1. [PROJECT_PLAN.md](./planning/PROJECT_PLAN.md)
**Main execution plan** - Start here!

- Complete 14-day day-by-day breakdown
- Component specifications
- Success criteria
- Risk mitigation
- File structure
- Demo scenario overview

**Use this for**: Understanding the full scope and timeline

#### 2. [IMPLEMENTATION_CHECKLIST.md](./planning/IMPLEMENTATION_CHECKLIST.md)
**Daily task checklist**

- Day-by-day actionable tasks
- Acceptance criteria
- Files to create
- Testing strategy
- Common issues & solutions

**Use this for**: Daily development tracking

---

### Technical Documents

#### 3. [TECHNICAL_ARCHITECTURE.md](./technical/TECHNICAL_ARCHITECTURE.md)
**System design and architecture**

- Architecture diagrams
- Technology stack decisions
- Component details
- API specifications
- Data flow examples
- Performance considerations

**Use this for**: Understanding how the system is built

#### 4. [DATA_SCHEMA.md](./technical/DATA_SCHEMA.md)
**Complete data model specification**

- All table schemas
- Relationships and constraints
- Data generation rules
- Sample data examples
- Validation queries

**Use this for**: Implementing data generators and understanding data structure

#### 5. [ANOMALY_DETECTION_ALGORITHM.md](./technical/ANOMALY_DETECTION_ALGORITHM.md)
**Anomaly detection algorithm documentation**

- Z-score detection method (formulas, examples, parameters)
- EWMA (Exponentially Weighted Moving Average) method
- Bayesian change point detection
- Combined consensus method
- Severity calculation
- Configuration parameters and tuning
- Performance characteristics
- Edge cases and handling

**Use this for**: Understanding how incidents are automatically detected and flagged

---

### User Documents

#### 5. [PERSONA_PLAN.md](./user/PERSONA_PLAN.md)
**Target users and their needs**

- Primary persona: ML Engineer (full build)
- Secondary persona: Product Manager (partial support)
- Tertiary personas: Ops, EM, Leadership (conceptual)
- Access patterns and workflows
- Demo strategy by persona

**Use this for**: Understanding who the system is built for and how they'll use it

#### 6. [USER_JOURNEY.md](./user/USER_JOURNEY.md)
**Step-by-step user experience**

- Complete user journey from incident detection to resolution
- What user sees at each step
- Decision points and outcomes
- Timeline and value delivered
- Alternative scenarios

**Use this for**: Understanding the end-to-end user experience and workflow

#### 7. [DEMO_SCRIPT.md](./user/DEMO_SCRIPT.md)
**Step-by-step demo scenario**

- Exact timeline and events
- What to show at each step
- Narrative for 2-minute demo
- Technical implementation details
- Validation checks

**Use this for**: Preparing and executing the demo

---

## Quick Start Guide

### For Project Managers
1. Read **[PROJECT_PLAN.md](./planning/PROJECT_PLAN.md)** for scope and timeline
2. Review **[DEMO_SCRIPT.md](./user/DEMO_SCRIPT.md)** to understand the end goal
3. Use **[IMPLEMENTATION_CHECKLIST.md](./planning/IMPLEMENTATION_CHECKLIST.md)** for daily tracking

### For Developers
1. Start with **[PROJECT_PLAN.md](./planning/PROJECT_PLAN.md)** for overview
2. Read **[TECHNICAL_ARCHITECTURE.md](./technical/TECHNICAL_ARCHITECTURE.md)** for system design
3. Reference **[DATA_SCHEMA.md](./technical/DATA_SCHEMA.md)** when building data generators
4. Use **[IMPLEMENTATION_CHECKLIST.md](./planning/IMPLEMENTATION_CHECKLIST.md)** for daily tasks
5. Follow **[DEMO_SCRIPT.md](./user/DEMO_SCRIPT.md)** when preparing demo

### For Reviewers
1. Read **[PROJECT_PLAN.md](./planning/PROJECT_PLAN.md)** to understand the approach
2. Review **[TECHNICAL_ARCHITECTURE.md](./technical/TECHNICAL_ARCHITECTURE.md)** for technical decisions
3. Check **[DEMO_SCRIPT.md](./user/DEMO_SCRIPT.md)** to see the end result

---

## Project Summary

### Goal
Build an agentic debugging + optimization workbench that:
- Detects CX degradation early
- Explains root causes
- Recommends fixes with quantified tradeoffs
- Auto-generates experiment plans

### Key Components
1. **Data Model**: Synthetic dataset generator
2. **Metrics Layer**: CX Score + decompositions
3. **Incident Detection**: Anomaly detection + slicing
4. **RCA Agent**: Hypothesis testing + SHAP + causal checks
5. **Recommendations**: What-if simulator + tradeoffs
6. **Experiment Plans**: Auto-generated markdown

### Timeline
- **14 days** total
- **Week 1**: Core logic (data, metrics, detection, RCA)
- **Week 2**: UI, recommendations, demo, polish

### Tech Stack
- **Backend**: FastAPI + Python
- **Frontend**: Next.js + React + TypeScript
- **Data**: Parquet files
- **ML**: SHAP, scikit-learn, pandas

---

## Success Metrics

### Technical
- ✅ Synthetic data generator produces realistic patterns
- ✅ CX metrics calculated correctly
- ✅ Incident detection catches regressions within 24 hours
- ✅ RCA identifies correct root causes
- ✅ Recommendations have quantified impact
- ✅ Experiment plans are complete

### Presentation
- ✅ Demo scenario feels realistic
- ✅ Tradeoffs are clearly explained
- ✅ Experiment plans match DoorDash standards
- ✅ README explains "why" not just "what"

---

## Next Steps

1. **Review all documents** to understand the full scope
2. **Set up development environment** (Python, Node.js, etc.)
3. **Start Day 1 tasks** from [IMPLEMENTATION_CHECKLIST.md](./planning/IMPLEMENTATION_CHECKLIST.md)
4. **Track progress daily** using the checklist

---

## Questions?

Refer to the specific document:
- **Scope/timeline**: [PROJECT_PLAN.md](./planning/PROJECT_PLAN.md)
- **Technical details**: [TECHNICAL_ARCHITECTURE.md](./technical/TECHNICAL_ARCHITECTURE.md)
- **Data structure**: [DATA_SCHEMA.md](./technical/DATA_SCHEMA.md)
- **Demo prep**: [DEMO_SCRIPT.md](./user/DEMO_SCRIPT.md)
- **Daily tasks**: [IMPLEMENTATION_CHECKLIST.md](./planning/IMPLEMENTATION_CHECKLIST.md)
- **Target users**: [PERSONA_PLAN.md](./user/PERSONA_PLAN.md)
- **User experience**: [USER_JOURNEY.md](./user/USER_JOURNEY.md)

---

## Document Status

All planning documents are complete and ready for implementation.

**Last Updated**: Project start
**Status**: ✅ Ready to begin development

---

## Folder Structure

```
documents/
├── README.md (this file)
├── planning/
│   ├── PROJECT_PLAN.md
│   └── IMPLEMENTATION_CHECKLIST.md
├── technical/
│   ├── TECHNICAL_ARCHITECTURE.md
│   └── DATA_SCHEMA.md
└── user/
    ├── PERSONA_PLAN.md
    ├── USER_JOURNEY.md
    └── DEMO_SCRIPT.md
```

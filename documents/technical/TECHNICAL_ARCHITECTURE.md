# Technical Architecture

## System Overview

The CX-Fulfillment Agent is built as a modern web application with a clear separation between data processing, business logic, and presentation layers.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend Layer                           │
│                         (Next.js/React)                         │
├─────────────────────────────────────────────────────────────────┤
│  Dashboard Page    │  Incident View  │  RCA Report  │  Recs     │
│  - CX Score trends │  - Top slices   │  - Causes    │  - Actions │
│  - Incident list   │  - Drilldown    │  - Evidence  │  - Impact  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/REST API
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Backend API Layer                          │
│                        (FastAPI)                                │
├─────────────────────────────────────────────────────────────────┤
│  /api/incidents          │  /api/rca/{id}  │  /api/recs/{id}   │
│  - List incidents        │  - Get RCA      │  - Get recs       │
│  - Get incident details  │  - Generate     │  - Simulate       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Python calls
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Business Logic Layer                       │
│                         (Python)                                │
├─────────────────────────────────────────────────────────────────┤
│  Detection Engine  │  RCA Agent    │  Recommendation Engine    │
│  - Anomaly detect  │  - Hypothesis │  - Action templates       │
│  - Slicing         │  - SHAP       │  - What-if simulation     │
│  - Incident mgmt   │  - Causal     │  - Tradeoff calc          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Data access
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Data Layer                                │
│                    (Parquet/CSV Files)                          │
├─────────────────────────────────────────────────────────────────┤
│  orders │ deliveries │ items │ inventory │ support │ ratings    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Generation
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Synthetic Data Generator                      │
│                      (Python Scripts)                            │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend (Next.js)

**Technology Stack**:
- Next.js 14+ (App Router)
- TypeScript
- Tailwind CSS (for styling)
- Recharts or Chart.js (for visualizations)
- React Query (for data fetching)

**Key Pages**:
1. **Dashboard** (`/`)
   - CX Score trend chart (time series)
   - Active incidents list
   - Quick stats cards

2. **Incident Detail** (`/incidents/[id]`)
   - Incident metadata
   - Top regressing slices visualization
   - Metric breakdown charts
   - Link to RCA report

3. **RCA Report** (`/rca/[id]`)
   - Ranked root causes
   - Evidence visualization
   - Confidence scores
   - Link to recommendations

4. **Recommendations** (`/recommendations/[id]`)
   - Actionable recommendations
   - Impact estimates with confidence intervals
   - Tradeoff charts (CX vs Efficiency)
   - Export experiment plan button

**State Management**:
- React Query for server state
- Local state for UI interactions

### Backend API (FastAPI)

**Technology Stack**:
- FastAPI
- Pydantic (for data validation)
- Pandas (for data manipulation)
- NumPy (for calculations)

**API Endpoints**:

```
GET  /api/incidents
     - Query params: start_date, end_date, severity
     - Returns: List of incidents

GET  /api/incidents/{incident_id}
     - Returns: Incident details

GET  /api/incidents/{incident_id}/rca
     - Returns: RCA report (causes, evidence, confidence)

GET  /api/incidents/{incident_id}/recommendations
     - Returns: Recommendations with impact estimates

POST /api/incidents/{incident_id}/experiment-plan
     - Returns: Markdown experiment plan

GET  /api/metrics/cx-score
     - Query params: start_date, end_date, cohort
     - Returns: CX Score time series

GET  /api/metrics/cohorts
     - Returns: Available cohort dimensions
```

**Error Handling**:
- Standard HTTP status codes
- JSON error responses with details
- Logging for debugging

### Business Logic Layer

#### Detection Engine

**Components**:
- `AnomalyDetector`: Z-score, EWMA, Bayesian change point
- `SlicingEngine`: Multi-dimensional cohort analysis
- `IncidentManager`: Incident creation, ranking, storage

**Flow**:
1. Calculate metrics for all cohorts
2. Run anomaly detection on CX Score + key metrics
3. Identify top regressing slices
4. Create incident records
5. Rank incidents by severity

#### RCA Agent

**Components**:
- `HypothesisLibrary`: Pre-defined hypothesis templates
- `SHAPAnalyzer`: Feature attribution using SHAP
- `CausalChecker`: Diff-in-diff, correlation analysis
- `ReportGenerator`: Narrative report creation

**Flow**:
1. Load incident and affected slice data
2. For each hypothesis:
   - Extract relevant features
   - Run SHAP analysis
   - Perform causal checks
   - Calculate confidence score
3. Rank hypotheses by confidence × impact
4. Generate narrative report

#### Recommendation Engine

**Components**:
- `ActionEngine`: Action templates and parameterization
- `WhatIfSimulator`: Counterfactual simulation
- `TradeoffCalculator`: CX vs efficiency tradeoffs

**Flow**:
1. Take top 2-3 root causes from RCA
2. For each cause, generate action templates
3. Run what-if simulation for each action
4. Calculate expected impact and tradeoffs
5. Rank recommendations

### Data Layer

**Storage Format**: Parquet files (efficient, columnar)

**Data Flow**:
1. Synthetic generator creates initial dataset
2. Data stored in `data/raw/` directory
3. Metrics calculated on-demand or cached
4. No database needed for MVP (file-based is sufficient)

**Data Access Pattern**:
- Read entire tables into Pandas DataFrames
- Filter and aggregate in memory
- Cache frequently accessed aggregations

### Synthetic Data Generator

**Purpose**: Create realistic dataset without DoorDash data

**Key Features**:
- Temporal relationships (orders → deliveries → items)
- Realistic correlations (e.g., batching → lateness)
- Policy change simulation (for demo scenario)
- Configurable noise and variance

**Generator Scripts**:
- `order_generator.py`: Creates orders with realistic patterns
- `delivery_generator.py`: Generates deliveries with correlations
- `item_generator.py`: Creates items with substitution/missing logic
- `synthetic_data_generator.py`: Orchestrates all generators

## Data Flow Example

### Incident Detection Flow

```
1. User opens Dashboard
   ↓
2. Frontend calls GET /api/incidents
   ↓
3. Backend Detection Engine:
   - Reads metrics data
   - Runs anomaly detection
   - Identifies top slices
   - Returns incidents
   ↓
4. Frontend displays incidents
```

### RCA Flow

```
1. User clicks on incident
   ↓
2. Frontend calls GET /api/incidents/{id}/rca
   ↓
3. Backend RCA Agent:
   - Loads incident data
   - Runs hypothesis tests
   - Calculates SHAP values
   - Performs causal checks
   - Generates report
   ↓
4. Frontend displays RCA report
```

### Recommendation Flow

```
1. User views RCA report
   ↓
2. Frontend calls GET /api/incidents/{id}/recommendations
   ↓
3. Backend Recommendation Engine:
   - Takes top causes from RCA
   - Generates action templates
   - Runs what-if simulations
   - Calculates tradeoffs
   ↓
4. Frontend displays recommendations
```

## Performance Considerations

### Optimization Strategies

1. **Data Caching**:
   - Cache calculated metrics
   - Cache cohort aggregations
   - Use Parquet for efficient reads

2. **Lazy Loading**:
   - Only calculate RCA when requested
   - Generate recommendations on-demand

3. **Parallel Processing**:
   - Run hypothesis tests in parallel
   - Parallel what-if simulations

4. **Frontend Optimization**:
   - React Query caching
   - Pagination for large lists
   - Virtual scrolling if needed

## Scalability Notes

**MVP Scope**: File-based, single-machine deployment

**Future Scalability** (out of scope for MVP):
- Database (PostgreSQL/ClickHouse) for larger datasets
- Distributed processing (Spark/Dask)
- Real-time streaming (Kafka)
- Microservices architecture

## Security Considerations

**MVP**: No authentication needed (demo tool)

**Future** (out of scope):
- User authentication
- Role-based access control
- API rate limiting
- Data encryption

## Deployment

**Development**:
- Local development with hot reload
- FastAPI: `uvicorn main:app --reload`
- Next.js: `npm run dev`

**Production** (future):
- Docker containers
- Kubernetes orchestration
- CI/CD pipeline

## Technology Choices Rationale

### FastAPI over Flask
- Better performance
- Automatic API documentation
- Type hints support
- Modern async support

### Next.js over plain React
- Server-side rendering
- Better SEO (if needed)
- File-based routing
- Built-in optimizations

### Parquet over CSV
- Columnar format (faster queries)
- Compression (smaller files)
- Type preservation
- Industry standard

### SHAP over other attribution methods
- Model-agnostic
- Well-documented
- Good interpretability
- Widely used in industry


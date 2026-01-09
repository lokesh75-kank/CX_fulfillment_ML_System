# Frontend Usage Guide

## Setup

### Prerequisites
- Node.js 18+ installed
- Backend API running on `http://localhost:8000`

### Installation

```bash
cd frontend
npm install
```

### Running the Frontend

```bash
npm run dev
```

The frontend will start on `http://localhost:3000`

---

## User Workflow

### 1. Dashboard (`/`)

**What you see:**
- Current CX Score (with delta from baseline)
- Number of active incidents
- Trend indicator (up/down/stable)
- List of active incidents

**What you can do:**
- View overall system health
- See all active incidents at a glance
- Click on any incident to view details

**Navigation:**
- Click "View Details →" on any incident card

---

### 2. Incident Detail Page (`/incidents/[id]`)

**What you see:**
- Incident metadata (detected time, severity, status)
- Current vs baseline metric values
- Delta (change amount and percentage)
- Top regressing slices (which cohorts are most affected)
- Description of the incident

**What you can do:**
- Understand what happened
- See which cohorts are most affected
- Navigate to RCA or Recommendations

**Navigation:**
- Click "View RCA Report" → Goes to RCA page
- Click "View Recommendations" → Goes to Recommendations page
- Click "← Back to Dashboard" → Returns to dashboard

---

### 3. RCA Report Page (`/rca/[id]`)

**What you see:**
- Summary statement (e.g., "Most of the CX drop comes from batching threshold increase")
- Narrative explanation
- Ranked root causes with:
  - Hypothesis name and category
  - Confidence score (%)
  - Impact score
  - Overall score

**What you can do:**
- Understand why the incident happened
- See which root causes are most likely
- Review evidence for each hypothesis

**Navigation:**
- Click "View Recommendations →" → Goes to Recommendations page
- Click "← Back to Incident" → Returns to incident detail

---

### 4. Recommendations Page (`/recommendations/[id]`)

**What you see:**
- List of actionable recommendations
- For each recommendation:
  - Expected CX impact (points)
  - Expected efficiency impact (%)
  - Confidence level
  - Complexity (low/medium/high)
  - Rollout time estimate
  - Net benefit score
  - Implementation details

**What you can do:**
- Review recommended actions
- Compare tradeoffs (CX vs efficiency)
- Export experiment plan for any recommendation

**Actions:**
- Click "Export Experiment Plan" → Downloads markdown file with experiment plan

**Navigation:**
- Click "← Back to Incident" → Returns to incident detail

---

## Complete User Journey Example

1. **Morning Check-in** → Open Dashboard (`http://localhost:3000`)
   - See: "Active Incidents: 1"
   - See: CX Score dropped from 88.5 to 72.3

2. **Investigate** → Click on incident
   - See: "Grocery SF - CX Score -18"
   - See: Top slice: "Grocery + SF + Dinner (6-8pm)"

3. **Understand Root Cause** → Click "View RCA Report"
   - See: "Batching Threshold Increase" (92% confidence)
   - See: Evidence from SHAP and diff-in-diff

4. **Get Recommendations** → Click "View Recommendations"
   - See: "Reduce Batching Threshold" (+12 CX, -5% efficiency)
   - See: Tradeoff analysis

5. **Take Action** → Click "Export Experiment Plan"
   - Download markdown file
   - Share with team
   - Start experiment

---

## API Integration

The frontend connects to the backend API at `http://localhost:8000`:

- Dashboard fetches: `/api/incidents/` and `/api/metrics/summary`
- Incident detail fetches: `/api/incidents/{id}`
- RCA page fetches: `/api/rca/{id}`
- Recommendations page fetches: `/api/recommendations/{id}`

---

## Troubleshooting

### Frontend won't start
- Check Node.js version: `node --version` (should be 18+)
- Install dependencies: `npm install`
- Check if port 3000 is available

### API connection errors
- Ensure backend is running: `curl http://localhost:8000/health`
- Check CORS settings in backend
- Verify API URL in frontend code

### No data showing
- Backend may not have incidents loaded
- Check browser console for errors
- Verify API endpoints are returning data

---

## Development

### Making Changes

- Frontend code: `frontend/pages/`
- API endpoints: `backend/api/`
- Hot reload: Both frontend and backend support hot reload

### Testing

- Backend: `curl http://localhost:8000/api/incidents/`
- Frontend: Open `http://localhost:3000` in browser
- API docs: `http://localhost:8000/docs`


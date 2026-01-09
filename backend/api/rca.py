"""
RCA API endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from rca.report_generator import RCAReportGenerator
from backend.api.data_loader import get_pipeline

router = APIRouter()

rca_generator = RCAReportGenerator()
detection_pipeline = get_pipeline()


class RCAResponse(BaseModel):
    """RCA report response"""
    incident_id: str
    incident_metric: str
    generated_at: datetime
    hypotheses_tested: int
    ranked_causes: List[dict]
    top_cause: Optional[dict]
    narrative: str
    summary: str


@router.get("/{incident_id}", response_model=RCAResponse)
async def get_rca_report(incident_id: str):
    """Get RCA report for an incident"""
    # Get incident
    incident = detection_pipeline.incident_manager.get_incident(incident_id)
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # For now, return a placeholder RCA report
    # In production, this would load actual data and generate real RCA
    report = {
        'incident_id': incident_id,
        'incident_metric': incident.metric_name,
        'generated_at': datetime.now(),
        'hypotheses_tested': 5,
        'ranked_causes': [
            {
                'rank': 1,
                'hypothesis': {
                    'name': 'Batching Threshold Increase',
                    'category': 'policy'
                },
                'confidence': 0.92,
                'impact': 0.85,
                'score': 0.782
            }
        ],
        'top_cause': {
            'hypothesis': {
                'name': 'Batching Threshold Increase',
                'category': 'policy'
            },
            'confidence': 0.92
        },
        'narrative': 'Root cause analysis identified Batching Threshold Increase as the most likely cause (confidence: 92%).',
        'summary': 'Most of the CX drop comes from batching threshold increase.'
    }
    
    return RCAResponse(**report)


@router.post("/{incident_id}/generate")
async def generate_rca_report(incident_id: str):
    """Generate RCA report for an incident"""
    # This would trigger actual RCA generation
    # For now, return success
    return {
        "message": "RCA report generation started",
        "incident_id": incident_id,
        "status": "processing"
    }


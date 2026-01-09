"""
Incidents API endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from detection.detection_pipeline import DetectionPipeline
from detection.incident_manager import IncidentManager
from backend.api.data_loader import get_pipeline

router = APIRouter()

# Get shared pipeline instance (loads data automatically)
detection_pipeline = get_pipeline()


class IncidentResponse(BaseModel):
    """Incident response model"""
    incident_id: str
    detected_at: datetime
    metric_name: str
    metric_value: float
    baseline_value: Optional[float]
    delta: float
    delta_percent: float
    severity: str
    status: str
    description: Optional[str]


class IncidentDetailResponse(BaseModel):
    """Detailed incident response"""
    incident_id: str
    detected_at: datetime
    metric_name: str
    metric_value: float
    baseline_value: Optional[float]
    delta: float
    delta_percent: float
    severity: str
    status: str
    description: Optional[str]
    top_regressing_slices: List[dict]
    affected_cohorts: Optional[List[dict]] = None
    total_orders_affected: Optional[int] = None
    detection_method: Optional[str] = None


@router.get("/", response_model=List[IncidentResponse])
async def list_incidents(
    status: Optional[str] = Query(None, description="Filter by status"),
    severity: Optional[str] = Query(None, description="Filter by severity"),
    limit: Optional[int] = Query(10, description="Maximum number of incidents")
):
    """List all incidents"""
    incidents = detection_pipeline.get_active_incidents()
    
    # Filter by status
    if status:
        incidents = [i for i in incidents if i.status == status]
    
    # Filter by severity
    if severity:
        incidents = [i for i in incidents if i.severity == severity]
    
    # Limit results
    if limit:
        incidents = incidents[:limit]
    
    return [
        IncidentResponse(
            incident_id=i.incident_id,
            detected_at=i.detected_at,
            metric_name=i.metric_name,
            metric_value=i.metric_value,
            baseline_value=i.baseline_value,
            delta=i.delta,
            delta_percent=i.delta_percent,
            severity=i.severity,
            status=i.status,
            description=i.description
        )
        for i in incidents
    ]


@router.get("/{incident_id}", response_model=IncidentDetailResponse)
async def get_incident(incident_id: str):
    """Get incident details"""
    incident = detection_pipeline.incident_manager.get_incident(incident_id)
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Calculate total orders affected
    total_orders = sum(
        slice.get('order_count', 0) 
        for slice in incident.top_regressing_slices
    ) if incident.top_regressing_slices else 0
    
    return IncidentDetailResponse(
        incident_id=incident.incident_id,
        detected_at=incident.detected_at,
        metric_name=incident.metric_name,
        metric_value=incident.metric_value,
        baseline_value=incident.baseline_value,
        delta=incident.delta,
        delta_percent=incident.delta_percent,
        severity=incident.severity,
        status=incident.status,
        description=incident.description,
        top_regressing_slices=incident.top_regressing_slices,
        affected_cohorts=incident.affected_cohorts,
        total_orders_affected=total_orders if total_orders > 0 else None,
        detection_method="Automated Anomaly Detection (Z-score + EWMA + Bayesian)"
    )


@router.post("/{incident_id}/status")
async def update_incident_status(incident_id: str, status: str):
    """Update incident status"""
    incident = detection_pipeline.incident_manager.get_incident(incident_id)
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    if status not in ['new', 'investigating', 'resolved']:
        raise HTTPException(status_code=400, detail="Invalid status")
    
    detection_pipeline.incident_manager.update_incident_status(incident_id, status)
    
    return {"message": "Status updated", "incident_id": incident_id, "status": status}


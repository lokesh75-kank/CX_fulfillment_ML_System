"""
Incident Manager

Manages incident creation, storage, and ranking.
"""

from typing import List, Dict, Optional
from datetime import datetime
from dataclasses import dataclass, asdict
import uuid
import pandas as pd


@dataclass
class Incident:
    """Incident data structure"""
    incident_id: str
    detected_at: datetime
    metric_name: str
    metric_value: float
    baseline_value: Optional[float]
    delta: float
    delta_percent: float
    severity: str  # 'HIGH', 'MEDIUM', 'LOW'
    status: str  # 'new', 'investigating', 'resolved'
    affected_cohorts: List[Dict]
    top_regressing_slices: List[Dict]
    description: Optional[str] = None


class IncidentManager:
    """Manages incidents: creation, storage, ranking"""
    
    def __init__(self):
        """Initialize incident manager"""
        self.incidents: List[Incident] = []
    
    def create_incident(self, metric_name: str, metric_value: float,
                       baseline_value: Optional[float],
                       detected_at: datetime,
                       affected_cohorts: List[Dict] = None,
                       top_regressing_slices: List[Dict] = None,
                       description: Optional[str] = None) -> Incident:
        """
        Create a new incident
        
        Args:
            metric_name: Name of metric that regressed
            metric_value: Current value of metric
            baseline_value: Baseline/reference value
            detected_at: When incident was detected
            affected_cohorts: List of affected cohorts
            top_regressing_slices: Top regressing slices
            description: Optional description
        
        Returns:
            Created Incident object
        """
        # Calculate delta
        if baseline_value is not None:
            delta = metric_value - baseline_value
            delta_percent = (delta / baseline_value * 100) if baseline_value != 0 else 0
        else:
            delta = 0
            delta_percent = 0
        
        # Determine severity
        severity = self._calculate_severity(delta, delta_percent, metric_name)
        
        # Generate incident ID
        incident_id = f"inc_{uuid.uuid4().hex[:12]}"
        
        incident = Incident(
            incident_id=incident_id,
            detected_at=detected_at,
            metric_name=metric_name,
            metric_value=metric_value,
            baseline_value=baseline_value,
            delta=delta,
            delta_percent=delta_percent,
            severity=severity,
            status='new',
            affected_cohorts=affected_cohorts or [],
            top_regressing_slices=top_regressing_slices or [],
            description=description
        )
        
        self.incidents.append(incident)
        return incident
    
    def _calculate_severity(self, delta: float, delta_percent: float,
                           metric_name: str) -> str:
        """Calculate incident severity"""
        # For CX Score, use absolute delta
        if metric_name == 'cx_score':
            if abs(delta) >= 15:
                return 'HIGH'
            elif abs(delta) >= 8:
                return 'MEDIUM'
            else:
                return 'LOW'
        
        # For rates (on-time, cancellation, etc.), use percentage change
        abs_delta_pct = abs(delta_percent)
        if abs_delta_pct >= 20:
            return 'HIGH'
        elif abs_delta_pct >= 10:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def get_incidents(self, status: Optional[str] = None,
                     severity: Optional[str] = None,
                     limit: Optional[int] = None) -> List[Incident]:
        """
        Get incidents with optional filtering
        
        Args:
            status: Filter by status ('new', 'investigating', 'resolved')
            severity: Filter by severity ('HIGH', 'MEDIUM', 'LOW')
            limit: Maximum number of incidents to return
        
        Returns:
            List of incidents
        """
        incidents = self.incidents
        
        if status:
            incidents = [i for i in incidents if i.status == status]
        
        if severity:
            incidents = [i for i in incidents if i.severity == severity]
        
        # Sort by severity and detected_at (most recent first)
        severity_order = {'HIGH': 3, 'MEDIUM': 2, 'LOW': 1}
        incidents.sort(
            key=lambda x: (severity_order.get(x.severity, 0), x.detected_at),
            reverse=True
        )
        
        if limit:
            incidents = incidents[:limit]
        
        return incidents
    
    def get_incident(self, incident_id: str) -> Optional[Incident]:
        """Get incident by ID"""
        for incident in self.incidents:
            if incident.incident_id == incident_id:
                return incident
        return None
    
    def update_incident_status(self, incident_id: str, status: str):
        """Update incident status"""
        incident = self.get_incident(incident_id)
        if incident:
            incident.status = status
    
    def rank_incidents(self) -> List[Incident]:
        """
        Rank incidents by severity score
        
        Returns:
            List of incidents sorted by severity
        """
        # Calculate severity score for each incident
        for incident in self.incidents:
            incident._severity_score = self._calculate_severity_score(incident)
        
        # Sort by severity score (highest first)
        ranked = sorted(
            self.incidents,
            key=lambda x: getattr(x, '_severity_score', 0),
            reverse=True
        )
        
        return ranked
    
    def _calculate_severity_score(self, incident: Incident) -> float:
        """Calculate numeric severity score for ranking"""
        severity_base = {'HIGH': 100, 'MEDIUM': 50, 'LOW': 10}[incident.severity]
        
        # Add delta magnitude
        delta_score = abs(incident.delta) * 2 if incident.metric_name == 'cx_score' else abs(incident.delta_percent)
        
        # Add recency bonus (more recent = higher score)
        hours_ago = (datetime.now() - incident.detected_at).total_seconds() / 3600
        recency_score = max(0, 10 - hours_ago / 24)  # Decay over 10 days
        
        return severity_base + delta_score + recency_score
    
    def to_dataframe(self) -> pd.DataFrame:
        """Convert incidents to DataFrame"""
        if not self.incidents:
            return pd.DataFrame()
        
        data = [asdict(incident) for incident in self.incidents]
        return pd.DataFrame(data)
    
    def get_active_incidents(self) -> List[Incident]:
        """Get all active (non-resolved) incidents"""
        return self.get_incidents(status=None, severity=None)
    
    def get_incidents_summary(self) -> Dict:
        """Get summary statistics of incidents"""
        total = len(self.incidents)
        by_status = {}
        by_severity = {}
        
        for incident in self.incidents:
            by_status[incident.status] = by_status.get(incident.status, 0) + 1
            by_severity[incident.severity] = by_severity.get(incident.severity, 0) + 1
        
        return {
            'total': total,
            'by_status': by_status,
            'by_severity': by_severity,
            'active': len([i for i in self.incidents if i.status != 'resolved'])
        }


"""
Recommendations API endpoints
"""

from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from recommendations.action_engine import ActionEngine
from recommendations.whatif_simulator import WhatIfSimulator
from recommendations.tradeoff_calculator import TradeoffCalculator
from backend.api.data_loader import get_pipeline

router = APIRouter()

action_engine = ActionEngine()
simulator = WhatIfSimulator()
tradeoff_calc = TradeoffCalculator()
detection_pipeline = get_pipeline()


class RecommendationResponse(BaseModel):
    """Recommendation response"""
    action_id: str
    name: str
    description: str
    target_cause: str
    implementation: str
    complexity: str
    rollout_time: str
    expected_cx_impact: float
    expected_efficiency_impact: float
    confidence: float
    net_benefit: Optional[float] = None
    recommendation: Optional[str] = None


@router.get("/{incident_id}", response_model=List[RecommendationResponse])
async def get_recommendations(incident_id: str):
    """Get recommendations for an incident"""
    # Get incident
    incident = detection_pipeline.incident_manager.get_incident(incident_id)
    
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    
    # Generate recommendations based on incident
    # For now, return sample recommendations
    # In production, this would use actual RCA results
    
    sample_causes = [
        {
            'hypothesis': type('Hypothesis', (), {
                'name': 'Batching Threshold Increase',
                'category': 'policy'
            })(),
            'confidence': 0.92,
            'impact': 0.85
        }
    ]
    
    actions = action_engine.generate_actions(
        sample_causes,
        affected_cohorts=incident.affected_cohorts
    )
    
    # Calculate tradeoffs
    action_dicts = [
        {
            'action_id': a.action_id,
            'name': a.name,
            'expected_cx_impact': a.expected_cx_impact,
            'expected_efficiency_impact': a.expected_efficiency_impact,
            'confidence': a.confidence
        }
        for a in actions
    ]
    
    compared = tradeoff_calc.compare_actions(action_dicts)
    
    # Combine with action details
    recommendations = []
    for action, tradeoff in zip(actions, compared):
        recommendations.append(RecommendationResponse(
            action_id=action.action_id,
            name=action.name,
            description=action.description,
            target_cause=action.target_cause,
            implementation=action.implementation,
            complexity=action.complexity,
            rollout_time=action.rollout_time,
            expected_cx_impact=action.expected_cx_impact,
            expected_efficiency_impact=action.expected_efficiency_impact,
            confidence=action.confidence,
            net_benefit=tradeoff.get('net_benefit'),
            recommendation=tradeoff.get('recommendation')
        ))
    
    return recommendations


@router.post("/{incident_id}/simulate")
async def simulate_recommendation(incident_id: str, action_id: str):
    """Simulate a specific recommendation"""
    # This would run what-if simulation
    return {
        "message": "Simulation completed",
        "incident_id": incident_id,
        "action_id": action_id,
        "cx_impact": 12.0,
        "efficiency_impact": -5.0
    }


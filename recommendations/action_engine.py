"""
Action Engine

Generates actionable recommendations based on root causes.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Action:
    """Action recommendation data structure"""
    action_id: str
    name: str
    description: str
    target_cause: str  # Root cause this addresses
    implementation: str  # How to implement
    complexity: str  # 'low', 'medium', 'high'
    rollout_time: str  # Estimated rollout time
    expected_cx_impact: float  # Expected CX improvement
    expected_efficiency_impact: float  # Expected efficiency impact (can be negative)
    confidence: float  # Confidence in impact estimates (0-1)
    affected_cohorts: List[Dict]  # Cohorts this applies to


class ActionEngine:
    """Generates actionable recommendations"""
    
    def __init__(self):
        """Initialize action engine"""
        self.action_templates = self._create_action_templates()
    
    def _create_action_templates(self) -> Dict[str, Dict]:
        """Create action templates for different root causes"""
        templates = {}
        
        # Batching threshold reduction
        templates['batching_threshold'] = {
            'name': 'Reduce Batching Threshold for Fragile SKUs During Peak Hours',
            'description': 'Reduce batching threshold from current value to 2 for fragile SKUs during peak hours',
            'implementation': 'Policy change: Update batching threshold parameter for specified cohorts',
            'complexity': 'low',
            'rollout_time': '1 day',
            'base_cx_impact': 12.0,  # Base CX score improvement
            'base_efficiency_impact': -5.0,  # Efficiency reduction (%)
            'affected_cohorts_default': ['grocery', 'dinner']
        }
        
        # ETA buffer increase
        templates['eta_buffer'] = {
            'name': 'Increase ETA Buffer for Stores with Prep-Time Drift',
            'description': 'Add buffer time to promised ETA for stores showing prep-time drift',
            'implementation': 'Model update: Add dynamic buffer based on prep-time trends',
            'complexity': 'medium',
            'rollout_time': '2 days',
            'base_cx_impact': 4.0,
            'base_efficiency_impact': 0.0,  # No direct efficiency impact
            'affected_cohorts_default': ['stores_with_drift']
        }
        
        # SKU suppression
        templates['sku_suppression'] = {
            'name': 'Suppress Low-Confidence SKUs from Search/Browse',
            'description': 'Hide SKUs with low in-stock probability from search results',
            'implementation': 'Search filter: Add in_stock_prob threshold to search logic',
            'complexity': 'low',
            'rollout_time': '1 day',
            'base_cx_impact': 2.0,
            'base_efficiency_impact': -3.0,  # Selection coverage reduction
            'affected_cohorts_default': ['all']
        }
        
        # Prep-time model update
        templates['prep_time_model'] = {
            'name': 'Update Prep-Time Model for Affected Stores',
            'description': 'Retrain prep-time prediction model using recent data',
            'implementation': 'Model retraining: Update prep-time model with latest data',
            'complexity': 'medium',
            'rollout_time': '3 days',
            'base_cx_impact': 6.0,
            'base_efficiency_impact': 0.0,
            'affected_cohorts_default': ['affected_stores']
        }
        
        # Dasher assignment optimization
        templates['dasher_assignment'] = {
            'name': 'Optimize Dasher Assignment Algorithm',
            'description': 'Improve dasher assignment to reduce wait times',
            'implementation': 'Algorithm update: Enhance assignment logic',
            'complexity': 'high',
            'rollout_time': '5 days',
            'base_cx_impact': 8.0,
            'base_efficiency_impact': 2.0,  # Positive efficiency impact
            'affected_cohorts_default': ['all']
        }
        
        return templates
    
    def generate_actions(self, root_causes: List[Dict],
                        affected_cohorts: List[Dict] = None) -> List[Action]:
        """
        Generate actions based on root causes
        
        Args:
            root_causes: List of root cause results from RCA
            affected_cohorts: List of affected cohorts
        
        Returns:
            List of Action recommendations
        """
        actions = []
        
        for i, cause in enumerate(root_causes[:3]):  # Top 3 causes
            hypothesis = cause.get('hypothesis')
            if not hypothesis:
                continue
            
            # Map hypothesis to action template
            template_key = self._map_hypothesis_to_action(hypothesis.name)
            
            if template_key and template_key in self.action_templates:
                template = self.action_templates[template_key]
                
                # Calculate expected impact based on cause confidence
                confidence = cause.get('confidence', 0.5)
                impact_multiplier = confidence
                
                action = Action(
                    action_id=f"action_{i+1:03d}",
                    name=template['name'],
                    description=template['description'],
                    target_cause=hypothesis.name,
                    implementation=template['implementation'],
                    complexity=template['complexity'],
                    rollout_time=template['rollout_time'],
                    expected_cx_impact=template['base_cx_impact'] * impact_multiplier,
                    expected_efficiency_impact=template['base_efficiency_impact'],
                    confidence=confidence,
                    affected_cohorts=affected_cohorts or []
                )
                
                actions.append(action)
        
        # Rank actions by expected net benefit
        actions.sort(key=lambda x: x.expected_cx_impact, reverse=True)
        
        return actions
    
    def _map_hypothesis_to_action(self, hypothesis_name: str) -> Optional[str]:
        """Map hypothesis name to action template key"""
        mapping = {
            'Batching Threshold Increase': 'batching_threshold',
            'Merchant Prep-Time Drift': 'eta_buffer',
            'Inventory Availability Degradation': 'sku_suppression',
            'ETA Model Bias': 'prep_time_model',
            'Low Dasher Availability': 'dasher_assignment'
        }
        
        return mapping.get(hypothesis_name)
    
    def get_action_details(self, action: Action) -> Dict:
        """Get detailed information about an action"""
        return {
            'action_id': action.action_id,
            'name': action.name,
            'description': action.description,
            'target_cause': action.target_cause,
            'implementation': action.implementation,
            'complexity': action.complexity,
            'rollout_time': action.rollout_time,
            'expected_cx_impact': action.expected_cx_impact,
            'expected_efficiency_impact': action.expected_efficiency_impact,
            'confidence': action.confidence,
            'affected_cohorts': action.affected_cohorts
        }


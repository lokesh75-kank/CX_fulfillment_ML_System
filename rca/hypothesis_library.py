"""
Hypothesis Library

Defines hypothesis templates for root cause analysis.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Hypothesis:
    """Hypothesis data structure"""
    hypothesis_id: str
    name: str
    category: str  # 'supply', 'merchant', 'policy', 'inventory', 'model'
    description: str
    features_to_check: List[str]  # Features to analyze
    expected_impact: str  # Description of expected impact
    test_methods: List[str]  # Methods to test this hypothesis


class HypothesisLibrary:
    """Library of predefined hypotheses"""
    
    def __init__(self):
        """Initialize hypothesis library"""
        self.hypotheses = self._create_hypotheses()
    
    def _create_hypotheses(self) -> Dict[str, Hypothesis]:
        """Create all hypothesis templates"""
        hypotheses = {}
        
        # Supply-side hypotheses
        hypotheses['low_dasher_availability'] = Hypothesis(
            hypothesis_id='supply_001',
            name='Low Dasher Availability',
            category='supply',
            description='Low dasher availability leads to longer assignment times and lateness',
            features_to_check=['dasher_wait', 'distance', 'actual_eta'],
            expected_impact='Increased dasher_wait times, longer actual_eta, higher lateness',
            test_methods=['shap', 'correlation', 'temporal']
        )
        
        # Merchant-side hypotheses
        hypotheses['prep_time_drift'] = Hypothesis(
            hypothesis_id='merchant_001',
            name='Merchant Prep-Time Drift',
            category='merchant',
            description='Merchant preparation time has increased, causing ETA misses',
            features_to_check=['merchant_prep_time', 'actual_eta', 'promised_eta'],
            expected_impact='Increased merchant_prep_time, actual_eta > promised_eta',
            test_methods=['shap', 'diff_in_diff', 'temporal']
        )
        
        # Policy hypotheses
        hypotheses['batching_threshold_increase'] = Hypothesis(
            hypothesis_id='policy_001',
            name='Batching Threshold Increase',
            category='policy',
            description='Batching threshold was increased, causing longer wait times and lateness',
            features_to_check=['batched_flag', 'dasher_wait', 'actual_eta', 'canceled_flag'],
            expected_impact='Higher batching rate, increased dasher_wait, lateness, cancellations',
            test_methods=['diff_in_diff', 'shap', 'correlation']
        )
        
        # Inventory hypotheses
        hypotheses['inventory_degradation'] = Hypothesis(
            hypothesis_id='inventory_001',
            name='Inventory Availability Degradation',
            category='inventory',
            description='Inventory in-stock probability decreased, causing substitutions and refunds',
            features_to_check=['in_stock_prob', 'substituted_flag', 'missing_flag', 'refund_amount'],
            expected_impact='Lower in_stock_prob, higher substitutions, missing items, refunds',
            test_methods=['shap', 'temporal', 'correlation']
        )
        
        # Model regression hypotheses
        hypotheses['eta_model_bias'] = Hypothesis(
            hypothesis_id='model_001',
            name='ETA Model Bias',
            category='model',
            description='ETA model has systematic bias, causing consistent over/under-estimation',
            features_to_check=['promised_eta', 'actual_eta', 'eta_error'],
            expected_impact='Systematic bias in promised_eta vs actual_eta',
            test_methods=['temporal', 'correlation', 'statistical']
        )
        
        return hypotheses
    
    def get_hypothesis(self, hypothesis_id: str) -> Optional[Hypothesis]:
        """Get hypothesis by ID"""
        return self.hypotheses.get(hypothesis_id)
    
    def get_all_hypotheses(self) -> List[Hypothesis]:
        """Get all hypotheses"""
        return list(self.hypotheses.values())
    
    def get_hypotheses_by_category(self, category: str) -> List[Hypothesis]:
        """Get hypotheses by category"""
        return [h for h in self.hypotheses.values() if h.category == category]
    
    def get_relevant_hypotheses(self, incident_metric: str,
                                affected_cohorts: List[Dict]) -> List[Hypothesis]:
        """
        Get hypotheses relevant to an incident
        
        Args:
            incident_metric: Metric that regressed (e.g., 'cx_score', 'on_time_rate')
            affected_cohorts: List of affected cohorts
        
        Returns:
            List of relevant hypotheses
        """
        relevant = []
        
        # Map metrics to hypothesis categories
        metric_to_categories = {
            'cx_score': ['supply', 'merchant', 'policy', 'inventory', 'model'],
            'on_time_rate': ['supply', 'merchant', 'policy', 'model'],
            'cancellation_rate': ['supply', 'merchant', 'policy'],
            'refund_rate': ['inventory', 'merchant'],
            'item_accuracy': ['inventory', 'merchant']
        }
        
        categories = metric_to_categories.get(incident_metric, [])
        
        for category in categories:
            relevant.extend(self.get_hypotheses_by_category(category))
        
        return relevant


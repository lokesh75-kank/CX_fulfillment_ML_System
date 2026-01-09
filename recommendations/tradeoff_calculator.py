"""
Tradeoff Calculator

Calculates and visualizes tradeoffs between CX improvements and efficiency costs.
"""

from typing import Dict, List, Optional, Tuple
import numpy as np


class TradeoffCalculator:
    """Calculates tradeoffs for recommendations"""
    
    def __init__(self):
        """Initialize tradeoff calculator"""
        pass
    
    def calculate_tradeoff(self, cx_improvement: float,
                          efficiency_impact: float,
                          confidence: float = 1.0) -> Dict:
        """
        Calculate tradeoff metrics
        
        Args:
            cx_improvement: Expected CX score improvement
            efficiency_impact: Expected efficiency impact (%)
            confidence: Confidence in estimates (0-1)
        
        Returns:
            Dict with tradeoff metrics
        """
        # Calculate net benefit (weighted)
        # CX improvement is primary, efficiency is secondary
        cx_weight = 0.7
        efficiency_weight = 0.3
        
        # Normalize efficiency impact (assume -10% to +10% range)
        normalized_efficiency = efficiency_impact / 10.0
        
        # Net benefit score
        net_benefit = (cx_weight * cx_improvement / 100.0) + (efficiency_weight * normalized_efficiency)
        
        # Calculate ROI (simplified)
        # Assume CX improvement translates to business value
        roi = cx_improvement / abs(efficiency_impact) if efficiency_impact != 0 else float('inf')
        
        # Risk-adjusted benefit (accounting for confidence)
        risk_adjusted_benefit = net_benefit * confidence
        
        return {
            'cx_improvement': cx_improvement,
            'efficiency_impact': efficiency_impact,
            'net_benefit': net_benefit,
            'roi': roi,
            'risk_adjusted_benefit': risk_adjusted_benefit,
            'confidence': confidence,
            'recommendation': self._get_recommendation(net_benefit, confidence)
        }
    
    def _get_recommendation(self, net_benefit: float, confidence: float) -> str:
        """Get recommendation based on tradeoff"""
        if net_benefit > 0.1 and confidence > 0.7:
            return 'strong_recommend'
        elif net_benefit > 0.05 and confidence > 0.6:
            return 'recommend'
        elif net_benefit > 0:
            return 'consider'
        else:
            return 'not_recommended'
    
    def compare_actions(self, actions: List[Dict]) -> List[Dict]:
        """
        Compare multiple actions and rank by tradeoff
        
        Args:
            actions: List of action dicts with impact estimates
        
        Returns:
            Ranked list of actions with tradeoff scores
        """
        compared = []
        
        for action in actions:
            tradeoff = self.calculate_tradeoff(
                action.get('expected_cx_impact', 0),
                action.get('expected_efficiency_impact', 0),
                action.get('confidence', 0.5)
            )
            
            compared.append({
                **action,
                **tradeoff
            })
        
        # Sort by risk-adjusted benefit
        compared.sort(key=lambda x: x['risk_adjusted_benefit'], reverse=True)
        
        return compared
    
    def calculate_confidence_interval(self, expected_value: float,
                                     confidence: float,
                                     std_dev: Optional[float] = None) -> Tuple[float, float]:
        """
        Calculate confidence interval for impact estimate
        
        Args:
            expected_value: Expected impact value
            confidence: Confidence level (0-1)
            std_dev: Optional standard deviation
        
        Returns:
            Tuple of (lower_bound, upper_bound)
        """
        if std_dev is None:
            # Assume 20% coefficient of variation
            std_dev = abs(expected_value) * 0.2
        
        # Z-score for confidence level
        z_scores = {
            0.9: 1.645,
            0.95: 1.96,
            0.99: 2.576
        }
        
        z = z_scores.get(confidence, 1.96)
        
        margin = z * std_dev
        
        return (expected_value - margin, expected_value + margin)
    
    def prepare_tradeoff_visualization(self, actions: List[Dict]) -> Dict:
        """
        Prepare data for tradeoff visualization
        
        Returns:
            Dict with data formatted for charts
        """
        chart_data = []
        
        for i, action in enumerate(actions):
            chart_data.append({
                'action_id': action.get('action_id', f'action_{i}'),
                'action_name': action.get('name', 'Unknown'),
                'cx_improvement': action.get('expected_cx_impact', 0),
                'efficiency_impact': action.get('expected_efficiency_impact', 0),
                'confidence': action.get('confidence', 0.5),
                'net_benefit': action.get('net_benefit', 0),
                'recommendation': action.get('recommendation', 'consider')
            })
        
        return {
            'actions': chart_data,
            'axes': {
                'x': 'CX Improvement (points)',
                'y': 'Efficiency Impact (%)'
            },
            'quadrants': {
                'ideal': {'cx': 'high', 'efficiency': 'neutral_or_positive'},
                'acceptable': {'cx': 'high', 'efficiency': 'slightly_negative'},
                'tradeoff': {'cx': 'medium', 'efficiency': 'negative'},
                'not_recommended': {'cx': 'low', 'efficiency': 'negative'}
            }
        }
    
    def calculate_combined_impact(self, actions: List[Dict]) -> Dict:
        """
        Calculate combined impact if multiple actions are implemented
        
        Args:
            actions: List of actions to combine
        
        Returns:
            Dict with combined impact estimates
        """
        # Sum CX improvements (with diminishing returns)
        total_cx_improvement = 0
        for action in actions:
            cx_impact = action.get('expected_cx_impact', 0)
            # Apply diminishing returns (90% of additional impact)
            total_cx_improvement += cx_impact * (0.9 ** len([a for a in actions if actions.index(a) < actions.index(action)]))
        
        # Sum efficiency impacts
        total_efficiency_impact = sum(action.get('expected_efficiency_impact', 0) for action in actions)
        
        # Average confidence
        avg_confidence = np.mean([action.get('confidence', 0.5) for action in actions])
        
        return {
            'combined_cx_improvement': total_cx_improvement,
            'combined_efficiency_impact': total_efficiency_impact,
            'combined_confidence': avg_confidence,
            'num_actions': len(actions)
        }


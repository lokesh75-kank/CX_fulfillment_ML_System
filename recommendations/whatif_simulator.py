"""
What-If Simulator

Simulates counterfactual scenarios to estimate impact of actions.
"""

from typing import Dict, List, Optional
import pandas as pd
import numpy as np
from datetime import datetime

from metrics.cx_metrics import CXMetricsCalculator


class WhatIfSimulator:
    """Simulates what-if scenarios for recommendations"""
    
    def __init__(self):
        """Initialize what-if simulator"""
        self.metrics_calculator = CXMetricsCalculator()
    
    def simulate_batching_reduction(self, orders_df: pd.DataFrame,
                                    deliveries_df: pd.DataFrame,
                                    items_df: pd.DataFrame,
                                    support_df: pd.DataFrame,
                                    ratings_df: pd.DataFrame,
                                    current_batching_rate: float,
                                    new_batching_rate: float,
                                    affected_cohort: Optional[Dict] = None) -> Dict:
        """
        Simulate impact of reducing batching threshold
        
        Args:
            orders_df: Orders DataFrame
            deliveries_df: Deliveries DataFrame
            items_df: Items DataFrame
            support_df: Support events DataFrame
            ratings_df: Ratings DataFrame
            current_batching_rate: Current batching rate (0-1)
            new_batching_rate: New batching rate (0-1)
            affected_cohort: Optional cohort filter
        
        Returns:
            Dict with simulated impact metrics
        """
        # Filter by cohort if specified
        if affected_cohort:
            from metrics.cohort_slicer import CohortSlicer
            slicer = CohortSlicer()
            filtered_orders = slicer.filter_by_cohort(orders_df, affected_cohort)
            order_ids = filtered_orders['order_id'].unique()
            
            deliveries_df = deliveries_df[deliveries_df['order_id'].isin(order_ids)]
            items_df = items_df[items_df['order_id'].isin(order_ids)]
            support_df = support_df[support_df['order_id'].isin(order_ids)]
            ratings_df = ratings_df[ratings_df['order_id'].isin(order_ids)]
            orders_df = filtered_orders
        
        # Calculate current metrics
        current_metrics = self.metrics_calculator.calculate_cx_score(
            orders_df, deliveries_df, items_df, support_df, ratings_df
        )
        
        # Simulate impact
        batching_reduction = current_batching_rate - new_batching_rate
        
        # Estimate impact on metrics
        # Batching reduction → lower dasher_wait → better on-time rate
        # Assume linear relationship for simplicity
        on_time_improvement = batching_reduction * 0.15  # 15% improvement per 10% reduction
        cancellation_reduction = batching_reduction * 0.10  # 10% reduction per 10% batching reduction
        
        # Simulate new metrics
        simulated_metrics = current_metrics.copy()
        simulated_metrics['on_time_rate'] = min(1.0, current_metrics['on_time_rate'] + on_time_improvement)
        simulated_metrics['cancellation_rate'] = max(0.0, current_metrics['cancellation_rate'] - cancellation_reduction)
        
        # Recalculate CX Score
        simulated_metrics['cx_score'] = (
            0.30 * simulated_metrics['on_time_rate'] * 100 +
            0.25 * simulated_metrics['item_accuracy'] * 100 +
            0.15 * (1.0 - simulated_metrics['cancellation_rate']) * 100 +
            0.15 * (1.0 - simulated_metrics['refund_rate']) * 100 +
            0.10 * (1.0 - simulated_metrics['support_rate']) * 100 +
            0.05 * simulated_metrics['rating_proxy'] * 100
        )
        
        # Calculate deltas
        cx_delta = simulated_metrics['cx_score'] - current_metrics['cx_score']
        on_time_delta = simulated_metrics['on_time_rate'] - current_metrics['on_time_rate']
        cancellation_delta = simulated_metrics['cancellation_rate'] - current_metrics['cancellation_rate']
        
        # Efficiency impact (negative: fewer orders per dasher trip)
        efficiency_impact = -batching_reduction * 5.0  # 5% efficiency loss per 10% batching reduction
        
        return {
            'current_metrics': current_metrics,
            'simulated_metrics': simulated_metrics,
            'cx_score_delta': cx_delta,
            'on_time_rate_delta': on_time_delta,
            'cancellation_rate_delta': cancellation_delta,
            'efficiency_impact': efficiency_impact,
            'confidence': 0.85  # High confidence for batching changes
        }
    
    def simulate_eta_buffer(self, orders_df: pd.DataFrame,
                            deliveries_df: pd.DataFrame,
                            items_df: pd.DataFrame,
                            support_df: pd.DataFrame,
                            ratings_df: pd.DataFrame,
                            buffer_minutes: int,
                            affected_cohort: Optional[Dict] = None) -> Dict:
        """
        Simulate impact of adding ETA buffer
        
        Args:
            buffer_minutes: Minutes to add to promised ETA
            affected_cohort: Optional cohort filter
        
        Returns:
            Dict with simulated impact metrics
        """
        # Filter by cohort if specified
        if affected_cohort:
            from metrics.cohort_slicer import CohortSlicer
            slicer = CohortSlicer()
            filtered_orders = slicer.filter_by_cohort(orders_df, affected_cohort)
            order_ids = filtered_orders['order_id'].unique()
            
            deliveries_df = deliveries_df[deliveries_df['order_id'].isin(order_ids)]
            items_df = items_df[items_df['order_id'].isin(order_ids)]
            support_df = support_df[support_df['order_id'].isin(order_ids)]
            ratings_df = ratings_df[ratings_df['order_id'].isin(order_ids)]
            orders_df = filtered_orders
        
        # Calculate current metrics
        current_metrics = self.metrics_calculator.calculate_cx_score(
            orders_df, deliveries_df, items_df, support_df, ratings_df
        )
        
        # Simulate: Adding buffer improves on-time rate
        # But increases customer wait time (negative CX impact)
        buffer_hours = buffer_minutes / 60.0
        
        # On-time improvement (more orders within window)
        on_time_improvement = min(0.1, buffer_hours * 0.05)  # Up to 10% improvement
        
        # Simulate new metrics
        simulated_metrics = current_metrics.copy()
        simulated_metrics['on_time_rate'] = min(1.0, current_metrics['on_time_rate'] + on_time_improvement)
        
        # Recalculate CX Score
        simulated_metrics['cx_score'] = (
            0.30 * simulated_metrics['on_time_rate'] * 100 +
            0.25 * simulated_metrics['item_accuracy'] * 100 +
            0.15 * (1.0 - simulated_metrics['cancellation_rate']) * 100 +
            0.15 * (1.0 - simulated_metrics['refund_rate']) * 100 +
            0.10 * (1.0 - simulated_metrics['support_rate']) * 100 +
            0.05 * simulated_metrics['rating_proxy'] * 100
        )
        
        # Calculate deltas
        cx_delta = simulated_metrics['cx_score'] - current_metrics['cx_score']
        on_time_delta = simulated_metrics['on_time_rate'] - current_metrics['on_time_rate']
        
        # Customer wait time impact (negative)
        wait_time_impact = buffer_minutes  # Average increase in wait time
        
        return {
            'current_metrics': current_metrics,
            'simulated_metrics': simulated_metrics,
            'cx_score_delta': cx_delta,
            'on_time_rate_delta': on_time_delta,
            'wait_time_impact': wait_time_impact,
            'efficiency_impact': 0.0,  # No efficiency impact
            'confidence': 0.75  # Medium confidence
        }
    
    def simulate_sku_suppression(self, orders_df: pd.DataFrame,
                                 deliveries_df: pd.DataFrame,
                                 items_df: pd.DataFrame,
                                 support_df: pd.DataFrame,
                                 ratings_df: pd.DataFrame,
                                 suppression_threshold: float,
                                 affected_cohort: Optional[Dict] = None) -> Dict:
        """
        Simulate impact of suppressing low-confidence SKUs
        
        Args:
            suppression_threshold: In-stock probability threshold (suppress below this)
            affected_cohort: Optional cohort filter
        
        Returns:
            Dict with simulated impact metrics
        """
        # Filter by cohort if specified
        if affected_cohort:
            from metrics.cohort_slicer import CohortSlicer
            slicer = CohortSlicer()
            filtered_orders = slicer.filter_by_cohort(orders_df, affected_cohort)
            order_ids = filtered_orders['order_id'].unique()
            
            deliveries_df = deliveries_df[deliveries_df['order_id'].isin(order_ids)]
            items_df = items_df[items_df['order_id'].isin(order_ids)]
            support_df = support_df[support_df['order_id'].isin(order_ids)]
            ratings_df = ratings_df[ratings_df['order_id'].isin(order_ids)]
            orders_df = filtered_orders
        
        # Calculate current metrics
        current_metrics = self.metrics_calculator.calculate_cx_score(
            orders_df, deliveries_df, items_df, support_df, ratings_df
        )
        
        # Estimate impact: Suppressing low-confidence SKUs reduces substitutions/refunds
        # But also reduces selection coverage
        
        # Assume 20% of items are below threshold
        suppression_rate = 0.2
        
        # Refund reduction
        refund_reduction = suppression_rate * 0.3  # 30% of suppressed items would have refunds
        
        # Simulate new metrics
        simulated_metrics = current_metrics.copy()
        simulated_metrics['refund_rate'] = max(0.0, current_metrics['refund_rate'] - refund_reduction)
        
        # Item accuracy improvement (fewer substitutions)
        item_accuracy_improvement = suppression_rate * 0.1
        simulated_metrics['item_accuracy'] = min(1.0, current_metrics['item_accuracy'] + item_accuracy_improvement)
        
        # Recalculate CX Score
        simulated_metrics['cx_score'] = (
            0.30 * simulated_metrics['on_time_rate'] * 100 +
            0.25 * simulated_metrics['item_accuracy'] * 100 +
            0.15 * (1.0 - simulated_metrics['cancellation_rate']) * 100 +
            0.15 * (1.0 - simulated_metrics['refund_rate']) * 100 +
            0.10 * (1.0 - simulated_metrics['support_rate']) * 100 +
            0.05 * simulated_metrics['rating_proxy'] * 100
        )
        
        # Calculate deltas
        cx_delta = simulated_metrics['cx_score'] - current_metrics['cx_score']
        refund_delta = simulated_metrics['refund_rate'] - current_metrics['refund_rate']
        
        # Selection coverage impact (negative)
        coverage_impact = -suppression_rate * 100  # Percentage reduction in available SKUs
        
        return {
            'current_metrics': current_metrics,
            'simulated_metrics': simulated_metrics,
            'cx_score_delta': cx_delta,
            'refund_rate_delta': refund_delta,
            'item_accuracy_delta': item_accuracy_improvement,
            'coverage_impact': coverage_impact,
            'efficiency_impact': 0.0,  # No direct efficiency impact
            'confidence': 0.70  # Medium confidence
        }
    
    def simulate_action(self, action_name: str,
                       orders_df: pd.DataFrame,
                       deliveries_df: pd.DataFrame,
                       items_df: pd.DataFrame,
                       support_df: pd.DataFrame,
                       ratings_df: pd.DataFrame,
                       action_params: Dict,
                       affected_cohort: Optional[Dict] = None) -> Dict:
        """
        Simulate a specific action
        
        Args:
            action_name: Name of action to simulate
            action_params: Parameters for the action
            affected_cohort: Optional cohort filter
        
        Returns:
            Dict with simulated impact
        """
        if 'batching' in action_name.lower():
            return self.simulate_batching_reduction(
                orders_df, deliveries_df, items_df, support_df, ratings_df,
                action_params.get('current_rate', 0.5),
                action_params.get('new_rate', 0.3),
                affected_cohort
            )
        elif 'eta' in action_name.lower() or 'buffer' in action_name.lower():
            return self.simulate_eta_buffer(
                orders_df, deliveries_df, items_df, support_df, ratings_df,
                action_params.get('buffer_minutes', 5),
                affected_cohort
            )
        elif 'sku' in action_name.lower() or 'suppress' in action_name.lower():
            return self.simulate_sku_suppression(
                orders_df, deliveries_df, items_df, support_df, ratings_df,
                action_params.get('threshold', 0.3),
                affected_cohort
            )
        else:
            return {'error': f'Unknown action: {action_name}'}


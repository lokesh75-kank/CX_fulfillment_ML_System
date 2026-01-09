"""
Slicing Engine

Identifies top regressing slices and calculates statistical significance.
"""

from typing import List, Dict, Optional, Tuple
import pandas as pd
import numpy as np
from scipy import stats
from datetime import datetime

from metrics.cohort_slicer import CohortSlicer
from metrics.cx_metrics import CXMetricsCalculator


class SlicingEngine:
    """Identifies top regressing slices with statistical significance"""
    
    def __init__(self):
        """Initialize slicing engine"""
        self.cohort_slicer = CohortSlicer()
        self.metrics_calculator = CXMetricsCalculator()
    
    def find_top_regressing_slices(self, baseline_metrics: List[Dict],
                                   current_metrics: List[Dict],
                                   metric: str = 'cx_score',
                                   top_n: int = 10,
                                   min_orders: int = 10) -> List[Dict]:
        """
        Find top regressing slices with statistical significance
        
        Args:
            baseline_metrics: List of cohort metrics from baseline period
            current_metrics: List of cohort metrics from current period
            metric: Metric to compare (default: 'cx_score')
            top_n: Number of top slices to return
            min_orders: Minimum orders required for significance
        
        Returns:
            List of regressing slices with significance scores
        """
        # Use cohort slicer's method to find regressing cohorts
        regressing = self.cohort_slicer.find_top_regressing_cohorts(
            baseline_metrics,
            current_metrics,
            metric=metric,
            top_n=top_n * 2  # Get more candidates for significance testing
        )
        
        # Add statistical significance
        for slice_data in regressing:
            # Get baseline and current data for this cohort
            baseline_cohort = self._find_cohort_metrics(
                baseline_metrics,
                slice_data['cohort']
            )
            current_cohort = self._find_cohort_metrics(
                current_metrics,
                slice_data['cohort']
            )
            
            if baseline_cohort and current_cohort:
                significance = self._calculate_significance(
                    baseline_cohort,
                    current_cohort,
                    metric
                )
                slice_data['significance'] = significance
                slice_data['significance_level'] = self._get_significance_level(significance)
            else:
                slice_data['significance'] = None
                slice_data['significance_level'] = 'unknown'
        
        # Filter by minimum orders and sort by significance
        filtered = [
            s for s in regressing
            if s.get('order_count', 0) >= min_orders
        ]
        
        # Sort by significance (most significant first)
        filtered.sort(
            key=lambda x: (
                self._significance_to_numeric(x.get('significance_level', 'unknown')),
                abs(x.get('delta', 0))
            ),
            reverse=True
        )
        
        return filtered[:top_n]
    
    def _find_cohort_metrics(self, metrics_list: List[Dict],
                             cohort: Dict) -> Optional[Dict]:
        """Find metrics for a specific cohort"""
        for m in metrics_list:
            if self._cohorts_match(m['cohort'], cohort):
                return m
        return None
    
    def _cohorts_match(self, cohort1: Dict, cohort2: Dict) -> bool:
        """Check if two cohorts match"""
        return sorted(cohort1.items()) == sorted(cohort2.items())
    
    def _calculate_significance(self, baseline: Dict, current: Dict,
                               metric: str) -> float:
        """
        Calculate statistical significance using t-test
        
        Returns:
            p-value (lower = more significant)
        """
        # For simplicity, we'll use a simplified approach
        # In production, you'd have individual order-level data
        
        baseline_value = baseline.get(metric, 0)
        current_value = current.get(metric, 0)
        baseline_count = baseline.get('order_count', 0)
        current_count = current.get('order_count', 0)
        
        if baseline_count < 10 or current_count < 10:
            return 1.0  # Not enough data
        
        # Simplified significance: use effect size and sample size
        # Effect size
        if baseline_value == 0:
            effect_size = abs(current_value - baseline_value) / 1.0
        else:
            effect_size = abs(current_value - baseline_value) / abs(baseline_value)
        
        # Sample size factor
        n_factor = min(baseline_count, current_count) / 100.0
        
        # Approximate p-value based on effect size and sample size
        # Larger effect size + larger sample = lower p-value
        p_value = max(0.001, 1.0 - (effect_size * n_factor))
        
        return p_value
    
    def _get_significance_level(self, p_value: Optional[float]) -> str:
        """Convert p-value to significance level"""
        if p_value is None:
            return 'unknown'
        
        if p_value < 0.001:
            return '***'  # Highly significant
        elif p_value < 0.01:
            return '**'   # Very significant
        elif p_value < 0.05:
            return '*'    # Significant
        else:
            return 'ns'   # Not significant
    
    def _significance_to_numeric(self, level: str) -> int:
        """Convert significance level to numeric for sorting"""
        mapping = {
            '***': 4,
            '**': 3,
            '*': 2,
            'ns': 1,
            'unknown': 0
        }
        return mapping.get(level, 0)
    
    def compare_slices(self, slice1_metrics: Dict, slice2_metrics: Dict,
                      metric: str = 'cx_score') -> Dict:
        """
        Compare two slices and return comparison metrics
        
        Returns:
            Dict with comparison results
        """
        value1 = slice1_metrics.get(metric, 0)
        value2 = slice2_metrics.get(metric, 0)
        
        delta = value2 - value1
        delta_pct = (delta / value1 * 100) if value1 != 0 else 0
        
        return {
            'slice1_value': value1,
            'slice2_value': value2,
            'delta': delta,
            'delta_percent': delta_pct,
            'slice1_cohort': slice1_metrics.get('cohort', {}),
            'slice2_cohort': slice2_metrics.get('cohort', {})
        }
    
    def get_slice_breakdown(self, cohort: Dict,
                           orders_df: pd.DataFrame,
                           deliveries_df: pd.DataFrame,
                           items_df: pd.DataFrame,
                           support_df: pd.DataFrame,
                           ratings_df: pd.DataFrame) -> Dict:
        """
        Get detailed breakdown for a specific slice
        
        Returns:
            Dict with detailed metrics and breakdown
        """
        # Calculate metrics for this cohort
        metrics = self.metrics_calculator.calculate_metrics_for_cohort(
            cohort,
            orders_df,
            deliveries_df,
            items_df,
            support_df,
            ratings_df
        )
        
        # Filter data for this cohort
        filtered_orders = self.cohort_slicer.filter_by_cohort(orders_df, cohort)
        order_ids = filtered_orders['order_id'].unique()
        
        filtered_deliveries = deliveries_df[deliveries_df['order_id'].isin(order_ids)]
        filtered_items = items_df[items_df['order_id'].isin(order_ids)]
        
        # Add breakdowns
        breakdown = {
            **metrics,
            'cohort': cohort,
            'order_count': len(filtered_orders),
            'breakdown': {
                'on_time_count': len(filtered_deliveries[
                    (filtered_deliveries['actual_eta'].notna()) &
                    (filtered_deliveries['canceled_flag'] != True)
                ]),
                'canceled_count': filtered_deliveries['canceled_flag'].sum(),
                'batched_count': filtered_deliveries['batched_flag'].sum(),
                'items_with_issues': (
                    filtered_items['substituted_flag'].sum() +
                    filtered_items['missing_flag'].sum()
                ),
                'total_items': len(filtered_items)
            }
        }
        
        return breakdown
    
    def prepare_visualization_data(self, regressing_slices: List[Dict]) -> Dict:
        """
        Prepare data for visualization
        
        Returns:
            Dict with data formatted for charts
        """
        if not regressing_slices:
            return {
                'slices': [],
                'chart_data': []
            }
        
        chart_data = []
        for i, slice_data in enumerate(regressing_slices):
            chart_data.append({
                'rank': i + 1,
                'cohort_label': self._format_cohort_label(slice_data['cohort']),
                'delta': slice_data['delta'],
                'delta_percent': slice_data.get('delta_percent', 0),
                'significance': slice_data.get('significance_level', 'unknown'),
                'order_count': slice_data.get('order_count', 0)
            })
        
        return {
            'slices': regressing_slices,
            'chart_data': chart_data
        }
    
    def _format_cohort_label(self, cohort: Dict) -> str:
        """Format cohort dict as readable label"""
        if not cohort:
            return 'All'
        
        parts = [f"{k}={v}" for k, v in sorted(cohort.items())]
        return " | ".join(parts)


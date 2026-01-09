"""
Cohort Slicing Engine

Implements multi-dimensional cohort analysis for CX metrics.
"""

from typing import List, Dict, Optional, Tuple
import pandas as pd
from itertools import product

from .cx_metrics import CXMetricsCalculator


class CohortSlicer:
    """Slices data into cohorts and calculates metrics for each"""
    
    # Available cohort dimensions
    COHORT_DIMENSIONS = [
        'store_id',
        'category',
        'region',
        'time_of_day',
        'basket_size'
    ]
    
    def __init__(self):
        """Initialize cohort slicer"""
        self.metrics_calculator = CXMetricsCalculator()
    
    def get_unique_values(self, orders_df: pd.DataFrame, dimension: str) -> List:
        """Get unique values for a dimension"""
        if dimension not in orders_df.columns:
            return []
        return sorted(orders_df[dimension].unique().tolist())
    
    def get_all_cohorts(self, orders_df: pd.DataFrame,
                       dimensions: Optional[List[str]] = None) -> List[Dict]:
        """
        Get all possible cohort combinations
        
        Args:
            orders_df: Orders DataFrame
            dimensions: List of dimensions to slice by. If None, uses all dimensions.
        
        Returns:
            List of cohort dictionaries
        """
        if dimensions is None:
            dimensions = self.COHORT_DIMENSIONS
        
        # Filter to dimensions that exist in the dataframe
        available_dimensions = [d for d in dimensions if d in orders_df.columns]
        
        if not available_dimensions:
            return [{}]  # Return empty cohort (all data)
        
        # Get unique values for each dimension
        dimension_values = {}
        for dim in available_dimensions:
            dimension_values[dim] = self.get_unique_values(orders_df, dim)
        
        # Generate all combinations
        cohorts = []
        keys = list(dimension_values.keys())
        values = [dimension_values[k] for k in keys]
        
        for combination in product(*values):
            cohort = {keys[i]: combination[i] for i in range(len(keys))}
            cohorts.append(cohort)
        
        return cohorts
    
    def filter_by_cohort(self, df: pd.DataFrame, cohort: Dict) -> pd.DataFrame:
        """Filter DataFrame by cohort criteria"""
        filtered = df.copy()
        
        for key, value in cohort.items():
            if key in filtered.columns:
                filtered = filtered[filtered[key] == value]
        
        return filtered
    
    def calculate_cohort_metrics(self, cohort: Dict,
                                 orders_df: pd.DataFrame,
                                 deliveries_df: pd.DataFrame,
                                 items_df: pd.DataFrame,
                                 support_df: pd.DataFrame,
                                 ratings_df: pd.DataFrame) -> Dict:
        """
        Calculate metrics for a specific cohort
        
        Returns:
            Dict with cohort info and metrics
        """
        metrics = self.metrics_calculator.calculate_metrics_for_cohort(
            cohort,
            orders_df,
            deliveries_df,
            items_df,
            support_df,
            ratings_df
        )
        
        # Add cohort info
        result = {
            'cohort': cohort,
            **metrics
        }
        
        # Add order count
        filtered_orders = self.filter_by_cohort(orders_df, cohort)
        result['order_count'] = len(filtered_orders)
        
        return result
    
    def calculate_all_cohort_metrics(self, orders_df: pd.DataFrame,
                                     deliveries_df: pd.DataFrame,
                                     items_df: pd.DataFrame,
                                     support_df: pd.DataFrame,
                                     ratings_df: pd.DataFrame,
                                     dimensions: Optional[List[str]] = None,
                                     min_orders: int = 10) -> List[Dict]:
        """
        Calculate metrics for all cohorts
        
        Args:
            orders_df: Orders DataFrame
            deliveries_df: Deliveries DataFrame
            items_df: Items DataFrame
            support_df: Support events DataFrame
            ratings_df: Ratings DataFrame
            dimensions: Dimensions to slice by
            min_orders: Minimum orders required for a cohort to be included
        
        Returns:
            List of cohort metrics dictionaries
        """
        cohorts = self.get_all_cohorts(orders_df, dimensions)
        
        results = []
        for cohort in cohorts:
            # Filter orders to check count
            filtered_orders = self.filter_by_cohort(orders_df, cohort)
            
            if len(filtered_orders) < min_orders:
                continue  # Skip cohorts with too few orders
            
            metrics = self.calculate_cohort_metrics(
                cohort,
                orders_df,
                deliveries_df,
                items_df,
                support_df,
                ratings_df
            )
            
            results.append(metrics)
        
        return results
    
    def find_top_regressing_cohorts(self, baseline_metrics: List[Dict],
                                    current_metrics: List[Dict],
                                    metric: str = 'cx_score',
                                    top_n: int = 10) -> List[Dict]:
        """
        Find top regressing cohorts by comparing baseline vs current metrics
        
        Args:
            baseline_metrics: List of cohort metrics from baseline period
            current_metrics: List of cohort metrics from current period
            metric: Metric to compare (default: 'cx_score')
            top_n: Number of top regressing cohorts to return
        
        Returns:
            List of regressing cohorts with delta information
        """
        # Create lookup dictionaries
        baseline_lookup = {}
        for m in baseline_metrics:
            cohort_key = self._cohort_to_key(m['cohort'])
            baseline_lookup[cohort_key] = m
        
        regressing = []
        
        for current in current_metrics:
            cohort_key = self._cohort_to_key(current['cohort'])
            
            if cohort_key not in baseline_lookup:
                continue  # Skip if no baseline data
            
            baseline = baseline_lookup[cohort_key]
            
            # Calculate delta
            baseline_value = baseline.get(metric, 0)
            current_value = current.get(metric, 0)
            delta = current_value - baseline_value
            
            # Only include if regressing (negative delta)
            if delta < 0:
                regressing.append({
                    'cohort': current['cohort'],
                    'baseline_value': baseline_value,
                    'current_value': current_value,
                    'delta': delta,
                    'delta_pct': (delta / baseline_value * 100) if baseline_value > 0 else 0,
                    'order_count': current.get('order_count', 0)
                })
        
        # Sort by delta (most negative first)
        regressing.sort(key=lambda x: x['delta'])
        
        return regressing[:top_n]
    
    def _cohort_to_key(self, cohort: Dict) -> str:
        """Convert cohort dict to string key for lookup"""
        # Sort keys for consistent ordering
        sorted_items = sorted(cohort.items())
        return str(sorted_items)
    
    def get_cohort_summary(self, cohort_metrics: List[Dict]) -> pd.DataFrame:
        """Convert cohort metrics list to summary DataFrame"""
        if not cohort_metrics:
            return pd.DataFrame()
        
        # Flatten cohort dicts
        rows = []
        for m in cohort_metrics:
            row = {}
            # Add cohort dimensions as columns
            for key, value in m['cohort'].items():
                row[key] = value
            # Add metrics
            for key, value in m.items():
                if key != 'cohort':
                    row[key] = value
            rows.append(row)
        
        return pd.DataFrame(rows)
    
    def slice_by_time_window(self, orders_df: pd.DataFrame,
                             start_date: pd.Timestamp,
                             end_date: pd.Timestamp) -> pd.DataFrame:
        """Filter orders by time window"""
        return orders_df[
            (orders_df['order_time'] >= start_date) &
            (orders_df['order_time'] < end_date)
        ]


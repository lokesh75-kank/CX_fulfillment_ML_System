"""
Causal Checks

Implements causal-style analysis methods:
- Diff-in-diff analysis
- Temporal correlation
- Attribution scoring
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from scipy import stats


class CausalChecker:
    """Performs causal-style checks for root cause analysis"""
    
    def __init__(self):
        """Initialize causal checker"""
        pass
    
    def diff_in_diff(self, baseline_before: pd.DataFrame,
                    baseline_after: pd.DataFrame,
                    treatment_before: pd.DataFrame,
                    treatment_after: pd.DataFrame,
                    metric_column: str,
                    treatment_column: str,
                    treatment_value: any) -> Dict:
        """
        Perform difference-in-differences analysis
        
        Args:
            baseline_before: Baseline group before treatment
            baseline_after: Baseline group after treatment
            treatment_before: Treatment group before treatment
            treatment_after: Treatment group after treatment
            metric_column: Column with metric values
            treatment_column: Column indicating treatment
            treatment_value: Value that indicates treatment
        
        Returns:
            Dict with diff-in-diff results
        """
        # Calculate means
        baseline_before_mean = baseline_before[metric_column].mean()
        baseline_after_mean = baseline_after[metric_column].mean()
        treatment_before_mean = treatment_before[metric_column].mean()
        treatment_after_mean = treatment_after[metric_column].mean()
        
        # Calculate differences
        baseline_diff = baseline_after_mean - baseline_before_mean
        treatment_diff = treatment_after_mean - treatment_before_mean
        
        # Diff-in-diff estimate
        did_estimate = treatment_diff - baseline_diff
        
        # Calculate statistical significance (simplified t-test)
        # Pooled standard error
        baseline_before_std = baseline_before[metric_column].std()
        baseline_after_std = baseline_after[metric_column].std()
        treatment_before_std = treatment_before[metric_column].std()
        treatment_after_std = treatment_after[metric_column].std()
        
        n_baseline = len(baseline_before) + len(baseline_after)
        n_treatment = len(treatment_before) + len(treatment_after)
        
        pooled_se = np.sqrt(
            (baseline_before_std**2 / len(baseline_before) +
             baseline_after_std**2 / len(baseline_after) +
             treatment_before_std**2 / len(treatment_before) +
             treatment_after_std**2 / len(treatment_after)) / 4
        )
        
        if pooled_se > 0:
            t_stat = did_estimate / pooled_se
            # Approximate p-value (two-tailed)
            p_value = 2 * (1 - stats.norm.cdf(abs(t_stat)))
        else:
            t_stat = 0
            p_value = 1.0
        
        return {
            'did_estimate': did_estimate,
            'baseline_diff': baseline_diff,
            'treatment_diff': treatment_diff,
            'baseline_before_mean': baseline_before_mean,
            'baseline_after_mean': baseline_after_mean,
            'treatment_before_mean': treatment_before_mean,
            'treatment_after_mean': treatment_after_mean,
            't_statistic': t_stat,
            'p_value': p_value,
            'significant': p_value < 0.05
        }
    
    def check_policy_change(self, orders_df: pd.DataFrame,
                           deliveries_df: pd.DataFrame,
                           policy_change_date: datetime,
                           policy_column: str,
                           policy_value_before: any,
                           policy_value_after: any,
                           metric_column: str,
                           window_days: int = 7) -> Dict:
        """
        Check impact of policy change using diff-in-diff
        
        Args:
            orders_df: Orders DataFrame
            deliveries_df: Deliveries DataFrame
            policy_change_date: Date of policy change
            policy_column: Column indicating policy (e.g., 'batched_flag')
            policy_value_before: Policy value before change
            policy_value_after: Policy value after change
            metric_column: Metric to analyze
            window_days: Days before/after to analyze
        
        Returns:
            Diff-in-diff results
        """
        # Define time windows
        before_start = policy_change_date - timedelta(days=window_days)
        before_end = policy_change_date
        after_start = policy_change_date
        after_end = policy_change_date + timedelta(days=window_days)
        
        # Filter by time
        orders_before = orders_df[
            (orders_df['order_time'] >= before_start) &
            (orders_df['order_time'] < before_end)
        ]
        orders_after = orders_df[
            (orders_df['order_time'] >= after_start) &
            (orders_df['order_time'] < after_end)
        ]
        
        # Merge with deliveries
        merged_before = orders_before.merge(deliveries_df, on='order_id', how='left')
        merged_after = orders_after.merge(deliveries_df, on='order_id', how='left')
        
        # Split by treatment (policy value)
        baseline_before = merged_before[merged_before[policy_column] == policy_value_before]
        treatment_before = merged_before[merged_before[policy_column] == policy_value_after]
        
        baseline_after = merged_after[merged_after[policy_column] == policy_value_before]
        treatment_after = merged_after[merged_after[policy_column] == policy_value_after]
        
        # Filter out NaN values
        baseline_before = baseline_before[baseline_before[metric_column].notna()]
        baseline_after = baseline_after[baseline_after[metric_column].notna()]
        treatment_before = treatment_before[treatment_before[metric_column].notna()]
        treatment_after = treatment_after[treatment_after[metric_column].notna()]
        
        if len(baseline_before) == 0 or len(baseline_after) == 0:
            return {'error': 'Insufficient baseline data'}
        
        if len(treatment_before) == 0 or len(treatment_after) == 0:
            return {'error': 'Insufficient treatment data'}
        
        # Perform diff-in-diff
        return self.diff_in_diff(
            baseline_before,
            baseline_after,
            treatment_before,
            treatment_after,
            metric_column,
            policy_column,
            policy_value_after
        )
    
    def temporal_correlation(self, time_series: pd.DataFrame,
                            feature_column: str,
                            target_column: str,
                            lag_days: int = 1) -> Dict:
        """
        Calculate temporal correlation between feature and target
        
        Args:
            time_series: DataFrame with time series data
            feature_column: Feature column name
            target_column: Target column name
            lag_days: Number of days to lag feature
        
        Returns:
            Dict with correlation results
        """
        # Sort by time
        time_col = 'order_time' if 'order_time' in time_series.columns else time_series.columns[0]
        time_series = time_series.sort_values(time_col)
        
        # Create lagged feature
        time_series[f'{feature_column}_lagged'] = time_series[feature_column].shift(lag_days)
        
        # Remove NaN
        clean = time_series[[f'{feature_column}_lagged', target_column]].dropna()
        
        if len(clean) < 10:
            return {'correlation': 0, 'p_value': 1.0, 'significant': False}
        
        # Calculate correlation
        correlation, p_value = stats.pearsonr(
            clean[f'{feature_column}_lagged'],
            clean[target_column]
        )
        
        return {
            'correlation': correlation,
            'p_value': p_value,
            'significant': p_value < 0.05,
            'lag_days': lag_days
        }
    
    def calculate_attribution_score(self, feature_importance: Dict[str, float],
                                   feature_values_before: Dict[str, float],
                                   feature_values_after: Dict[str, float]) -> Dict[str, float]:
        """
        Calculate attribution score for each feature
        
        Args:
            feature_importance: Dict of feature importance (from SHAP)
            feature_values_before: Dict of feature values before change
            feature_values_after: Dict of feature values after change
        
        Returns:
            Dict of attribution scores
        """
        attribution = {}
        
        for feature, importance in feature_importance.items():
            if feature in feature_values_before and feature in feature_values_after:
                change = abs(feature_values_after[feature] - feature_values_before[feature])
                attribution[feature] = importance * change
        
        # Normalize
        total = sum(attribution.values())
        if total > 0:
            attribution = {k: v / total for k, v in attribution.items()}
        
        return attribution
    
    def calculate_confidence_score(self, shap_importance: Dict[str, float],
                                   did_result: Optional[Dict],
                                   correlation_result: Optional[Dict]) -> float:
        """
        Calculate overall confidence score for a hypothesis
        
        Args:
            shap_importance: SHAP feature importance
            did_result: Diff-in-diff result
            correlation_result: Temporal correlation result
        
        Returns:
            Confidence score (0-1)
        """
        confidence = 0.0
        
        # SHAP evidence (40% weight)
        if shap_importance:
            # Check if relevant features have high importance
            max_importance = max(shap_importance.values()) if shap_importance else 0
            confidence += 0.4 * min(1.0, max_importance * 2)  # Scale to 0-1
        
        # Diff-in-diff evidence (40% weight)
        if did_result and 'significant' in did_result:
            if did_result['significant']:
                confidence += 0.4
            else:
                confidence += 0.2  # Partial credit if not significant
        
        # Temporal correlation evidence (20% weight)
        if correlation_result and 'significant' in correlation_result:
            if correlation_result['significant']:
                confidence += 0.2
        
        return min(1.0, confidence)


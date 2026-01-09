"""
RCA Report Generator

Generates root cause analysis reports with ranked hypotheses,
evidence, and narrative explanations.
"""

from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd

from .hypothesis_library import HypothesisLibrary, Hypothesis
from .shap_analyzer import SHAPAnalyzer
from .causal_checks import CausalChecker
from metrics.cohort_slicer import CohortSlicer
from metrics.cx_metrics import CXMetricsCalculator


class RCAReportGenerator:
    """Generates comprehensive RCA reports"""
    
    def __init__(self):
        """Initialize RCA report generator"""
        self.hypothesis_lib = HypothesisLibrary()
        self.shap_analyzer = SHAPAnalyzer()
        self.causal_checker = CausalChecker()
        self.cohort_slicer = CohortSlicer()
        self.metrics_calculator = CXMetricsCalculator()
    
    def generate_rca_report(self, incident_id: str,
                           incident_metric: str,
                           baseline_orders: pd.DataFrame,
                           baseline_deliveries: pd.DataFrame,
                           baseline_items: pd.DataFrame,
                           current_orders: pd.DataFrame,
                           current_deliveries: pd.DataFrame,
                           current_items: pd.DataFrame,
                           support_df: pd.DataFrame,
                           ratings_df: pd.DataFrame,
                           policy_change_date: Optional[datetime] = None) -> Dict:
        """
        Generate complete RCA report for an incident
        
        Args:
            incident_id: Incident ID
            incident_metric: Metric that regressed
            baseline_orders: Orders from baseline period
            baseline_deliveries: Deliveries from baseline period
            baseline_items: Items from baseline period
            current_orders: Orders from current period
            current_deliveries: Deliveries from current period
            current_items: Items from current period
            support_df: Support events DataFrame
            ratings_df: Ratings DataFrame
            policy_change_date: Optional policy change date for diff-in-diff
        
        Returns:
            Complete RCA report dict
        """
        # Get relevant hypotheses
        relevant_hypotheses = self.hypothesis_lib.get_relevant_hypotheses(
            incident_metric,
            []
        )
        
        # Test each hypothesis
        hypothesis_results = []
        
        for hypothesis in relevant_hypotheses:
            result = self._test_hypothesis(
                hypothesis,
                incident_metric,
                baseline_orders,
                baseline_deliveries,
                baseline_items,
                current_orders,
                current_deliveries,
                current_items,
                support_df,
                ratings_df,
                policy_change_date
            )
            hypothesis_results.append(result)
        
        # Rank hypotheses by confidence × impact
        ranked_hypotheses = self._rank_hypotheses(hypothesis_results)
        
        # Generate narrative
        narrative = self._generate_narrative(ranked_hypotheses, incident_metric)
        
        # Build report
        report = {
            'incident_id': incident_id,
            'incident_metric': incident_metric,
            'generated_at': datetime.now(),
            'hypotheses_tested': len(hypothesis_results),
            'ranked_causes': ranked_hypotheses,
            'top_cause': ranked_hypotheses[0] if ranked_hypotheses else None,
            'narrative': narrative,
            'summary': self._generate_summary(ranked_hypotheses)
        }
        
        return report
    
    def _test_hypothesis(self, hypothesis: Hypothesis,
                        incident_metric: str,
                        baseline_orders: pd.DataFrame,
                        baseline_deliveries: pd.DataFrame,
                        baseline_items: pd.DataFrame,
                        current_orders: pd.DataFrame,
                        current_deliveries: pd.DataFrame,
                        current_items: pd.DataFrame,
                        support_df: pd.DataFrame,
                        ratings_df: pd.DataFrame,
                        policy_change_date: Optional[datetime]) -> Dict:
        """Test a single hypothesis"""
        result = {
            'hypothesis': hypothesis,
            'evidence': {},
            'confidence': 0.0,
            'impact': 0.0,
            'score': 0.0
        }
        
        # Map incident metric to outcome column
        outcome_map = {
            'cx_score': 'is_late',
            'on_time_rate': 'is_late',
            'cancellation_rate': 'canceled_flag',
            'refund_rate': 'has_refund'
        }
        
        outcome_column = outcome_map.get(incident_metric, 'is_late')
        
        # Create outcome variables
        baseline_deliveries = baseline_deliveries.copy()
        current_deliveries = current_deliveries.copy()
        
        if outcome_column == 'is_late':
            baseline_deliveries['is_late'] = self._calculate_late_flag(
                baseline_orders, baseline_deliveries
            )
            current_deliveries['is_late'] = self._calculate_late_flag(
                current_orders, current_deliveries
            )
        elif outcome_column == 'has_refund':
            baseline_items = baseline_items.copy()
            current_items = current_items.copy()
            baseline_deliveries['has_refund'] = baseline_items.groupby('order_id')['refund_amount'].sum() > 0
            current_deliveries['has_refund'] = current_items.groupby('order_id')['refund_amount'].sum() > 0
        
        # SHAP analysis
        shap_importance = {}
        try:
            shap_importance = self.shap_analyzer.get_feature_importance(
                current_orders,
                current_deliveries,
                current_items,
                outcome_column,
                f"{hypothesis.hypothesis_id}_{outcome_column}"
            )
            result['evidence']['shap'] = shap_importance
        except Exception as e:
            result['evidence']['shap_error'] = str(e)
        
        # Diff-in-diff (if policy change date provided)
        did_result = None
        if policy_change_date and 'batched_flag' in baseline_deliveries.columns:
            try:
                did_result = self.causal_checker.check_policy_change(
                    pd.concat([baseline_orders, current_orders]),
                    pd.concat([baseline_deliveries, current_deliveries]),
                    policy_change_date,
                    'batched_flag',
                    False,
                    True,
                    outcome_column if outcome_column in current_deliveries.columns else 'dasher_wait'
                )
                result['evidence']['diff_in_diff'] = did_result
            except Exception as e:
                result['evidence']['did_error'] = str(e)
        
        # Temporal correlation
        correlation_result = None
        if 'merchant_prep_time' in baseline_deliveries.columns:
            try:
                merged = pd.concat([
                    baseline_orders.merge(baseline_deliveries, on='order_id'),
                    current_orders.merge(current_deliveries, on='order_id')
                ])
                correlation_result = self.causal_checker.temporal_correlation(
                    merged,
                    'merchant_prep_time',
                    outcome_column if outcome_column in merged.columns else 'dasher_wait'
                )
                result['evidence']['temporal_correlation'] = correlation_result
            except Exception as e:
                result['evidence']['correlation_error'] = str(e)
        
        # Calculate confidence
        result['confidence'] = self.causal_checker.calculate_confidence_score(
            shap_importance,
            did_result,
            correlation_result
        )
        
        # Calculate impact (simplified: based on feature importance)
        if shap_importance:
            # Get top feature importance
            top_feature = max(shap_importance.items(), key=lambda x: x[1])[0]
            result['impact'] = shap_importance.get(top_feature, 0)
        else:
            result['impact'] = 0.5  # Default
        
        # Calculate score (confidence × impact)
        result['score'] = result['confidence'] * result['impact']
        
        return result
    
    def _calculate_late_flag(self, orders_df: pd.DataFrame,
                            deliveries_df: pd.DataFrame) -> pd.Series:
        """Calculate if orders are late"""
        merged = orders_df.merge(deliveries_df, on='order_id', how='left')
        merged = merged[merged['actual_eta'].notna()]
        
        if len(merged) == 0:
            return pd.Series([False] * len(deliveries_df), index=deliveries_df.index)
        
        # Check if actual_eta is more than 5 minutes after promised_eta
        threshold = pd.Timedelta(minutes=5)
        is_late = (merged['actual_eta'] - merged['promised_eta']) > threshold
        
        # Map back to deliveries index
        late_series = pd.Series(False, index=deliveries_df.index)
        late_series.loc[merged.index] = is_late.values
        
        return late_series
    
    def _rank_hypotheses(self, hypothesis_results: List[Dict]) -> List[Dict]:
        """Rank hypotheses by score (confidence × impact)"""
        # Sort by score descending
        ranked = sorted(hypothesis_results, key=lambda x: x['score'], reverse=True)
        
        # Add rank
        for i, result in enumerate(ranked):
            result['rank'] = i + 1
        
        return ranked
    
    def _generate_narrative(self, ranked_hypotheses: List[Dict],
                           incident_metric: str) -> str:
        """Generate narrative explanation"""
        if not ranked_hypotheses:
            return "No hypotheses could be tested."
        
        top_cause = ranked_hypotheses[0]
        hypothesis = top_cause['hypothesis']
        
        narrative = f"Root cause analysis identified {hypothesis.name} as the most likely cause "
        narrative += f"(confidence: {top_cause['confidence']:.0%}). "
        
        # Add evidence
        if 'shap' in top_cause['evidence']:
            shap_data = top_cause['evidence']['shap']
            if shap_data:
                top_feature = max(shap_data.items(), key=lambda x: x[1])[0]
                narrative += f"SHAP analysis shows {top_feature} is the top driver. "
        
        if 'diff_in_diff' in top_cause['evidence']:
            did = top_cause['evidence']['diff_in_diff']
            if did.get('significant', False):
                narrative += f"Diff-in-diff analysis confirms significant impact (p={did.get('p_value', 0):.3f}). "
        
        # Add secondary causes
        if len(ranked_hypotheses) > 1:
            secondary = ranked_hypotheses[1]
            if secondary['confidence'] > 0.5:
                narrative += f"{secondary['hypothesis'].name} is a secondary factor "
                narrative += f"(confidence: {secondary['confidence']:.0%}). "
        
        return narrative
    
    def _generate_summary(self, ranked_hypotheses: List[Dict]) -> str:
        """Generate summary statement"""
        if not ranked_hypotheses:
            return "No root causes identified."
        
        top_cause = ranked_hypotheses[0]
        hypothesis = top_cause['hypothesis']
        
        summary = f"Most of the CX drop comes from {hypothesis.name.lower()}"
        
        if len(ranked_hypotheses) > 1:
            secondary = ranked_hypotheses[1]
            if secondary['confidence'] > 0.5:
                summary += f" and {secondary['hypothesis'].name.lower()}"
        
        summary += "."
        
        return summary
    
    def format_report(self, report: Dict) -> str:
        """Format report as readable text"""
        lines = []
        lines.append("=" * 60)
        lines.append("ROOT CAUSE ANALYSIS REPORT")
        lines.append("=" * 60)
        lines.append(f"Incident ID: {report['incident_id']}")
        lines.append(f"Metric: {report['incident_metric']}")
        lines.append(f"Generated: {report['generated_at']}")
        lines.append("")
        
        lines.append("SUMMARY")
        lines.append("-" * 60)
        lines.append(report['summary'])
        lines.append("")
        
        lines.append("NARRATIVE")
        lines.append("-" * 60)
        lines.append(report['narrative'])
        lines.append("")
        
        lines.append("RANKED CAUSES")
        lines.append("-" * 60)
        for i, cause in enumerate(report['ranked_causes'][:5], 1):
            hypothesis = cause['hypothesis']
            lines.append(f"{i}. {hypothesis.name}")
            lines.append(f"   Category: {hypothesis.category}")
            lines.append(f"   Confidence: {cause['confidence']:.0%}")
            lines.append(f"   Impact: {cause['impact']:.2f}")
            lines.append(f"   Score: {cause['score']:.3f}")
            lines.append("")
        
        return "\n".join(lines)


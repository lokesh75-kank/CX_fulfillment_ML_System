"""
Detection Pipeline

Main pipeline that orchestrates anomaly detection, incident creation,
and slice identification.
"""

from typing import List, Dict, Optional
from datetime import datetime, timedelta
import pandas as pd

from detection.anomaly_detector import AnomalyDetector
from detection.incident_manager import IncidentManager
from detection.slicing_engine import SlicingEngine
from metrics.cohort_slicer import CohortSlicer
from metrics.cx_metrics import CXMetricsCalculator


class DetectionPipeline:
    """Main detection pipeline"""
    
    def __init__(self):
        """Initialize detection pipeline"""
        self.anomaly_detector = AnomalyDetector()
        self.incident_manager = IncidentManager()
        self.slicing_engine = SlicingEngine()
        self.cohort_slicer = CohortSlicer()
        self.metrics_calculator = CXMetricsCalculator()
    
    def detect_incidents(self, orders_df: pd.DataFrame,
                        deliveries_df: pd.DataFrame,
                        items_df: pd.DataFrame,
                        support_df: pd.DataFrame,
                        ratings_df: pd.DataFrame,
                        baseline_start: datetime,
                        baseline_end: datetime,
                        current_start: datetime,
                        current_end: datetime,
                        metrics_to_check: List[str] = None) -> List:
        """
        Main detection function: detects incidents and creates incident records
        
        Args:
            orders_df: Orders DataFrame
            deliveries_df: Deliveries DataFrame
            items_df: Items DataFrame
            support_df: Support events DataFrame
            ratings_df: Ratings DataFrame
            baseline_start: Start of baseline period
            baseline_end: End of baseline period
            current_start: Start of current period
            current_end: End of current period
            metrics_to_check: List of metrics to check (default: ['cx_score', 'on_time_rate'])
        
        Returns:
            List of created incidents
        """
        if metrics_to_check is None:
            metrics_to_check = ['cx_score', 'on_time_rate', 'cancellation_rate']
        
        # Filter data by time periods
        baseline_orders = self.cohort_slicer.slice_by_time_window(
            orders_df, baseline_start, baseline_end
        )
        current_orders = self.cohort_slicer.slice_by_time_window(
            orders_df, current_start, current_end
        )
        
        # Get order IDs for each period
        baseline_order_ids = baseline_orders['order_id'].unique()
        current_order_ids = current_orders['order_id'].unique()
        
        baseline_deliveries = deliveries_df[deliveries_df['order_id'].isin(baseline_order_ids)]
        current_deliveries = deliveries_df[deliveries_df['order_id'].isin(current_order_ids)]
        
        baseline_items = items_df[items_df['order_id'].isin(baseline_order_ids)]
        current_items = items_df[items_df['order_id'].isin(current_order_ids)]
        
        baseline_support = support_df[support_df['order_id'].isin(baseline_order_ids)]
        current_support = support_df[support_df['order_id'].isin(current_order_ids)]
        
        baseline_ratings = ratings_df[ratings_df['order_id'].isin(baseline_order_ids)]
        current_ratings = ratings_df[ratings_df['order_id'].isin(current_order_ids)]
        
        # Calculate metrics for baseline and current periods
        baseline_metrics = self.metrics_calculator.calculate_cx_score(
            baseline_orders, baseline_deliveries, baseline_items,
            baseline_support, baseline_ratings
        )
        
        current_metrics = self.metrics_calculator.calculate_cx_score(
            current_orders, current_deliveries, current_items,
            current_support, current_ratings
        )
        
        # Detect incidents for each metric
        incidents = []
        
        for metric_name in metrics_to_check:
            baseline_value = baseline_metrics.get(metric_name)
            current_value = current_metrics.get(metric_name)
            
            if baseline_value is None or current_value is None:
                continue
            
            # Check if there's a significant change
            delta = current_value - baseline_value
            
            # For CX Score, check absolute delta
            if metric_name == 'cx_score':
                if abs(delta) < 5:  # Threshold for CX Score
                    continue
            else:
                # For rates, check percentage change
                delta_pct = abs((delta / baseline_value * 100)) if baseline_value != 0 else 0
                if delta_pct < 5:  # 5% threshold
                    continue
            
            # Calculate cohort metrics for both periods
            baseline_cohort_metrics = self.cohort_slicer.calculate_all_cohort_metrics(
                baseline_orders, baseline_deliveries, baseline_items,
                baseline_support, baseline_ratings,
                min_orders=10
            )
            
            current_cohort_metrics = self.cohort_slicer.calculate_all_cohort_metrics(
                current_orders, current_deliveries, current_items,
                current_support, current_ratings,
                min_orders=10
            )
            
            # Find top regressing slices
            top_slices = self.slicing_engine.find_top_regressing_slices(
                baseline_cohort_metrics,
                current_cohort_metrics,
                metric=metric_name,
                top_n=5
            )
            
            # Create incident
            incident = self.incident_manager.create_incident(
                metric_name=metric_name,
                metric_value=current_value,
                baseline_value=baseline_value,
                detected_at=datetime.now(),
                top_regressing_slices=top_slices,
                description=f"{metric_name} regressed from {baseline_value:.2f} to {current_value:.2f}"
            )
            
            incidents.append(incident)
        
        return incidents
    
    def get_active_incidents(self) -> List:
        """Get all active incidents"""
        return self.incident_manager.get_active_incidents()
    
    def get_incident_details(self, incident_id: str) -> Optional[Dict]:
        """Get detailed information about an incident"""
        incident = self.incident_manager.get_incident(incident_id)
        if not incident:
            return None
        
        return {
            'incident_id': incident.incident_id,
            'detected_at': incident.detected_at,
            'metric_name': incident.metric_name,
            'metric_value': incident.metric_value,
            'baseline_value': incident.baseline_value,
            'delta': incident.delta,
            'delta_percent': incident.delta_percent,
            'severity': incident.severity,
            'status': incident.status,
            'description': incident.description,
            'top_regressing_slices': incident.top_regressing_slices
        }


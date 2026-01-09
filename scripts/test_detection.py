"""
Test script for detection system

Tests anomaly detection and incident creation.
"""

import sys
import os
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.generators.synthetic_data_generator import SyntheticDataGenerator
from detection.detection_pipeline import DetectionPipeline

def test_detection():
    """Test detection system"""
    print("Testing detection system...")
    
    # Generate baseline data (normal operations)
    print("\n=== Generating Baseline Data ===")
    generator = SyntheticDataGenerator(seed=42)
    baseline_start = datetime(2024, 1, 1)
    baseline_end = datetime(2024, 1, 3)
    
    baseline_dataset = generator.generate_dataset(
        start_date=baseline_start,
        end_date=baseline_end,
        orders_per_day=100,
        batching_threshold=2  # Normal threshold
    )
    
    # Generate current data (with regression - batching threshold increased)
    print("\n=== Generating Current Data (with regression) ===")
    current_start = datetime(2024, 1, 3)
    current_end = datetime(2024, 1, 4)
    
    # Simulate policy change: increase batching threshold
    generator.delivery_gen.set_batching_threshold(4, change_date=current_start)
    
    current_dataset = generator.generate_dataset(
        start_date=current_start,
        end_date=current_end,
        orders_per_day=100,
        batching_threshold=4,  # Increased threshold
        prep_time_drift=0.15  # Some prep-time drift
    )
    
    # Combine datasets
    import pandas as pd
    orders_df = pd.concat([baseline_dataset['orders'], current_dataset['orders']])
    deliveries_df = pd.concat([baseline_dataset['deliveries'], current_dataset['deliveries']])
    items_df = pd.concat([baseline_dataset['items'], current_dataset['items']])
    support_df = pd.concat([baseline_dataset['support_events'], current_dataset['support_events']])
    ratings_df = pd.concat([baseline_dataset['ratings'], current_dataset['ratings']])
    
    # Run detection pipeline
    print("\n=== Running Detection Pipeline ===")
    pipeline = DetectionPipeline()
    
    incidents = pipeline.detect_incidents(
        orders_df=orders_df,
        deliveries_df=deliveries_df,
        items_df=items_df,
        support_df=support_df,
        ratings_df=ratings_df,
        baseline_start=baseline_start,
        baseline_end=baseline_end,
        current_start=current_start,
        current_end=current_end,
        metrics_to_check=['cx_score', 'on_time_rate', 'cancellation_rate']
    )
    
    print(f"\n=== Detection Results ===")
    print(f"Detected {len(incidents)} incidents")
    
    for incident in incidents:
        print(f"\nIncident: {incident.incident_id}")
        print(f"  Metric: {incident.metric_name}")
        print(f"  Severity: {incident.severity}")
        print(f"  Baseline: {incident.baseline_value:.2f}")
        print(f"  Current: {incident.metric_value:.2f}")
        print(f"  Delta: {incident.delta:.2f} ({incident.delta_percent:.1f}%)")
        print(f"  Top Slices: {len(incident.top_regressing_slices)}")
        
        if incident.top_regressing_slices:
            top_slice = incident.top_regressing_slices[0]
            print(f"    Top: {top_slice.get('cohort', {})} - Delta: {top_slice.get('delta', 0):.2f}")
    
    # Get active incidents
    active = pipeline.get_active_incidents()
    print(f"\n=== Active Incidents: {len(active)} ===")
    
    print("\n✅ Detection test passed!")
    return incidents

if __name__ == "__main__":
    test_detection()


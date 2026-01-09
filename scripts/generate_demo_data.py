"""
Generate Demo Data Script

Generates the demo scenario data and populates incidents for the UI.
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.generators.synthetic_data_generator import SyntheticDataGenerator
from detection.detection_pipeline import DetectionPipeline
import pandas as pd

def generate_demo_data():
    """Generate demo scenario data"""
    print("=" * 60)
    print("Generating Demo Scenario Data")
    print("=" * 60)
    
    # Initialize generator
    generator = SyntheticDataGenerator(seed=42)
    
    # Baseline period (Jan 1-2): Normal operations
    print("\n1. Generating baseline data (Jan 1-2)...")
    baseline_start = datetime(2024, 1, 1)
    baseline_end = datetime(2024, 1, 3)
    
    baseline_dataset = generator.generate_dataset(
        start_date=baseline_start,
        end_date=baseline_end,
        orders_per_day=1000,
        batching_threshold=2  # Normal threshold
    )
    
    print(f"   Generated {len(baseline_dataset['orders'])} orders")
    
    # Current period (Jan 3-4): With regression
    print("\n2. Generating current data with regression (Jan 3-4)...")
    current_start = datetime(2024, 1, 3)
    current_end = datetime(2024, 1, 5)
    
    # Simulate policy change: increase batching threshold
    generator.delivery_gen.set_batching_threshold(4, change_date=current_start)
    
    current_dataset = generator.generate_dataset(
        start_date=current_start,
        end_date=current_end,
        orders_per_day=1000,
        batching_threshold=4,  # Increased threshold
        prep_time_drift=0.15  # Some prep-time drift
    )
    
    print(f"   Generated {len(current_dataset['orders'])} orders")
    
    # Combine datasets
    print("\n3. Combining datasets...")
    orders_df = pd.concat([baseline_dataset['orders'], current_dataset['orders']])
    deliveries_df = pd.concat([baseline_dataset['deliveries'], current_dataset['deliveries']])
    items_df = pd.concat([baseline_dataset['items'], current_dataset['items']])
    support_df = pd.concat([baseline_dataset['support_events'], current_dataset['support_events']])
    ratings_df = pd.concat([baseline_dataset['ratings'], current_dataset['ratings']])
    
    print(f"   Total orders: {len(orders_df)}")
    print(f"   Total deliveries: {len(deliveries_df)}")
    
    # Save to data/raw for persistence
    print("\n4. Saving data to data/raw/...")
    os.makedirs('data/raw', exist_ok=True)
    
    orders_df.to_parquet('data/raw/orders.parquet', index=False)
    deliveries_df.to_parquet('data/raw/deliveries.parquet', index=False)
    items_df.to_parquet('data/raw/items.parquet', index=False)
    support_df.to_parquet('data/raw/support_events.parquet', index=False)
    ratings_df.to_parquet('data/raw/ratings.parquet', index=False)
    
    print("   Data saved successfully")
    
    # Run detection pipeline
    print("\n5. Running detection pipeline...")
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
    
    print(f"\n✅ Generated {len(incidents)} incidents")
    
    # Print incident summary
    print("\n" + "=" * 60)
    print("Incident Summary")
    print("=" * 60)
    for incident in incidents:
        print(f"\nIncident: {incident.incident_id}")
        print(f"  Metric: {incident.metric_name}")
        print(f"  Severity: {incident.severity}")
        print(f"  Baseline: {incident.baseline_value:.2f}")
        print(f"  Current: {incident.metric_value:.2f}")
        print(f"  Delta: {incident.delta:.2f} ({incident.delta_percent:.1f}%)")
        print(f"  Top Slices: {len(incident.top_regressing_slices)}")
    
    print("\n" + "=" * 60)
    print("✅ Demo data generation complete!")
    print("=" * 60)
    print("\nThe detection pipeline now has incidents loaded.")
    print("Refresh your frontend to see the incidents in the UI.")
    
    return {
        'orders_df': orders_df,
        'deliveries_df': deliveries_df,
        'items_df': items_df,
        'support_df': support_df,
        'ratings_df': ratings_df,
        'incidents': incidents,
        'pipeline': pipeline
    }

if __name__ == "__main__":
    result = generate_demo_data()


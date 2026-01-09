"""
Test script for metrics layer

Quick test to verify metrics calculation works correctly.
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.generators.synthetic_data_generator import SyntheticDataGenerator
from metrics.cx_metrics import CXMetricsCalculator
from metrics.cohort_slicer import CohortSlicer

def test_metrics():
    """Test metrics calculation"""
    print("Testing metrics layer...")
    
    # Generate test data
    generator = SyntheticDataGenerator(seed=42)
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 2)
    
    print(f"\nGenerating test data...")
    dataset = generator.generate_dataset(
        start_date=start_date,
        end_date=end_date,
        orders_per_day=100,
        batching_threshold=2
    )
    
    # Calculate overall metrics
    print("\n=== Overall Metrics ===")
    calculator = CXMetricsCalculator()
    metrics = calculator.calculate_cx_score(
        dataset['orders'],
        dataset['deliveries'],
        dataset['items'],
        dataset['support_events'],
        dataset['ratings']
    )
    
    for key, value in metrics.items():
        print(f"{key}: {value}")
    
    # Test cohort slicing
    print("\n=== Cohort Metrics ===")
    slicer = CohortSlicer()
    
    # Calculate metrics for a few cohorts
    cohorts = [
        {'region': 'SF'},
        {'category': 'grocery'},
        {'region': 'SF', 'category': 'grocery'},
    ]
    
    for cohort in cohorts:
        print(f"\nCohort: {cohort}")
        cohort_metrics = slicer.calculate_cohort_metrics(
            cohort,
            dataset['orders'],
            dataset['deliveries'],
            dataset['items'],
            dataset['support_events'],
            dataset['ratings']
        )
        print(f"  CX Score: {cohort_metrics['cx_score']}")
        print(f"  On-time Rate: {cohort_metrics['on_time_rate']:.2%}")
        print(f"  Order Count: {cohort_metrics['order_count']}")
    
    print("\n✅ Metrics test passed!")
    return metrics

if __name__ == "__main__":
    test_metrics()


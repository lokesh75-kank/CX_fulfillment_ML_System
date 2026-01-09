"""
Test script for RCA system

Tests root cause analysis on demo scenario.
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.generators.synthetic_data_generator import SyntheticDataGenerator
from rca.report_generator import RCAReportGenerator

def test_rca():
    """Test RCA system"""
    print("Testing RCA system...")
    
    # Generate baseline data (normal operations)
    print("\n=== Generating Baseline Data ===")
    generator = SyntheticDataGenerator(seed=42)
    baseline_start = datetime(2024, 1, 1)
    baseline_end = datetime(2024, 1, 3)
    
    baseline_dataset = generator.generate_dataset(
        start_date=baseline_start,
        end_date=baseline_end,
        orders_per_day=200,
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
        orders_per_day=200,
        batching_threshold=4,  # Increased threshold
        prep_time_drift=0.15  # Some prep-time drift
    )
    
    # Generate RCA report
    print("\n=== Generating RCA Report ===")
    rca_generator = RCAReportGenerator()
    
    report = rca_generator.generate_rca_report(
        incident_id='test_incident_001',
        incident_metric='cx_score',
        baseline_orders=baseline_dataset['orders'],
        baseline_deliveries=baseline_dataset['deliveries'],
        baseline_items=baseline_dataset['items'],
        current_orders=current_dataset['orders'],
        current_deliveries=current_dataset['deliveries'],
        current_items=current_dataset['items'],
        support_df=current_dataset['support_events'],
        ratings_df=current_dataset['ratings'],
        policy_change_date=current_start
    )
    
    # Print report
    print("\n" + "=" * 60)
    print("RCA REPORT")
    print("=" * 60)
    print(f"\nIncident: {report['incident_id']}")
    print(f"Metric: {report['incident_metric']}")
    print(f"\nSummary: {report['summary']}")
    print(f"\nNarrative: {report['narrative']}")
    
    print(f"\nTop Causes:")
    for i, cause in enumerate(report['ranked_causes'][:3], 1):
        hypothesis = cause['hypothesis']
        print(f"\n{i}. {hypothesis.name}")
        print(f"   Confidence: {cause['confidence']:.0%}")
        print(f"   Impact: {cause['impact']:.2f}")
        print(f"   Score: {cause['score']:.3f}")
        
        if 'shap' in cause['evidence']:
            shap_data = cause['evidence']['shap']
            if shap_data:
                top_features = sorted(shap_data.items(), key=lambda x: x[1], reverse=True)[:3]
                print(f"   Top Features:")
                for feat, imp in top_features:
                    print(f"     - {feat}: {imp:.3f}")
    
    print("\n✅ RCA test passed!")
    return report

if __name__ == "__main__":
    test_rca()


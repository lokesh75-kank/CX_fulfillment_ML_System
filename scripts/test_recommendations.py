"""
Test script for recommendations system

Tests action generation, what-if simulation, and tradeoff calculation.
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.generators.synthetic_data_generator import SyntheticDataGenerator
from rca.report_generator import RCAReportGenerator
from recommendations.action_engine import ActionEngine
from recommendations.whatif_simulator import WhatIfSimulator
from recommendations.tradeoff_calculator import TradeoffCalculator

def test_recommendations():
    """Test recommendations system"""
    print("Testing recommendations system...")
    
    # Generate test data
    print("\n=== Generating Test Data ===")
    generator = SyntheticDataGenerator(seed=42)
    baseline_start = datetime(2024, 1, 1)
    baseline_end = datetime(2024, 1, 3)
    current_start = datetime(2024, 1, 3)
    current_end = datetime(2024, 1, 4)
    
    baseline_dataset = generator.generate_dataset(
        start_date=baseline_start,
        end_date=baseline_end,
        orders_per_day=200,
        batching_threshold=2
    )
    
    generator.delivery_gen.set_batching_threshold(4, change_date=current_start)
    current_dataset = generator.generate_dataset(
        start_date=current_start,
        end_date=current_end,
        orders_per_day=200,
        batching_threshold=4,
        prep_time_drift=0.15
    )
    
    # Generate RCA report
    print("\n=== Generating RCA Report ===")
    rca_generator = RCAReportGenerator()
    rca_report = rca_generator.generate_rca_report(
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
    
    # Generate actions
    print("\n=== Generating Actions ===")
    action_engine = ActionEngine()
    actions = action_engine.generate_actions(
        rca_report['ranked_causes'],
        affected_cohorts=[{'region': 'SF', 'category': 'grocery'}]
    )
    
    print(f"Generated {len(actions)} actions")
    for i, action in enumerate(actions[:3], 1):
        print(f"\n{i}. {action.name}")
        print(f"   CX Impact: +{action.expected_cx_impact:.1f} points")
        print(f"   Efficiency Impact: {action.expected_efficiency_impact:+.1f}%")
        print(f"   Confidence: {action.confidence:.0%}")
    
    # Simulate actions
    print("\n=== Simulating Actions ===")
    simulator = WhatIfSimulator()
    
    simulated_impacts = []
    for action in actions[:2]:  # Simulate top 2
        if 'batching' in action.name.lower():
            impact = simulator.simulate_batching_reduction(
                current_dataset['orders'],
                current_dataset['deliveries'],
                current_dataset['items'],
                current_dataset['support_events'],
                current_dataset['ratings'],
                current_batching_rate=0.6,
                new_batching_rate=0.3,
                affected_cohort={'region': 'SF', 'category': 'grocery'}
            )
        elif 'eta' in action.name.lower():
            impact = simulator.simulate_eta_buffer(
                current_dataset['orders'],
                current_dataset['deliveries'],
                current_dataset['items'],
                current_dataset['support_events'],
                current_dataset['ratings'],
                buffer_minutes=5,
                affected_cohort={'region': 'SF', 'category': 'grocery'}
            )
        else:
            continue
        
        simulated_impacts.append({
            'action': action,
            'impact': impact
        })
        
        print(f"\n{action.name}:")
        print(f"  CX Score Delta: +{impact.get('cx_score_delta', 0):.1f} points")
        print(f"  Efficiency Impact: {impact.get('efficiency_impact', 0):+.1f}%")
    
    # Calculate tradeoffs
    print("\n=== Calculating Tradeoffs ===")
    tradeoff_calc = TradeoffCalculator()
    
    action_dicts = []
    for item in simulated_impacts:
        action_dicts.append({
            'action_id': item['action'].action_id,
            'name': item['action'].name,
            'expected_cx_impact': item['impact'].get('cx_score_delta', 0),
            'expected_efficiency_impact': item['impact'].get('efficiency_impact', 0),
            'confidence': item['impact'].get('confidence', 0.5)
        })
    
    compared = tradeoff_calc.compare_actions(action_dicts)
    
    print("\nRanked Actions by Tradeoff:")
    for i, action in enumerate(compared, 1):
        print(f"\n{i}. {action['name']}")
        print(f"   Net Benefit: {action['net_benefit']:.3f}")
        print(f"   ROI: {action['roi']:.2f}")
        print(f"   Recommendation: {action['recommendation']}")
    
    print("\n✅ Recommendations test passed!")
    return actions, simulated_impacts, compared

if __name__ == "__main__":
    test_recommendations()


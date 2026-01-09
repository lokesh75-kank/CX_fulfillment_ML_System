"""
Test script for data generators

Quick test to verify generators work correctly.
"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.generators.synthetic_data_generator import SyntheticDataGenerator

def test_generators():
    """Test data generation"""
    print("Testing data generators...")
    
    generator = SyntheticDataGenerator(seed=42)
    
    # Generate small test dataset (1 day)
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 2)
    
    print(f"\nGenerating test data from {start_date} to {end_date}...")
    dataset = generator.generate_dataset(
        start_date=start_date,
        end_date=end_date,
        orders_per_day=100,  # Small number for testing
        batching_threshold=2
    )
    
    # Print summary
    print("\n=== Dataset Summary ===")
    for table_name, df in dataset.items():
        print(f"{table_name}: {len(df)} rows")
        if len(df) > 0:
            print(f"  Columns: {list(df.columns)}")
            print(f"  Sample row:")
            print(f"    {df.iloc[0].to_dict()}")
        print()
    
    print("✅ Generators test passed!")
    return dataset

if __name__ == "__main__":
    test_generators()


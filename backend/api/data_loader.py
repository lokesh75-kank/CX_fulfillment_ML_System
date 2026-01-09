"""
Data Loader

Loads data and generates incidents for the API.
"""

import os
import pandas as pd
from datetime import datetime
from detection.detection_pipeline import DetectionPipeline

# Global pipeline instance
_pipeline = None
_data_loaded = False


def get_pipeline() -> DetectionPipeline:
    """Get or create detection pipeline instance"""
    global _pipeline
    if _pipeline is None:
        _pipeline = DetectionPipeline()
    return _pipeline


def load_data_and_generate_incidents():
    """Load data from files and generate incidents"""
    global _data_loaded
    
    if _data_loaded:
        return  # Already loaded
    
    data_dir = 'data/raw'
    
    # Check if data files exist
    if not os.path.exists(os.path.join(data_dir, 'orders.parquet')):
        print("No data files found. Run generate_demo_data.py first.")
        return
    
    print("Loading data from data/raw/...")
    
    try:
        # Load data
        orders_df = pd.read_parquet(os.path.join(data_dir, 'orders.parquet'))
        deliveries_df = pd.read_parquet(os.path.join(data_dir, 'deliveries.parquet'))
        items_df = pd.read_parquet(os.path.join(data_dir, 'items.parquet'))
        support_df = pd.read_parquet(os.path.join(data_dir, 'support_events.parquet'))
        ratings_df = pd.read_parquet(os.path.join(data_dir, 'ratings.parquet'))
        
        print(f"Loaded {len(orders_df)} orders")
        
        # Get pipeline
        pipeline = get_pipeline()
        
        # Define time periods
        baseline_start = datetime(2024, 1, 1)
        baseline_end = datetime(2024, 1, 3)
        current_start = datetime(2024, 1, 3)
        current_end = datetime(2024, 1, 5)
        
        # Generate incidents
        print("Generating incidents...")
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
        
        print(f"Generated {len(incidents)} incidents")
        _data_loaded = True
        
    except Exception as e:
        print(f"Error loading data: {e}")
        import traceback
        traceback.print_exc()


# Auto-load on import
load_data_and_generate_incidents()


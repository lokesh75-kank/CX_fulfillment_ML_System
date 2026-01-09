"""
Metrics API endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
import pandas as pd
import os

from metrics.cx_metrics import CXMetricsCalculator
from metrics.cohort_slicer import CohortSlicer

router = APIRouter()

metrics_calculator = CXMetricsCalculator()
cohort_slicer = CohortSlicer()


def load_data():
    """Load data from files"""
    data_dir = 'data/raw'
    if not os.path.exists(os.path.join(data_dir, 'orders.parquet')):
        return None, None, None, None, None
    
    orders_df = pd.read_parquet(os.path.join(data_dir, 'orders.parquet'))
    deliveries_df = pd.read_parquet(os.path.join(data_dir, 'deliveries.parquet'))
    items_df = pd.read_parquet(os.path.join(data_dir, 'items.parquet'))
    support_df = pd.read_parquet(os.path.join(data_dir, 'support_events.parquet'))
    ratings_df = pd.read_parquet(os.path.join(data_dir, 'ratings.parquet'))
    
    return orders_df, deliveries_df, items_df, support_df, ratings_df


class CXScoreResponse(BaseModel):
    """CX Score response"""
    timestamp: datetime
    cx_score: float
    on_time_rate: float
    cancellation_rate: float
    refund_rate: float


class MetricsSummaryResponse(BaseModel):
    """Metrics summary response"""
    current_cx_score: float
    baseline_cx_score: Optional[float]
    delta: Optional[float]
    trend: str  # 'up', 'down', 'stable'


@router.get("/cx-score")
async def get_cx_score(
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    cohort: Optional[str] = Query(None)
):
    """Get CX Score time series"""
    # In production, this would query actual data
    # For now, return sample data
    
    sample_data = [
        {"timestamp": datetime(2024, 1, 1), "cx_score": 88.5, "on_time_rate": 0.92},
        {"timestamp": datetime(2024, 1, 2), "cx_score": 87.2, "on_time_rate": 0.91},
        {"timestamp": datetime(2024, 1, 3), "cx_score": 85.8, "on_time_rate": 0.89},
        {"timestamp": datetime(2024, 1, 4), "cx_score": 72.3, "on_time_rate": 0.78},
    ]
    
    return sample_data


@router.get("/summary")
async def get_metrics_summary():
    """Get metrics summary"""
    # Load data
    data = load_data()
    if data[0] is None:
        # Return sample data if no data loaded
        return MetricsSummaryResponse(
            current_cx_score=72.3,
            baseline_cx_score=88.5,
            delta=-16.2,
            trend="down"
        )
    
    orders_df, deliveries_df, items_df, support_df, ratings_df = data
    
    # Calculate baseline (Jan 1-3)
    baseline_orders = cohort_slicer.slice_by_time_window(
        orders_df, datetime(2024, 1, 1), datetime(2024, 1, 3)
    )
    baseline_order_ids = baseline_orders['order_id'].unique()
    baseline_deliveries = deliveries_df[deliveries_df['order_id'].isin(baseline_order_ids)]
    baseline_items = items_df[items_df['order_id'].isin(baseline_order_ids)]
    baseline_support = support_df[support_df['order_id'].isin(baseline_order_ids)]
    baseline_ratings = ratings_df[ratings_df['order_id'].isin(baseline_order_ids)]
    
    baseline_metrics = metrics_calculator.calculate_cx_score(
        baseline_orders, baseline_deliveries, baseline_items,
        baseline_support, baseline_ratings
    )
    
    # Calculate current (Jan 3-5)
    current_orders = cohort_slicer.slice_by_time_window(
        orders_df, datetime(2024, 1, 3), datetime(2024, 1, 5)
    )
    current_order_ids = current_orders['order_id'].unique()
    current_deliveries = deliveries_df[deliveries_df['order_id'].isin(current_order_ids)]
    current_items = items_df[items_df['order_id'].isin(current_order_ids)]
    current_support = support_df[support_df['order_id'].isin(current_order_ids)]
    current_ratings = ratings_df[ratings_df['order_id'].isin(current_order_ids)]
    
    current_metrics = metrics_calculator.calculate_cx_score(
        current_orders, current_deliveries, current_items,
        current_support, current_ratings
    )
    
    baseline_score = baseline_metrics['cx_score']
    current_score = current_metrics['cx_score']
    delta = current_score - baseline_score
    
    trend = "down" if delta < -2 else "up" if delta > 2 else "stable"
    
    return MetricsSummaryResponse(
        current_cx_score=round(current_score, 1),
        baseline_cx_score=round(baseline_score, 1),
        delta=round(delta, 1),
        trend=trend
    )


@router.get("/cohorts")
async def get_cohorts():
    """Get available cohort dimensions"""
    return {
        "dimensions": [
            {"name": "store_id", "type": "categorical"},
            {"name": "category", "type": "categorical", "values": ["grocery", "convenience", "retail"]},
            {"name": "region", "type": "categorical", "values": ["SF", "NYC", "LA", "Chicago", "Boston"]},
            {"name": "time_of_day", "type": "categorical", "values": ["breakfast", "lunch", "dinner", "late-night"]},
            {"name": "basket_size", "type": "categorical", "values": ["small", "medium", "large"]}
        ]
    }


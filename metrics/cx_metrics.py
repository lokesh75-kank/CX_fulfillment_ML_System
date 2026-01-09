"""
CX Metrics Calculation

Implements CX Score and all sub-metrics for customer experience measurement.
"""

from typing import Dict, Optional
import pandas as pd
import numpy as np
from datetime import timedelta


class CXMetricsCalculator:
    """Calculates CX metrics from order, delivery, item, support, and rating data"""
    
    # Weight configuration for CX Score
    WEIGHTS = {
        "on_time": 0.30,
        "item_accuracy": 0.25,
        "cancellation": 0.15,
        "refund": 0.15,
        "support": 0.10,
        "rating": 0.05
    }
    
    # On-time threshold (minutes)
    ON_TIME_THRESHOLD_MINUTES = 5
    
    def __init__(self):
        """Initialize metrics calculator"""
        pass
    
    def calculate_on_time_rate(self, orders_df: pd.DataFrame, 
                              deliveries_df: pd.DataFrame) -> float:
        """
        Calculate on-time rate: % of orders delivered within promised_eta ± threshold
        
        Args:
            orders_df: DataFrame with orders (must have order_id, promised_eta)
            deliveries_df: DataFrame with deliveries (must have order_id, actual_eta, canceled_flag)
        
        Returns:
            On-time rate (0-1)
        """
        # Merge orders and deliveries
        merged = orders_df.merge(
            deliveries_df[['order_id', 'actual_eta', 'canceled_flag']],
            on='order_id',
            how='left'
        )
        
        # Filter out canceled orders
        merged = merged[merged['canceled_flag'] != True]
        
        # Filter out orders without actual_eta
        merged = merged[merged['actual_eta'].notna()]
        
        if len(merged) == 0:
            return 0.0
        
        # Calculate if on-time
        threshold = timedelta(minutes=self.ON_TIME_THRESHOLD_MINUTES)
        merged['on_time'] = (
            (merged['actual_eta'] >= merged['promised_eta'] - threshold) &
            (merged['actual_eta'] <= merged['promised_eta'] + threshold)
        )
        
        return merged['on_time'].mean()
    
    def calculate_eta_error(self, orders_df: pd.DataFrame,
                           deliveries_df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate ETA error metrics
        
        Returns:
            Dict with 'mean_absolute_error', 'mean_error', 'std_error'
        """
        merged = orders_df.merge(
            deliveries_df[['order_id', 'actual_eta', 'canceled_flag']],
            on='order_id',
            how='left'
        )
        
        # Filter out canceled orders and missing ETAs
        merged = merged[
            (merged['canceled_flag'] != True) &
            (merged['actual_eta'].notna())
        ]
        
        if len(merged) == 0:
            return {
                'mean_absolute_error': 0.0,
                'mean_error': 0.0,
                'std_error': 0.0
            }
        
        # Calculate error in minutes
        merged['error_minutes'] = (
            (merged['actual_eta'] - merged['promised_eta']).dt.total_seconds() / 60
        )
        
        return {
            'mean_absolute_error': merged['error_minutes'].abs().mean(),
            'mean_error': merged['error_minutes'].mean(),
            'std_error': merged['error_minutes'].std()
        }
    
    def calculate_item_accuracy(self, items_df: pd.DataFrame) -> float:
        """
        Calculate item accuracy: 1 - (substituted_rate + missing_rate)
        
        Args:
            items_df: DataFrame with items (must have substituted_flag, missing_flag)
        
        Returns:
            Item accuracy (0-1)
        """
        if len(items_df) == 0:
            return 1.0
        
        substituted_rate = items_df['substituted_flag'].mean()
        missing_rate = items_df['missing_flag'].mean()
        
        accuracy = 1.0 - (substituted_rate + missing_rate)
        return max(0.0, min(1.0, accuracy))  # Clamp between 0 and 1
    
    def calculate_cancellation_rate(self, deliveries_df: pd.DataFrame) -> float:
        """
        Calculate cancellation rate: % of canceled orders
        
        Args:
            deliveries_df: DataFrame with deliveries (must have canceled_flag)
        
        Returns:
            Cancellation rate (0-1)
        """
        if len(deliveries_df) == 0:
            return 0.0
        
        return deliveries_df['canceled_flag'].mean()
    
    def calculate_refund_rate(self, items_df: pd.DataFrame) -> float:
        """
        Calculate refund rate: % of items with refund_amount > 0
        
        Args:
            items_df: DataFrame with items (must have refund_amount)
        
        Returns:
            Refund rate (0-1)
        """
        if len(items_df) == 0:
            return 0.0
        
        # Calculate at order level (order has refund if any item has refund)
        order_refunds = items_df.groupby('order_id')['refund_amount'].sum()
        refund_rate = (order_refunds > 0).mean()
        
        return refund_rate
    
    def calculate_support_rate(self, orders_df: pd.DataFrame,
                              support_df: pd.DataFrame) -> float:
        """
        Calculate support-contact rate: % of orders with support tickets
        
        Args:
            orders_df: DataFrame with orders (must have order_id)
            support_df: DataFrame with support events (must have order_id)
        
        Returns:
            Support rate (0-1)
        """
        if len(orders_df) == 0:
            return 0.0
        
        orders_with_support = support_df['order_id'].nunique()
        total_orders = orders_df['order_id'].nunique()
        
        if total_orders == 0:
            return 0.0
        
        return orders_with_support / total_orders
    
    def calculate_rating_proxy(self, ratings_df: pd.DataFrame) -> float:
        """
        Calculate rating proxy: normalized mean stars (1-5 scale -> 0-1 scale)
        
        Args:
            ratings_df: DataFrame with ratings (must have stars)
        
        Returns:
            Rating proxy (0-1), where 5 stars = 1.0, 1 star = 0.0
        """
        if len(ratings_df) == 0:
            return 0.5  # Default to neutral if no ratings
        
        mean_stars = ratings_df['stars'].mean()
        # Normalize: (stars - 1) / 4, so 1 star = 0, 5 stars = 1
        normalized = (mean_stars - 1) / 4.0
        return max(0.0, min(1.0, normalized))
    
    def calculate_cx_score(self, orders_df: pd.DataFrame,
                          deliveries_df: pd.DataFrame,
                          items_df: pd.DataFrame,
                          support_df: pd.DataFrame,
                          ratings_df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate comprehensive CX Score and all sub-metrics
        
        Args:
            orders_df: Orders DataFrame
            deliveries_df: Deliveries DataFrame
            items_df: Items DataFrame
            support_df: Support events DataFrame
            ratings_df: Ratings DataFrame
        
        Returns:
            Dict with all metrics including 'cx_score' (0-100)
        """
        # Calculate all sub-metrics
        on_time_rate = self.calculate_on_time_rate(orders_df, deliveries_df)
        eta_error = self.calculate_eta_error(orders_df, deliveries_df)
        item_accuracy = self.calculate_item_accuracy(items_df)
        cancellation_rate = self.calculate_cancellation_rate(deliveries_df)
        refund_rate = self.calculate_refund_rate(items_df)
        support_rate = self.calculate_support_rate(orders_df, support_df)
        rating_proxy = self.calculate_rating_proxy(ratings_df)
        
        # Convert rates to scores (0-100 scale)
        on_time_score = on_time_rate * 100
        item_accuracy_score = item_accuracy * 100
        cancellation_score = (1.0 - cancellation_rate) * 100  # Invert: lower is better
        refund_score = (1.0 - refund_rate) * 100  # Invert: lower is better
        support_score = (1.0 - support_rate) * 100  # Invert: lower is better
        rating_score = rating_proxy * 100
        
        # Calculate weighted CX Score
        cx_score = (
            self.WEIGHTS['on_time'] * on_time_score +
            self.WEIGHTS['item_accuracy'] * item_accuracy_score +
            self.WEIGHTS['cancellation'] * cancellation_score +
            self.WEIGHTS['refund'] * refund_score +
            self.WEIGHTS['support'] * support_score +
            self.WEIGHTS['rating'] * rating_score
        )
        
        return {
            'cx_score': round(cx_score, 2),
            'on_time_rate': round(on_time_rate, 4),
            'on_time_score': round(on_time_score, 2),
            'eta_mean_absolute_error': round(eta_error['mean_absolute_error'], 2),
            'eta_mean_error': round(eta_error['mean_error'], 2),
            'eta_std_error': round(eta_error['std_error'], 2),
            'item_accuracy': round(item_accuracy, 4),
            'item_accuracy_score': round(item_accuracy_score, 2),
            'cancellation_rate': round(cancellation_rate, 4),
            'cancellation_score': round(cancellation_score, 2),
            'refund_rate': round(refund_rate, 4),
            'refund_score': round(refund_score, 2),
            'support_rate': round(support_rate, 4),
            'support_score': round(support_score, 2),
            'rating_proxy': round(rating_proxy, 4),
            'rating_score': round(rating_score, 2),
            'mean_stars': round(ratings_df['stars'].mean(), 2) if len(ratings_df) > 0 else None
        }
    
    def calculate_metrics_for_cohort(self, cohort_filter: Dict,
                                    orders_df: pd.DataFrame,
                                    deliveries_df: pd.DataFrame,
                                    items_df: pd.DataFrame,
                                    support_df: pd.DataFrame,
                                    ratings_df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate metrics for a specific cohort
        
        Args:
            cohort_filter: Dict with filters like {'region': 'SF', 'category': 'grocery'}
            orders_df: Orders DataFrame
            deliveries_df: Deliveries DataFrame
            items_df: Items DataFrame
            support_df: Support events DataFrame
            ratings_df: Ratings DataFrame
        
        Returns:
            Dict with all metrics for this cohort
        """
        # Filter orders by cohort
        filtered_orders = orders_df.copy()
        for key, value in cohort_filter.items():
            if key in filtered_orders.columns:
                filtered_orders = filtered_orders[filtered_orders[key] == value]
        
        # Filter other dataframes based on filtered orders
        order_ids = filtered_orders['order_id'].unique()
        
        filtered_deliveries = deliveries_df[deliveries_df['order_id'].isin(order_ids)]
        filtered_items = items_df[items_df['order_id'].isin(order_ids)]
        filtered_support = support_df[support_df['order_id'].isin(order_ids)]
        filtered_ratings = ratings_df[ratings_df['order_id'].isin(order_ids)]
        
        # Calculate metrics
        return self.calculate_cx_score(
            filtered_orders,
            filtered_deliveries,
            filtered_items,
            filtered_support,
            filtered_ratings
        )


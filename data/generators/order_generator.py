"""
Order Generator

Generates realistic order data with temporal patterns, category distributions,
and regional variations.
"""

import uuid
import random
from datetime import datetime, timedelta
from typing import List, Dict
import pandas as pd

from ..schemas.schema_definitions import (
    OrderSchema,
    VALID_CATEGORIES,
    VALID_REGIONS,
    VALID_TIME_OF_DAY,
    BASKET_SIZE_THRESHOLDS,
    TIME_OF_DAY_WINDOWS,
)


class OrderGenerator:
    """Generates synthetic order data"""
    
    def __init__(self, seed: int = 42):
        """Initialize generator with random seed"""
        random.seed(seed)
        self.user_ids = [f"user_{i:06d}" for i in range(10000)]
        self.store_ids = self._generate_store_ids()
        
    def _generate_store_ids(self) -> List[str]:
        """Generate store IDs for each region and category"""
        store_ids = []
        for region in VALID_REGIONS:
            for category in VALID_CATEGORIES:
                for i in range(1, 11):  # 10 stores per region-category combo
                    store_ids.append(f"store_{region.lower()}_{category}_{i:02d}")
        return store_ids
    
    def _get_time_of_day(self, hour: int) -> str:
        """Determine time of day based on hour"""
        if 6 <= hour < 11:
            return "breakfast"
        elif 11 <= hour < 15:
            return "lunch"
        elif 17 <= hour < 21:
            return "dinner"
        else:
            return "late-night"
    
    def _get_basket_size(self, basket_value: float) -> str:
        """Determine basket size based on value"""
        if basket_value < 25:
            return "small"
        elif basket_value < 75:
            return "medium"
        else:
            return "large"
    
    def _generate_basket_value(self, category: str, time_of_day: str) -> float:
        """Generate basket value based on category and time of day"""
        # Base values by category
        base_values = {
            "grocery": (30, 80),
            "convenience": (15, 40),
            "retail": (25, 60)
        }
        
        # Time-of-day multipliers
        time_multipliers = {
            "breakfast": 0.8,
            "lunch": 1.0,
            "dinner": 1.2,
            "late-night": 0.9
        }
        
        base_min, base_max = base_values[category]
        multiplier = time_multipliers[time_of_day]
        
        return round(random.uniform(base_min * multiplier, base_max * multiplier), 2)
    
    def _generate_promised_eta(self, order_time: datetime, category: str, 
                               region: str, time_of_day: str) -> datetime:
        """Generate promised ETA based on order characteristics"""
        # Base prep time by category (minutes)
        base_prep_times = {
            "grocery": 25,
            "convenience": 10,
            "retail": 15
        }
        
        # Peak hour multiplier
        peak_multipliers = {
            "breakfast": 1.1,
            "lunch": 1.3,
            "dinner": 1.5,
            "late-night": 1.0
        }
        
        base_prep = base_prep_times[category]
        multiplier = peak_multipliers[time_of_day]
        
        # Add travel time (5-15 minutes based on region density)
        travel_times = {
            "SF": 8,
            "NYC": 10,
            "LA": 12,
            "Chicago": 9,
            "Boston": 8
        }
        travel_time = travel_times.get(region, 10)
        
        total_minutes = int(base_prep * multiplier + travel_time)
        
        return order_time + timedelta(minutes=total_minutes)
    
    def generate_order(self, order_time: datetime, region: str = None, 
                      category: str = None) -> OrderSchema:
        """Generate a single order"""
        # Random selection if not specified
        if region is None:
            region = random.choice(VALID_REGIONS)
        if category is None:
            category = random.choice(VALID_CATEGORIES)
        
        # Get time of day from order time
        hour = order_time.hour
        time_of_day = self._get_time_of_day(hour)
        
        # Generate order attributes
        order_id = f"ord_{uuid.uuid4().hex[:12]}"
        user_id = random.choice(self.user_ids)
        
        # Select store from region and category
        matching_stores = [s for s in self.store_ids 
                          if f"_{region.lower()}_{category}_" in s]
        store_id = random.choice(matching_stores) if matching_stores else random.choice(self.store_ids)
        
        # Generate basket value
        basket_value = self._generate_basket_value(category, time_of_day)
        basket_size = self._get_basket_size(basket_value)
        
        # Generate promised ETA
        promised_eta = self._generate_promised_eta(order_time, category, region, time_of_day)
        
        return OrderSchema(
            order_id=order_id,
            user_id=user_id,
            store_id=store_id,
            category=category,
            basket_value=basket_value,
            promised_eta=promised_eta,
            order_time=order_time,
            region=region,
            time_of_day=time_of_day,
            basket_size=basket_size
        )
    
    def generate_orders(self, start_date: datetime, end_date: datetime,
                       orders_per_day: int = 10000) -> List[OrderSchema]:
        """Generate orders for a date range"""
        orders = []
        current_date = start_date
        
        while current_date < end_date:
            # Generate orders for this day
            # Vary orders by day of week (weekends have more orders)
            day_of_week = current_date.weekday()
            if day_of_week >= 5:  # Weekend
                daily_orders = int(orders_per_day * 1.2)
            else:
                daily_orders = orders_per_day
            
            # Distribute orders throughout the day with peak hours
            for _ in range(daily_orders):
                # Generate random hour with peak distribution
                hour_weights = {
                    "breakfast": 0.15,
                    "lunch": 0.25,
                    "dinner": 0.35,
                    "late-night": 0.25
                }
                
                time_of_day = random.choices(
                    list(hour_weights.keys()),
                    weights=list(hour_weights.values())
                )[0]
                
                # Get hour range for time of day
                hour_start, hour_end = TIME_OF_DAY_WINDOWS[time_of_day]
                if hour_start > hour_end:  # Late-night wraps around
                    hour = random.choice(list(range(hour_start, 24)) + list(range(0, hour_end)))
                else:
                    hour = random.randint(hour_start, hour_end - 1)
                
                minute = random.randint(0, 59)
                order_time = current_date.replace(hour=hour, minute=minute, second=0)
                
                # Generate order
                order = self.generate_order(order_time)
                orders.append(order)
            
            # Move to next day
            current_date += timedelta(days=1)
        
        return orders
    
    def to_dataframe(self, orders: List[OrderSchema]) -> pd.DataFrame:
        """Convert orders to pandas DataFrame"""
        data = []
        for order in orders:
            data.append({
                "order_id": order.order_id,
                "user_id": order.user_id,
                "store_id": order.store_id,
                "category": order.category,
                "basket_value": order.basket_value,
                "promised_eta": order.promised_eta,
                "order_time": order.order_time,
                "region": order.region,
                "time_of_day": order.time_of_day,
                "basket_size": order.basket_size
            })
        return pd.DataFrame(data)


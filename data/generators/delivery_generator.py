"""
Delivery Generator

Generates delivery data correlated with orders, including batching logic,
prep-time variations, and realistic delivery patterns.
"""

import uuid
import random
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import pandas as pd

from ..schemas.schema_definitions import DeliverySchema


class DeliveryGenerator:
    """Generates synthetic delivery data"""
    
    def __init__(self, seed: int = 42):
        """Initialize generator with random seed"""
        random.seed(seed)
        self.dasher_ids = [f"dasher_{i:04d}" for i in range(1000)]
        
        # Policy parameters (can be changed for demo scenario)
        self.batching_threshold = 2  # Default: batch when 2+ orders ready
        self.policy_change_date = None  # Set to simulate policy change
        
    def set_batching_threshold(self, threshold: int, change_date: datetime = None):
        """Set batching threshold (for policy change simulation)"""
        self.batching_threshold = threshold
        self.policy_change_date = change_date
    
    def _generate_prep_time(self, order_time: datetime, category: str, 
                           region: str, time_of_day: str, 
                           prep_time_drift: float = 0.0) -> int:
        """Generate merchant prep time in seconds"""
        # Base prep times by category (seconds)
        base_prep_times = {
            "grocery": 1500,  # 25 minutes
            "convenience": 600,  # 10 minutes
            "retail": 900  # 15 minutes
        }
        
        # Peak hour multipliers
        peak_multipliers = {
            "breakfast": 1.1,
            "lunch": 1.3,
            "dinner": 1.5,
            "late-night": 1.0
        }
        
        base_prep = base_prep_times[category]
        multiplier = peak_multipliers[time_of_day]
        
        # Add drift if specified (for demo scenario)
        drift_factor = 1.0 + prep_time_drift
        
        # Add some randomness
        prep_time = int(base_prep * multiplier * drift_factor * random.uniform(0.8, 1.2))
        
        return max(300, prep_time)  # Minimum 5 minutes
    
    def _generate_distance(self, region: str) -> float:
        """Generate delivery distance based on region"""
        # Urban regions have shorter distances
        distance_ranges = {
            "SF": (0.5, 3.0),
            "NYC": (0.3, 2.5),
            "LA": (1.0, 5.0),
            "Chicago": (0.5, 3.5),
            "Boston": (0.5, 3.0)
        }
        
        min_dist, max_dist = distance_ranges.get(region, (0.5, 4.0))
        return round(random.uniform(min_dist, max_dist), 2)
    
    def _calculate_dasher_wait(self, batched_flag: bool, num_batched: int = 1) -> int:
        """Calculate dasher wait time at store"""
        if not batched_flag:
            return random.randint(60, 180)  # 1-3 minutes for single order
        
        # Batched orders wait longer
        # More orders = longer wait
        base_wait = 300  # 5 minutes base
        additional_wait = (num_batched - 1) * 120  # 2 minutes per additional order
        
        # If batching threshold increased, wait times increase significantly
        if self.batching_threshold >= 4:
            multiplier = 1.5
        else:
            multiplier = 1.0
        
        wait_time = int((base_wait + additional_wait) * multiplier * random.uniform(0.9, 1.3))
        
        return wait_time
    
    def _should_batch(self, order_time: datetime, order_queue: List) -> bool:
        """Determine if order should be batched based on current policy"""
        # Check if policy change applies
        if self.policy_change_date and order_time >= self.policy_change_date:
            # After policy change, use new threshold
            return len(order_queue) >= self.batching_threshold - 1
        
        # Before policy change, use default threshold
        return len(order_queue) >= (self.batching_threshold - 1)
    
    def _calculate_actual_eta(self, order_time: datetime, promised_eta: datetime,
                             prep_time: int, dasher_wait: int, distance: float,
                             batched_flag: bool) -> datetime:
        """Calculate actual delivery time"""
        # Start from order time
        actual_time = order_time
        
        # Add prep time
        actual_time += timedelta(seconds=prep_time)
        
        # Add dasher wait (if batched, this is longer)
        actual_time += timedelta(seconds=dasher_wait)
        
        # Add travel time (based on distance)
        # Average speed: 15 mph in urban areas
        travel_time_seconds = int((distance / 15.0) * 3600)
        actual_time += timedelta(seconds=travel_time_seconds)
        
        # Add some randomness
        actual_time += timedelta(seconds=random.randint(-300, 600))  # ±5 minutes
        
        return actual_time
    
    def _should_cancel(self, promised_eta: datetime, actual_eta: datetime,
                       batched_flag: bool) -> bool:
        """Determine if order should be canceled"""
        # Calculate delay
        delay_minutes = (actual_eta - promised_eta).total_seconds() / 60
        
        # Cancellation probability increases with delay
        if delay_minutes < 5:
            cancel_prob = 0.01
        elif delay_minutes < 10:
            cancel_prob = 0.03
        elif delay_minutes < 15:
            cancel_prob = 0.08
        else:
            cancel_prob = 0.15
        
        # Batched orders have higher cancellation risk
        if batched_flag:
            cancel_prob *= 1.5
        
        return random.random() < cancel_prob
    
    def generate_delivery(self, order: Dict, prep_time_drift: float = 0.0,
                         order_queue: List = None) -> DeliverySchema:
        """Generate delivery for a single order"""
        order_time = order['order_time']
        promised_eta = order['promised_eta']
        category = order['category']
        region = order['region']
        time_of_day = order['time_of_day']
        
        # Determine if order should be batched
        if order_queue is None:
            order_queue = []
        
        batched_flag = self._should_batch(order_time, order_queue)
        num_batched = len(order_queue) + 1 if batched_flag else 1
        
        # Generate delivery attributes
        prep_time = self._generate_prep_time(
            order_time, category, region, time_of_day, prep_time_drift
        )
        distance = self._generate_distance(region)
        dasher_wait = self._calculate_dasher_wait(batched_flag, num_batched)
        
        # Calculate actual ETA
        actual_eta = self._calculate_actual_eta(
            order_time, promised_eta, prep_time, dasher_wait, distance, batched_flag
        )
        
        # Determine cancellation
        canceled_flag = self._should_cancel(promised_eta, actual_eta, batched_flag)
        
        if canceled_flag:
            delivery_time = None
            actual_eta = None
        else:
            delivery_time = actual_eta
        
        dasher_id = random.choice(self.dasher_ids) if not canceled_flag else None
        
        return DeliverySchema(
            order_id=order['order_id'],
            actual_eta=actual_eta,
            dasher_wait=dasher_wait,
            merchant_prep_time=prep_time,
            distance=distance,
            batched_flag=batched_flag,
            canceled_flag=canceled_flag,
            delivery_time=delivery_time,
            dasher_id=dasher_id
        )
    
    def generate_deliveries(self, orders_df: pd.DataFrame,
                           prep_time_drift: float = 0.0) -> List[DeliverySchema]:
        """Generate deliveries for all orders"""
        deliveries = []
        
        # Group orders by store and time window for batching simulation
        orders_df = orders_df.sort_values('order_time')
        
        # Track orders waiting to be batched
        store_queues: Dict[str, List[Dict]] = {}
        
        for _, order_row in orders_df.iterrows():
            order = order_row.to_dict()
            store_id = order['store_id']
            
            # Initialize queue for store if needed
            if store_id not in store_queues:
                store_queues[store_id] = []
            
            # Check if we should batch orders from this store
            queue = store_queues[store_id]
            
            # Add current order to queue
            queue.append(order)
            
            # Check if we should batch
            if self._should_batch(order['order_time'], queue[:-1]):  # Exclude current order
                # Generate deliveries for batched orders
                for queued_order in queue:
                    delivery = self.generate_delivery(
                        queued_order, prep_time_drift, queue
                    )
                    deliveries.append(delivery)
                
                # Clear queue
                store_queues[store_id] = []
            else:
                # Check if oldest order in queue is too old (force delivery)
                if len(queue) > 0:
                    oldest_order = queue[0]
                    wait_time = (order['order_time'] - oldest_order['order_time']).total_seconds()
                    
                    # If waiting more than 15 minutes, deliver oldest order
                    if wait_time > 900:
                        oldest_order = queue.pop(0)
                        delivery = self.generate_delivery(
                            oldest_order, prep_time_drift, [oldest_order]
                        )
                        deliveries.append(delivery)
        
        # Process remaining orders in queues
        for store_id, queue in store_queues.items():
            for queued_order in queue:
                delivery = self.generate_delivery(
                    queued_order, prep_time_drift, queue
                )
                deliveries.append(delivery)
        
        return deliveries
    
    def to_dataframe(self, deliveries: List[DeliverySchema]) -> pd.DataFrame:
        """Convert deliveries to pandas DataFrame"""
        data = []
        for delivery in deliveries:
            data.append({
                "order_id": delivery.order_id,
                "actual_eta": delivery.actual_eta,
                "dasher_wait": delivery.dasher_wait,
                "merchant_prep_time": delivery.merchant_prep_time,
                "distance": delivery.distance,
                "batched_flag": delivery.batched_flag,
                "canceled_flag": delivery.canceled_flag,
                "delivery_time": delivery.delivery_time,
                "dasher_id": delivery.dasher_id
            })
        return pd.DataFrame(data)


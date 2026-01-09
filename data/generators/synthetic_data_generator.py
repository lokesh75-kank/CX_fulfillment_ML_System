"""
Synthetic Data Generator

Orchestrates all data generators to create a complete synthetic dataset
for the CX-Fulfillment Agent system.
"""

import os
import random
from datetime import datetime, timedelta
from typing import Optional, Dict
import pandas as pd

from .order_generator import OrderGenerator
from .delivery_generator import DeliveryGenerator
from .item_generator import ItemGenerator


class SyntheticDataGenerator:
    """Main orchestrator for generating synthetic data"""
    
    def __init__(self, seed: int = 42):
        """Initialize all generators"""
        self.order_gen = OrderGenerator(seed=seed)
        self.delivery_gen = DeliveryGenerator(seed=seed)
        self.item_gen = ItemGenerator(seed=seed)
        
    def generate_inventory_events(self, start_date: datetime, end_date: datetime,
                                 stores: list, skus: list,
                                 base_in_stock_prob: float = 0.85,
                                 degradation_rate: float = 0.0) -> pd.DataFrame:
        """Generate inventory events"""
        events = []
        current_date = start_date
        
        event_id_counter = 1
        
        # Sample stores and SKUs to avoid too many events
        # Generate events for subset of stores and SKUs
        sampled_stores = random.sample(stores, min(50, len(stores)))
        sampled_skus = random.sample(skus, min(20, len(skus)))
        
        while current_date < end_date:
            # Generate events every 4 hours (6 times per day) to reduce volume
            for hour in range(0, 24, 4):
                event_time = current_date.replace(hour=hour, minute=0, second=0)
                
                # Calculate degradation over time
                days_elapsed = (event_time - start_date).days
                current_prob = base_in_stock_prob - (degradation_rate * days_elapsed)
                current_prob = max(0.1, min(1.0, current_prob))  # Clamp between 0.1 and 1.0
                
                # Generate events for sampled store-SKU combinations
                for store_id in sampled_stores:
                    for sku_id in sampled_skus:
                        # Add some randomness
                        in_stock_prob = current_prob * random.uniform(0.9, 1.1)
                        in_stock_prob = max(0.0, min(1.0, in_stock_prob))
                        
                        oos_flag = in_stock_prob < 0.3
                        
                        events.append({
                            "event_id": f"inv_{event_id_counter:08d}",
                            "sku_id": sku_id,
                            "store_id": store_id,
                            "event_time": event_time,
                            "in_stock_prob": round(in_stock_prob, 3),
                            "oos_flag": oos_flag
                        })
                        
                        event_id_counter += 1
            
            current_date += timedelta(days=1)
        
        return pd.DataFrame(events)
    
    def generate_support_events(self, orders_df: pd.DataFrame,
                               deliveries_df: pd.DataFrame,
                               items_df: pd.DataFrame) -> pd.DataFrame:
        """Generate support events based on order issues"""
        
        support_events = []
        ticket_id_counter = 1
        
        # Merge data
        merged = orders_df.merge(deliveries_df, on='order_id', how='left')
        merged = merged.merge(
            items_df.groupby('order_id').agg({
                'missing_flag': 'any',
                'substituted_flag': 'any'
            }).reset_index(),
            on='order_id',
            how='left'
        )
        
        for _, row in merged.iterrows():
            # Determine if support ticket should be created
            ticket_prob = 0.0
            
            # Late delivery increases ticket probability
            if not pd.isna(row.get('actual_eta')) and not pd.isna(row.get('promised_eta')):
                delay_minutes = (row['actual_eta'] - row['promised_eta']).total_seconds() / 60
                if delay_minutes > 10:
                    ticket_prob += 0.15
                elif delay_minutes > 5:
                    ticket_prob += 0.08
            
            # Missing items increase ticket probability
            if row.get('missing_flag', False):
                ticket_prob += 0.25
            
            # Substitutions increase ticket probability
            if row.get('substituted_flag', False):
                ticket_prob += 0.10
            
            # Cancellations always get tickets
            if row.get('canceled_flag', False):
                ticket_prob = 1.0
            
            # Generate ticket if probability threshold met
            if random.random() < ticket_prob:
                # Determine issue type
                if row.get('canceled_flag', False):
                    issue_type = "late"
                elif row.get('missing_flag', False):
                    issue_type = "missing_item"
                elif row.get('substituted_flag', False):
                    issue_type = "wrong_item"
                else:
                    issue_type = "late"
                
                # Ticket created shortly after delivery (or cancellation)
                if pd.isna(row.get('delivery_time')):
                    ticket_time = row['order_time'] + timedelta(hours=2)
                else:
                    ticket_time = row['delivery_time'] + timedelta(minutes=random.randint(30, 180))
                
                support_events.append({
                    "ticket_id": f"ticket_{ticket_id_counter:08d}",
                    "order_id": row['order_id'],
                    "issue_type": issue_type,
                    "ticket_created": ticket_time
                })
                
                ticket_id_counter += 1
        
        return pd.DataFrame(support_events)
    
    def generate_ratings(self, orders_df: pd.DataFrame,
                        deliveries_df: pd.DataFrame,
                        items_df: pd.DataFrame) -> pd.DataFrame:
        """Generate ratings correlated with CX"""
        
        ratings = []
        rating_id_counter = 1
        
        # Merge data
        merged = orders_df.merge(deliveries_df, on='order_id', how='left')
        merged = merged.merge(
            items_df.groupby('order_id').agg({
                'missing_flag': 'any',
                'substituted_flag': 'any',
                'refund_amount': 'sum'
            }).reset_index(),
            on='order_id',
            how='left'
        )
        
        # Only 30% of orders get ratings
        rating_rate = 0.3
        
        for _, row in merged.iterrows():
            if random.random() < rating_rate:
                # Base rating starts at 5
                stars = 5
                
                # Reduce rating based on issues
                # Late delivery
                if not pd.isna(row.get('actual_eta')) and not pd.isna(row.get('promised_eta')):
                    delay_minutes = (row['actual_eta'] - row['promised_eta']).total_seconds() / 60
                    if delay_minutes > 15:
                        stars -= 2
                    elif delay_minutes > 5:
                        stars -= 1
                
                # Missing items
                if row.get('missing_flag', False):
                    stars -= 1
                
                # Substitutions
                if row.get('substituted_flag', False):
                    stars -= 0.5
                
                # Cancellations
                if row.get('canceled_flag', False):
                    stars = 1
                
                # Ensure stars is between 1 and 5
                stars = max(1, min(5, int(stars)))
                
                # Generate rating time (within 24 hours of delivery)
                if pd.isna(row.get('delivery_time')):
                    rating_time = row['order_time'] + timedelta(hours=random.randint(2, 24))
                else:
                    rating_time = row['delivery_time'] + timedelta(hours=random.randint(1, 24))
                
                # Generate optional free text (20% chance)
                free_text = None
                if random.random() < 0.2:
                    if stars <= 2:
                        free_text = "Order was late and items were missing"
                    elif stars == 3:
                        free_text = "Order was okay but could be better"
                    else:
                        free_text = "Great service, fast delivery!"
                
                ratings.append({
                    "rating_id": f"rating_{rating_id_counter:08d}",
                    "order_id": row['order_id'],
                    "stars": stars,
                    "free_text": free_text,
                    "rating_time": rating_time
                })
                
                rating_id_counter += 1
        
        return pd.DataFrame(ratings)
    
    def generate_dataset(self, start_date: datetime, end_date: datetime,
                       orders_per_day: int = 10000,
                       batching_threshold: int = 2,
                       batching_change_date: Optional[datetime] = None,
                       prep_time_drift: float = 0.0,
                       inventory_degradation: float = 0.0) -> Dict[str, pd.DataFrame]:
        """Generate complete dataset"""
        
        print(f"Generating orders from {start_date} to {end_date}...")
        
        # Set batching policy
        if batching_change_date:
            self.delivery_gen.set_batching_threshold(batching_threshold, batching_change_date)
        else:
            self.delivery_gen.set_batching_threshold(batching_threshold)
        
        # Generate orders
        orders = self.order_gen.generate_orders(start_date, end_date, orders_per_day)
        orders_df = self.order_gen.to_dataframe(orders)
        print(f"Generated {len(orders_df)} orders")
        
        # Generate deliveries
        print("Generating deliveries...")
        deliveries = self.delivery_gen.generate_deliveries(orders_df, prep_time_drift)
        deliveries_df = self.delivery_gen.to_dataframe(deliveries)
        print(f"Generated {len(deliveries_df)} deliveries")
        
        # Generate inventory probabilities (for items)
        # Get unique stores and SKUs
        stores = orders_df['store_id'].unique().tolist()
        all_skus = []
        for skus in self.item_gen.sku_catalog.values():
            all_skus.extend(skus)
        skus = list(set(all_skus))
        
        # Generate inventory events
        print("Generating inventory events...")
        inventory_df = self.generate_inventory_events(
            start_date, end_date, stores, skus,
            base_in_stock_prob=0.85,
            degradation_rate=inventory_degradation
        )
        print(f"Generated {len(inventory_df)} inventory events")
        
        # Create inventory probability lookup
        # Use average inventory prob for each SKU-store combo
        inventory_probs = {}
        if len(inventory_df) > 0:
            # Group by store and SKU, take mean
            grouped = inventory_df.groupby(['store_id', 'sku_id'])['in_stock_prob'].mean()
            for (store_id, sku_id), prob in grouped.items():
                key = f"{store_id}_{sku_id}"
                inventory_probs[key] = prob
        
        # Fallback: use default probability if no inventory data
        default_prob = 0.85 - (inventory_degradation * (end_date - start_date).days)
        default_prob = max(0.1, min(1.0, default_prob))
        
        # Generate items
        print("Generating items...")
        items = self.item_gen.generate_items_for_orders(orders_df, inventory_probs)
        items_df = self.item_gen.to_dataframe(items)
        print(f"Generated {len(items_df)} items")
        
        # Generate support events
        print("Generating support events...")
        support_df = self.generate_support_events(orders_df, deliveries_df, items_df)
        print(f"Generated {len(support_df)} support events")
        
        # Generate ratings
        print("Generating ratings...")
        ratings_df = self.generate_ratings(orders_df, deliveries_df, items_df)
        print(f"Generated {len(ratings_df)} ratings")
        
        return {
            "orders": orders_df,
            "deliveries": deliveries_df,
            "items": items_df,
            "inventory_events": inventory_df,
            "support_events": support_df,
            "ratings": ratings_df
        }
    
    def save_dataset(self, dataset: Dict[str, pd.DataFrame], output_dir: str):
        """Save dataset to Parquet files"""
        os.makedirs(output_dir, exist_ok=True)
        
        for table_name, df in dataset.items():
            file_path = os.path.join(output_dir, f"{table_name}.parquet")
            df.to_parquet(file_path, index=False)
            print(f"Saved {table_name} to {file_path} ({len(df)} rows)")


if __name__ == "__main__":
    # Example usage
    generator = SyntheticDataGenerator(seed=42)
    
    # Generate baseline dataset
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 1, 31)  # 30 days
    
    dataset = generator.generate_dataset(
        start_date=start_date,
        end_date=end_date,
        orders_per_day=10000,
        batching_threshold=2
    )
    
    # Save to data/raw directory
    generator.save_dataset(dataset, "data/raw")


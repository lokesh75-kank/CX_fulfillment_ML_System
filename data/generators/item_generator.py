"""
Item Generator

Generates item data for orders, including substitutions, missing items,
and refunds correlated with inventory availability.
"""

import uuid
import random
from typing import List, Dict
import pandas as pd

from ..schemas.schema_definitions import ItemSchema


class ItemGenerator:
    """Generates synthetic item data"""
    
    def __init__(self, seed: int = 42):
        """Initialize generator with random seed"""
        random.seed(seed)
        
        # SKU catalog by category
        self.sku_catalog = {
            "grocery": [
                "sku_milk_2gal", "sku_bread_white", "sku_eggs_dozen",
                "sku_chicken_breast", "sku_bananas_lb", "sku_apples_lb",
                "sku_lettuce_head", "sku_tomatoes_lb", "sku_onions_lb",
                "sku_pasta_spaghetti", "sku_sauce_marinara", "sku_cheese_cheddar",
                "sku_yogurt_greek", "sku_cereal_cheerios", "sku_coffee_grounds"
            ],
            "convenience": [
                "sku_soda_coke", "sku_chips_lays", "sku_candy_snickers",
                "sku_water_bottle", "sku_sandwich_premade", "sku_coffee_ready",
                "sku_energy_drink", "sku_gum_trident", "sku_magazine_time"
            ],
            "retail": [
                "sku_shampoo_head", "sku_toothpaste_colgate", "sku_deodorant_dove",
                "sku_paper_towels", "sku_detergent_tide", "sku_batteries_aa",
                "sku_lightbulb_led", "sku_tape_scotch", "sku_bandages_brand"
            ]
        }
        
        # SKU prices (for refund calculations)
        self.sku_prices = {
            "sku_milk_2gal": 4.99,
            "sku_bread_white": 2.49,
            "sku_eggs_dozen": 3.99,
            "sku_chicken_breast": 8.99,
            "sku_bananas_lb": 0.79,
            "sku_apples_lb": 1.99,
            "sku_lettuce_head": 1.49,
            "sku_tomatoes_lb": 2.99,
            "sku_onions_lb": 0.99,
            "sku_pasta_spaghetti": 1.29,
            "sku_sauce_marinara": 2.99,
            "sku_cheese_cheddar": 4.49,
            "sku_yogurt_greek": 1.29,
            "sku_cereal_cheerios": 4.99,
            "sku_coffee_grounds": 7.99,
            "sku_soda_coke": 1.99,
            "sku_chips_lays": 3.49,
            "sku_candy_snickers": 1.29,
            "sku_water_bottle": 1.49,
            "sku_sandwich_premade": 5.99,
            "sku_coffee_ready": 2.99,
            "sku_energy_drink": 2.99,
            "sku_gum_trident": 1.49,
            "sku_magazine_time": 4.99,
            "sku_shampoo_head": 5.99,
            "sku_toothpaste_colgate": 3.99,
            "sku_deodorant_dove": 4.99,
            "sku_paper_towels": 8.99,
            "sku_detergent_tide": 12.99,
            "sku_batteries_aa": 5.99,
            "sku_lightbulb_led": 3.99,
            "sku_tape_scotch": 2.99,
            "sku_bandages_brand": 4.99,
        }
    
    def _get_items_per_order(self, category: str, basket_value: float) -> int:
        """Determine number of items based on category and basket value"""
        # Average item prices by category
        avg_prices = {
            "grocery": 3.50,
            "convenience": 2.50,
            "retail": 5.00
        }
        
        avg_price = avg_prices[category]
        num_items = max(1, int(basket_value / avg_price))
        
        # Add some randomness
        num_items = random.randint(max(1, num_items - 2), num_items + 2)
        
        return num_items
    
    def _should_substitute(self, in_stock_prob: float) -> bool:
        """Determine if item should be substituted"""
        # Higher substitution rate when in_stock_prob is low
        if in_stock_prob < 0.3:
            return random.random() < 0.4  # 40% substitution rate
        elif in_stock_prob < 0.6:
            return random.random() < 0.15  # 15% substitution rate
        else:
            return random.random() < 0.05  # 5% substitution rate
    
    def _should_missing(self, in_stock_prob: float) -> bool:
        """Determine if item should be missing"""
        # Missing items when in_stock_prob is very low
        if in_stock_prob < 0.2:
            return random.random() < 0.3  # 30% missing rate
        elif in_stock_prob < 0.5:
            return random.random() < 0.1  # 10% missing rate
        else:
            return random.random() < 0.02  # 2% missing rate
    
    def _calculate_refund(self, sku_id: str, missing_flag: bool, 
                         substituted_flag: bool) -> float:
        """Calculate refund amount"""
        if missing_flag:
            # Full refund for missing items
            return self.sku_prices.get(sku_id, 5.0)
        elif substituted_flag:
            # Partial refund (50%) for substitutions
            return self.sku_prices.get(sku_id, 5.0) * 0.5
        else:
            return 0.0
    
    def generate_items(self, order: Dict, inventory_probs: Dict[str, float] = None) -> List[ItemSchema]:
        """Generate items for a single order"""
        order_id = order['order_id']
        category = order['category']
        basket_value = order['basket_value']
        
        # Get number of items
        num_items = self._get_items_per_order(category, basket_value)
        
        # Get SKUs for this category
        available_skus = self.sku_catalog[category]
        
        items = []
        for i in range(num_items):
            # Select SKU
            sku_id = random.choice(available_skus)
            
            # Get inventory probability (default to high if not provided)
            in_stock_prob = inventory_probs.get(sku_id, 0.9) if inventory_probs else 0.9
            
            # Determine item status
            substituted_flag = self._should_substitute(in_stock_prob)
            missing_flag = self._should_missing(in_stock_prob) and not substituted_flag
            
            # Calculate refund
            refund_amount = self._calculate_refund(sku_id, missing_flag, substituted_flag)
            
            # Generate item
            item = ItemSchema(
                item_id=f"item_{uuid.uuid4().hex[:12]}",
                order_id=order_id,
                sku_id=sku_id,
                ordered_qty=random.randint(1, 3),
                substituted_flag=substituted_flag,
                missing_flag=missing_flag,
                refund_amount=round(refund_amount, 2)
            )
            
            items.append(item)
        
        return items
    
    def generate_items_for_orders(self, orders_df: pd.DataFrame,
                                  inventory_probs: Dict[str, float] = None) -> List[ItemSchema]:
        """Generate items for all orders"""
        all_items = []
        
        for _, order_row in orders_df.iterrows():
            order = order_row.to_dict()
            items = self.generate_items(order, inventory_probs)
            all_items.extend(items)
        
        return all_items
    
    def to_dataframe(self, items: List[ItemSchema]) -> pd.DataFrame:
        """Convert items to pandas DataFrame"""
        data = []
        for item in items:
            data.append({
                "item_id": item.item_id,
                "order_id": item.order_id,
                "sku_id": item.sku_id,
                "ordered_qty": item.ordered_qty,
                "substituted_flag": item.substituted_flag,
                "missing_flag": item.missing_flag,
                "refund_amount": item.refund_amount
            })
        return pd.DataFrame(data)


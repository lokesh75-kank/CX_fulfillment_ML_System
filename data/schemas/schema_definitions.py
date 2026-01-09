"""
Data Schema Definitions for CX-Fulfillment Agent

This module defines the schemas for all data tables used in the system.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class OrderSchema:
    """Schema for orders table"""
    order_id: str  # Primary key, UUID format
    user_id: str
    store_id: str
    category: str  # "grocery" | "convenience" | "retail"
    basket_value: float  # Total order value in USD
    promised_eta: datetime  # Promised delivery time
    order_time: datetime  # When order was placed
    region: str  # Geographic region (e.g., "SF", "NYC", "LA")
    time_of_day: str  # "breakfast" | "lunch" | "dinner" | "late-night"
    basket_size: str  # "small" | "medium" | "large" (derived from basket_value)


@dataclass
class DeliverySchema:
    """Schema for deliveries table"""
    order_id: str  # Foreign key to orders
    actual_eta: Optional[datetime]  # Actual delivery time (can be NULL if canceled)
    dasher_wait: int  # Dasher wait time at store (seconds)
    merchant_prep_time: int  # Merchant preparation time (seconds)
    distance: float  # Delivery distance (miles)
    batched_flag: bool  # Whether order was batched
    canceled_flag: bool  # Whether order was canceled
    delivery_time: Optional[datetime]  # When delivery completed (or canceled)
    dasher_id: Optional[str]  # Dasher identifier (optional)


@dataclass
class ItemSchema:
    """Schema for items table"""
    item_id: str  # Primary key, UUID format
    order_id: str  # Foreign key to orders
    sku_id: str  # Stock keeping unit identifier
    ordered_qty: int  # Quantity ordered
    substituted_flag: bool  # Whether item was substituted
    missing_flag: bool  # Whether item was missing
    refund_amount: float  # Refund amount for this item (USD)


@dataclass
class InventoryEventSchema:
    """Schema for inventory_events table"""
    event_id: str  # Primary key, UUID format
    sku_id: str  # Stock keeping unit identifier
    store_id: str  # Store identifier
    event_time: datetime  # When event occurred
    in_stock_prob: float  # Probability item is in stock (0-1)
    oos_flag: bool  # Out of stock flag


@dataclass
class SupportEventSchema:
    """Schema for support_events table"""
    ticket_id: str  # Primary key, UUID format
    order_id: str  # Foreign key to orders
    issue_type: str  # "late" | "missing_item" | "wrong_item" | "other"
    ticket_created: datetime  # When ticket was created


@dataclass
class RatingSchema:
    """Schema for ratings table"""
    rating_id: str  # Primary key, UUID format
    order_id: str  # Foreign key to orders
    stars: int  # Rating 1-5
    free_text: Optional[str]  # Optional feedback text
    rating_time: datetime  # When rating was submitted


# Schema validation constants
VALID_CATEGORIES = ["grocery", "convenience", "retail"]
VALID_TIME_OF_DAY = ["breakfast", "lunch", "dinner", "late-night"]
VALID_BASKET_SIZES = ["small", "medium", "large"]
VALID_REGIONS = ["SF", "NYC", "LA", "Chicago", "Boston"]
VALID_ISSUE_TYPES = ["late", "missing_item", "wrong_item", "other"]
VALID_RATING_STARS = [1, 2, 3, 4, 5]

# Basket size thresholds (USD)
BASKET_SIZE_THRESHOLDS = {
    "small": (0, 25),
    "medium": (25, 75),
    "large": (75, float('inf'))
}

# Time of day windows
TIME_OF_DAY_WINDOWS = {
    "breakfast": (6, 11),  # 6 AM - 11 AM
    "lunch": (11, 15),     # 11 AM - 3 PM
    "dinner": (17, 21),   # 5 PM - 9 PM
    "late-night": (21, 6)  # 9 PM - 6 AM (next day)
}


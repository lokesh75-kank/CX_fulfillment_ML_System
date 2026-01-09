# Data Schema Specification

## Overview

This document defines the complete data model for the CX-Fulfillment Agent system. All tables are designed to support realistic DoorDash-style operations with temporal relationships and correlations.

## Table Definitions

### 1. orders

**Purpose**: Core order information

**Schema**:
```python
{
    "order_id": str,           # Primary key, UUID format
    "user_id": str,            # User identifier
    "store_id": str,           # Store identifier
    "category": str,           # "grocery" | "convenience" | "retail"
    "basket_value": float,     # Total order value in USD
    "promised_eta": datetime,  # Promised delivery time
    "order_time": datetime,    # When order was placed
    "region": str,             # Geographic region (e.g., "SF", "NYC", "LA")
    "time_of_day": str,        # "breakfast" | "lunch" | "dinner" | "late-night"
    "basket_size": str         # "small" | "medium" | "large" (derived from basket_value)
}
```

**Constraints**:
- `order_id` must be unique
- `promised_eta` > `order_time`
- `basket_value` > 0
- `category` must be one of the allowed values

**Relationships**:
- One-to-many with `deliveries`
- One-to-many with `items`
- One-to-many with `support_events`
- One-to-one with `ratings`

**Sample Data**:
```
order_id: "ord_abc123"
user_id: "user_xyz789"
store_id: "store_sf_grocery_01"
category: "grocery"
basket_value: 45.99
promised_eta: "2024-01-04 19:30:00"
order_time: "2024-01-04 19:00:00"
region: "SF"
time_of_day: "dinner"
basket_size: "medium"
```

---

### 2. deliveries

**Purpose**: Delivery execution details

**Schema**:
```python
{
    "order_id": str,           # Foreign key to orders
    "actual_eta": datetime,    # Actual delivery time
    "dasher_wait": int,        # Dasher wait time at store (seconds)
    "merchant_prep_time": int, # Merchant preparation time (seconds)
    "distance": float,         # Delivery distance (miles)
    "batched_flag": bool,      # Whether order was batched
    "canceled_flag": bool,     # Whether order was canceled
    "delivery_time": datetime, # When delivery completed (or canceled)
    "dasher_id": str           # Dasher identifier (optional)
}
```

**Constraints**:
- `order_id` must exist in `orders`
- `actual_eta` can be NULL if `canceled_flag` is True
- `merchant_prep_time` >= 0
- `distance` >= 0

**Relationships**:
- Many-to-one with `orders`

**Correlations** (for realistic data generation):
- `batched_flag` → higher `dasher_wait`, potentially higher `actual_eta`
- `merchant_prep_time` drift → `actual_eta` misses
- `distance` → affects `actual_eta` vs `promised_eta`

**Sample Data**:
```
order_id: "ord_abc123"
actual_eta: "2024-01-04 19:45:00"
dasher_wait: 300
merchant_prep_time: 1200
distance: 2.5
batched_flag: True
canceled_flag: False
delivery_time: "2024-01-04 19:45:00"
dasher_id: "dasher_001"
```

---

### 3. items

**Purpose**: Individual items in orders

**Schema**:
```python
{
    "item_id": str,            # Primary key, UUID format
    "order_id": str,           # Foreign key to orders
    "sku_id": str,             # Stock keeping unit identifier
    "ordered_qty": int,        # Quantity ordered
    "substituted_flag": bool,  # Whether item was substituted
    "missing_flag": bool,      # Whether item was missing
    "refund_amount": float     # Refund amount for this item (USD)
}
```

**Constraints**:
- `item_id` must be unique
- `order_id` must exist in `orders`
- `ordered_qty` > 0
- `refund_amount` >= 0
- If `missing_flag` is True, `refund_amount` > 0 typically

**Relationships**:
- Many-to-one with `orders`
- Many-to-one with `inventory_events` (via `sku_id`)

**Sample Data**:
```
item_id: "item_001"
order_id: "ord_abc123"
sku_id: "sku_milk_2gal"
ordered_qty: 1
substituted_flag: False
missing_flag: False
refund_amount: 0.0
```

---

### 4. inventory_events

**Purpose**: Inventory availability events (simulated)

**Schema**:
```python
{
    "event_id": str,           # Primary key, UUID format
    "sku_id": str,             # Stock keeping unit identifier
    "store_id": str,           # Store identifier
    "event_time": datetime,    # When event occurred
    "in_stock_prob": float,    # Probability item is in stock (0-1)
    "oos_flag": bool           # Out of stock flag
}
```

**Constraints**:
- `in_stock_prob` between 0 and 1
- `oos_flag` is True when `in_stock_prob` < threshold (e.g., 0.3)

**Relationships**:
- Many-to-many with `items` (via `sku_id`)

**Usage**:
- Used to simulate inventory availability
- Correlates with `substituted_flag` and `missing_flag` in `items`
- Can show inventory degradation over time

**Sample Data**:
```
event_id: "inv_001"
sku_id: "sku_milk_2gal"
store_id: "store_sf_grocery_01"
event_time: "2024-01-04 19:00:00"
in_stock_prob: 0.85
oos_flag: False
```

---

### 5. support_events

**Purpose**: Customer support ticket events (simulated)

**Schema**:
```python
{
    "ticket_id": str,          # Primary key, UUID format
    "order_id": str,           # Foreign key to orders
    "issue_type": str,         # "late" | "missing_item" | "wrong_item" | "other"
    "ticket_created": datetime # When ticket was created
}
```

**Constraints**:
- `order_id` must exist in `orders`
- `issue_type` must be one of the allowed values

**Relationships**:
- Many-to-one with `orders`

**Correlations**:
- `issue_type: "late"` correlates with `actual_eta` > `promised_eta`
- `issue_type: "missing_item"` correlates with `missing_flag` in `items`

**Sample Data**:
```
ticket_id: "ticket_001"
order_id: "ord_abc123"
issue_type: "late"
ticket_created: "2024-01-04 20:00:00"
```

---

### 6. ratings

**Purpose**: Customer ratings and feedback

**Schema**:
```python
{
    "rating_id": str,          # Primary key, UUID format
    "order_id": str,           # Foreign key to orders
    "stars": int,              # Rating 1-5
    "free_text": str,          # Optional feedback text
    "rating_time": datetime    # When rating was submitted
}
```

**Constraints**:
- `order_id` must exist in `orders`
- `stars` between 1 and 5
- `free_text` can be NULL

**Relationships**:
- One-to-one with `orders` (one rating per order, optional)

**Correlations**:
- Low `stars` correlates with:
  - Late deliveries (`actual_eta` > `promised_eta`)
  - Missing/wrong items
  - Cancellations

**Sample Data**:
```
rating_id: "rating_001"
order_id: "ord_abc123"
stars: 3
free_text: "Order was late but items were correct"
rating_time: "2024-01-04 20:30:00"
```

---

## Temporal Relationships

### Order Lifecycle

```
order_time (orders)
    ↓
[merchant_prep_time] (deliveries)
    ↓
promised_eta (orders)
    ↓
actual_eta (deliveries)
    ↓
delivery_time (deliveries)
    ↓
rating_time (ratings, optional)
    ↓
ticket_created (support_events, optional)
```

### Key Time Windows

- **Prep time**: `merchant_prep_time` seconds after `order_time`
- **Delivery window**: `promised_eta` ± 5 minutes (on-time threshold)
- **Rating window**: Typically within 24 hours of `delivery_time`
- **Support window**: Typically within 48 hours of `delivery_time`

## Data Generation Rules

### Realistic Patterns

1. **Batching Impact**:
   - `batched_flag = True` → `dasher_wait` increases (300-900 seconds)
   - `batched_flag = True` → higher chance of `actual_eta` > `promised_eta`

2. **Prep Time Drift**:
   - `merchant_prep_time` can drift over time (policy change simulation)
   - Drift → `actual_eta` misses → lower on-time rate

3. **Inventory Degradation**:
   - `in_stock_prob` decreases over time (for demo scenario)
   - Low `in_stock_prob` → higher `substituted_flag` or `missing_flag`

4. **Category Differences**:
   - Grocery: Higher basket value, more items, longer prep time
   - Convenience: Lower basket value, fewer items, shorter prep time
   - Retail: Medium basket value, variable items

5. **Time-of-Day Patterns**:
   - Dinner (6-8pm): Peak hours, higher volume, more batching
   - Late-night: Lower volume, longer prep times
   - Breakfast: Quick prep, shorter distances

6. **Region Differences**:
   - Urban (SF, NYC): Shorter distances, higher density
   - Suburban: Longer distances, lower density

## Data Quality Constraints

### Referential Integrity
- All foreign keys must reference existing records
- Cascade deletes not needed (historical data preserved)

### Data Types
- All timestamps in UTC
- All monetary values in USD
- All durations in seconds
- All distances in miles

### Null Handling
- `actual_eta` can be NULL if `canceled_flag = True`
- `free_text` can be NULL in `ratings`
- All other fields are required

## Sample Dataset Size

**For MVP Demo**:
- 30 days of data
- ~10,000 orders per day = 300,000 orders total
- ~3 items per order = 900,000 items
- ~1 delivery per order = 300,000 deliveries
- ~50,000 inventory events per day = 1.5M events
- ~5% support rate = 15,000 support events
- ~30% rating rate = 90,000 ratings

**File Sizes** (estimated):
- orders.parquet: ~50 MB
- deliveries.parquet: ~40 MB
- items.parquet: ~60 MB
- inventory_events.parquet: ~80 MB
- support_events.parquet: ~5 MB
- ratings.parquet: ~10 MB

**Total**: ~245 MB (compressed Parquet)

## Data Generation Script Structure

```python
# synthetic_data_generator.py

def generate_orders(start_date, end_date, num_orders_per_day):
    """Generate orders with realistic patterns"""
    pass

def generate_deliveries(orders_df):
    """Generate deliveries correlated with orders"""
    pass

def generate_items(orders_df):
    """Generate items for each order"""
    pass

def generate_inventory_events(start_date, end_date):
    """Generate inventory availability events"""
    pass

def generate_support_events(orders_df, deliveries_df):
    """Generate support tickets based on issues"""
    pass

def generate_ratings(orders_df, deliveries_df):
    """Generate ratings correlated with CX"""
    pass

def apply_policy_change(date, change_type):
    """Simulate policy change (e.g., batching threshold)"""
    pass
```

## Validation Queries

### Data Quality Checks

```python
# Check referential integrity
assert all(order_id in orders['order_id'] 
           for order_id in deliveries['order_id'])

# Check temporal consistency
assert all(delivery['actual_eta'] >= order['order_time']
           for order, delivery in zip(orders, deliveries))

# Check metric calculations
assert all(0 <= prob <= 1 
           for prob in inventory_events['in_stock_prob'])
```


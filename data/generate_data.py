"""
Synthetic MochaMate cafe sales data generator.
Produces realistic transactional data with seasonal trends,
peak-hour patterns, and menu item popularity distributions.

Usage: python data/generate_data.py
Output: data/cafe_sales.csv
"""
from __future__ import annotations

import random
import csv
from datetime import datetime, timedelta
from pathlib import Path

random.seed(42)

MENU = {
    "Espresso":          {"price": 3.50,  "category": "Coffee",   "popularity": 0.10},
    "Cappuccino":        {"price": 4.75,  "category": "Coffee",   "popularity": 0.14},
    "Latte":             {"price": 5.25,  "category": "Coffee",   "popularity": 0.16},
    "Cold Brew":         {"price": 5.50,  "category": "Coffee",   "popularity": 0.12},
    "Matcha Latte":      {"price": 6.00,  "category": "Specialty","popularity": 0.08},
    "Caramel Macchiato": {"price": 5.75,  "category": "Specialty","popularity": 0.07},
    "Croissant":         {"price": 3.25,  "category": "Pastry",   "popularity": 0.09},
    "Blueberry Muffin":  {"price": 3.75,  "category": "Pastry",   "popularity": 0.08},
    "Avocado Toast":     {"price": 9.50,  "category": "Food",     "popularity": 0.07},
    "Breakfast Burrito": {"price": 10.50, "category": "Food",     "popularity": 0.06},
    "Sparkling Water":   {"price": 2.50,  "category": "Beverage", "popularity": 0.03},
}

# Hourly traffic weights (07:00 – 20:00)
HOURLY_WEIGHTS = {
    7: 3, 8: 9, 9: 8, 10: 5, 11: 4, 12: 7,
    13: 6, 14: 4, 15: 5, 16: 4, 17: 3, 18: 2, 19: 1, 20: 1,
}

# Weekend boost factor
WEEKEND_BOOST = 1.35

# Seasonal multipliers
SEASONAL = {1: 0.85, 2: 0.88, 3: 0.92, 4: 0.97, 5: 1.02, 6: 1.10,
            7: 1.08, 8: 1.05, 9: 0.98, 10: 0.95, 11: 1.12, 12: 1.18}

PAYMENT_METHODS = ["Credit Card", "Debit Card", "Cash", "Mobile Pay"]
LOYALTY_RATE    = 0.42   # 42% of customers have loyalty cards


def _daily_base_orders(date: datetime) -> int:
    """Estimate daily order volume with seasonal and weekday variation."""
    base       = 120
    seasonal   = SEASONAL[date.month]
    weekend    = WEEKEND_BOOST if date.weekday() >= 5 else 1.0
    noise      = random.uniform(0.92, 1.08)
    return int(base * seasonal * weekend * noise)


def _sample_hour() -> int:
    hours   = list(HOURLY_WEIGHTS.keys())
    weights = list(HOURLY_WEIGHTS.values())
    return random.choices(hours, weights=weights)[0]


def _sample_item() -> tuple[str, dict]:
    items   = list(MENU.keys())
    weights = [MENU[i]["popularity"] for i in items]
    name    = random.choices(items, weights=weights)[0]
    return name, MENU[name]


def generate(start: str = "2024-01-01",
             end:   str = "2024-12-31",
             output: str = "data/cafe_sales.csv") -> None:

    Path(output).parent.mkdir(parents=True, exist_ok=True)
    start_dt = datetime.strptime(start, "%Y-%m-%d")
    end_dt   = datetime.strptime(end,   "%Y-%m-%d")

    rows = []
    order_id = 1000

    current = start_dt
    while current <= end_dt:
        n_orders = _daily_base_orders(current)
        for _ in range(n_orders):
            hour    = _sample_hour()
            minute  = random.randint(0, 59)
            second  = random.randint(0, 59)
            ts      = current.replace(hour=hour, minute=minute, second=second)

            item_name, item = _sample_item()
            qty   = random.choices([1, 2, 3], weights=[0.75, 0.20, 0.05])[0]
            price = item["price"]

            # Apply occasional discount
            discount = random.choices([0, 0.10, 0.15, 0.20],
                                      weights=[0.70, 0.15, 0.10, 0.05])[0]
            total = round(price * qty * (1 - discount), 2)

            rows.append({
                "order_id":       order_id,
                "timestamp":      ts.strftime("%Y-%m-%d %H:%M:%S"),
                "date":           ts.strftime("%Y-%m-%d"),
                "time":           ts.strftime("%H:%M:%S"),
                "hour":           hour,
                "day_of_week":    ts.strftime("%A"),
                "is_weekend":     ts.weekday() >= 5,
                "month":          ts.month,
                "month_name":     ts.strftime("%B"),
                "item_name":      item_name,
                "category":       item["category"],
                "unit_price":     price,
                "quantity":       qty,
                "discount_pct":   int(discount * 100),
                "total_revenue":  total,
                "payment_method": random.choice(PAYMENT_METHODS),
                "loyalty_card":   random.random() < LOYALTY_RATE,
            })
            order_id += 1
        current += timedelta(days=1)

    fieldnames = list(rows[0].keys())
    with open(output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Generated {len(rows):,} orders -> {output}")


if __name__ == "__main__":
    generate()

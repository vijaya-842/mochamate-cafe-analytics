"""
Core analytics engine for MochaMate cafe data.
Provides revenue analysis, menu performance, customer behaviour,
and operational KPIs used by the Tableau dashboard.
"""
from __future__ import annotations

import pandas as pd
import numpy as np
from pathlib import Path


class CafeAnalytics:
    """Encapsulates all analytical computations on the cafe dataset."""

    def __init__(self, csv_path: str = "data/cafe_sales.csv") -> None:
        self.df = self._load_and_clean(csv_path)

    # ── Data loading ─────────────────────────────────────────────────────────

    def _load_and_clean(self, path: str) -> pd.DataFrame:
        df = pd.read_csv(path, parse_dates=["timestamp", "date"])
        df["date"]        = pd.to_datetime(df["date"])
        df["is_weekend"]  = df["is_weekend"].astype(bool)
        df["loyalty_card"]= df["loyalty_card"].astype(bool)
        df["week"]        = df["date"].dt.isocalendar().week.astype(int)
        df["quarter"]     = df["date"].dt.quarter
        return df

    # ── Revenue KPIs ─────────────────────────────────────────────────────────

    def total_revenue(self) -> float:
        return round(self.df["total_revenue"].sum(), 2)

    def avg_order_value(self) -> float:
        return round(self.df.groupby("order_id")["total_revenue"].sum().mean(), 2)

    def revenue_by_month(self) -> pd.DataFrame:
        return (self.df.groupby(["month", "month_name"])["total_revenue"]
                .sum().reset_index()
                .rename(columns={"total_revenue": "revenue"})
                .sort_values("month"))

    def revenue_by_quarter(self) -> pd.DataFrame:
        return (self.df.groupby("quarter")["total_revenue"]
                .agg(revenue="sum", orders="count")
                .reset_index())

    def mom_growth(self) -> pd.DataFrame:
        monthly = self.revenue_by_month()
        monthly["prev_revenue"] = monthly["revenue"].shift(1)
        monthly["mom_growth_pct"] = (
            (monthly["revenue"] - monthly["prev_revenue"])
            / monthly["prev_revenue"] * 100
        ).round(2)
        return monthly

    # ── Menu performance ─────────────────────────────────────────────────────

    def top_items_by_revenue(self, n: int = 10) -> pd.DataFrame:
        return (self.df.groupby(["item_name", "category"])
                .agg(total_revenue=("total_revenue", "sum"),
                     total_orders=("order_id", "count"),
                     avg_price=("unit_price", "mean"))
                .reset_index()
                .sort_values("total_revenue", ascending=False)
                .head(n)
                .round(2))

    def category_breakdown(self) -> pd.DataFrame:
        total = self.df["total_revenue"].sum()
        cat = (self.df.groupby("category")["total_revenue"]
               .sum().reset_index()
               .rename(columns={"total_revenue": "revenue"}))
        cat["revenue_pct"] = (cat["revenue"] / total * 100).round(2)
        return cat.sort_values("revenue", ascending=False)

    def underperforming_items(self, threshold_pct: float = 2.0) -> pd.DataFrame:
        items = self.top_items_by_revenue(n=len(self.df["item_name"].unique()))
        total = items["total_revenue"].sum()
        items["rev_pct"] = (items["total_revenue"] / total * 100).round(2)
        return items[items["rev_pct"] < threshold_pct]

    # ── Peak-hour & day analysis ──────────────────────────────────────────────

    def orders_by_hour(self) -> pd.DataFrame:
        return (self.df.groupby("hour")
                .agg(orders=("order_id", "count"),
                     revenue=("total_revenue", "sum"))
                .reset_index().round(2))

    def peak_hours(self, top_n: int = 3) -> list[int]:
        return (self.orders_by_hour()
                .nlargest(top_n, "orders")["hour"]
                .tolist())

    def orders_by_day(self) -> pd.DataFrame:
        day_order = ["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"]
        df = (self.df.groupby("day_of_week")
              .agg(orders=("order_id", "count"),
                   revenue=("total_revenue", "sum"))
              .reset_index())
        df["day_of_week"] = pd.Categorical(df["day_of_week"], categories=day_order, ordered=True)
        return df.sort_values("day_of_week").round(2)

    def weekend_vs_weekday(self) -> pd.DataFrame:
        return (self.df.groupby("is_weekend")
                .agg(orders=("order_id", "count"),
                     revenue=("total_revenue", "sum"),
                     avg_order=("total_revenue", "mean"))
                .reset_index()
                .assign(segment=lambda x: x["is_weekend"].map({True:"Weekend", False:"Weekday"}))
                .drop(columns="is_weekend").round(2))

    # ── Customer & loyalty ────────────────────────────────────────────────────

    def loyalty_impact(self) -> pd.DataFrame:
        return (self.df.groupby("loyalty_card")
                .agg(orders=("order_id", "count"),
                     revenue=("total_revenue", "sum"),
                     avg_order=("total_revenue", "mean"))
                .reset_index()
                .assign(segment=lambda x: x["loyalty_card"].map({True:"Loyalty", False:"Non-loyalty"}))
                .drop(columns="loyalty_card").round(2))

    def payment_distribution(self) -> pd.DataFrame:
        return (self.df.groupby("payment_method")
                .agg(orders=("order_id", "count"),
                     revenue=("total_revenue", "sum"))
                .reset_index()
                .sort_values("orders", ascending=False).round(2))

    # ── Full KPI summary ──────────────────────────────────────────────────────

    def kpi_summary(self) -> dict:
        return {
            "total_revenue_usd":    self.total_revenue(),
            "total_orders":         len(self.df),
            "avg_order_value_usd":  self.avg_order_value(),
            "best_selling_item":    self.top_items_by_revenue(1)["item_name"].iloc[0],
            "peak_hours":           self.peak_hours(),
            "loyalty_card_pct":     round(self.df["loyalty_card"].mean() * 100, 1),
            "top_category":         self.category_breakdown()["category"].iloc[0],
        }

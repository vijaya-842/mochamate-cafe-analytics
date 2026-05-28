"""
Chart generation for MochaMate analytics.
All charts are saved as PNG files in the output/ directory.
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

OUTPUT_DIR = Path("output/charts")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

PALETTE = ["#2D6A4F", "#40916C", "#52B788", "#74C69D", "#95D5B2",
           "#B7E4C7", "#D8F3DC", "#1B4332", "#081C15"]
ACCENT  = "#2D6A4F"

plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor":   "white",
    "axes.spines.top":  False,
    "axes.spines.right":False,
    "font.family":      "DejaVu Sans",
})


def _save(fig: plt.Figure, name: str) -> None:
    path = OUTPUT_DIR / f"{name}.png"
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {path}")


def plot_monthly_revenue(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(12, 5))
    bars = ax.bar(df["month_name"], df["revenue"], color=PALETTE[:len(df)], edgecolor="white")
    ax.bar_label(bars, labels=[f"${v:,.0f}" for v in df["revenue"]], padding=4, fontsize=9)
    ax.set_title("Monthly Revenue — 2024", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Month"); ax.set_ylabel("Revenue (USD)")
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
    plt.xticks(rotation=30, ha="right")
    _save(fig, "monthly_revenue")


def plot_top_items(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(10, 6))
    colors  = [PALETTE[i % len(PALETTE)] for i in range(len(df))]
    bars    = ax.barh(df["item_name"], df["total_revenue"], color=colors)
    ax.bar_label(bars, labels=[f"${v:,.0f}" for v in df["total_revenue"]], padding=4, fontsize=9)
    ax.set_title("Top Menu Items by Revenue", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlabel("Total Revenue (USD)")
    ax.invert_yaxis()
    _save(fig, "top_items_revenue")


def plot_hourly_orders(df: pd.DataFrame) -> None:
    fig, ax1 = plt.subplots(figsize=(12, 5))
    ax2 = ax1.twinx()
    ax1.bar(df["hour"], df["orders"], color=ACCENT, alpha=0.75, label="Orders")
    ax2.plot(df["hour"], df["revenue"], color="#E76F51", linewidth=2.5,
             marker="o", markersize=5, label="Revenue")
    ax1.set_xlabel("Hour of Day"); ax1.set_ylabel("Number of Orders")
    ax2.set_ylabel("Revenue (USD)")
    ax1.set_title("Hourly Order Volume & Revenue", fontsize=14, fontweight="bold", pad=15)
    ax1.set_xticks(df["hour"]); ax1.set_xticklabels([f"{h:02d}:00" for h in df["hour"]], rotation=45)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right")
    _save(fig, "hourly_orders")


def plot_category_pie(df: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(
        df["revenue"], labels=df["category"],
        colors=PALETTE[:len(df)], autopct="%1.1f%%",
        startangle=140, pctdistance=0.82,
        wedgeprops={"edgecolor": "white", "linewidth": 2},
    )
    for at in autotexts:
        at.set_fontsize(10); at.set_fontweight("bold")
    ax.set_title("Revenue by Category", fontsize=14, fontweight="bold", pad=15)
    _save(fig, "category_breakdown")


def plot_weekend_vs_weekday(df: pd.DataFrame) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, col, title in zip(axes, ["orders", "avg_order"], ["Total Orders", "Avg Order Value ($)"]):
        colors = [PALETTE[0], PALETTE[2]]
        bars   = ax.bar(df["segment"], df[col], color=colors, edgecolor="white", width=0.5)
        ax.bar_label(bars, padding=4, fontsize=10, fmt="%.0f")
        ax.set_title(title, fontsize=12, fontweight="bold")
        ax.set_xlabel("")
    fig.suptitle("Weekday vs Weekend Comparison", fontsize=14, fontweight="bold")
    plt.tight_layout()
    _save(fig, "weekend_vs_weekday")


def generate_all(analytics) -> None:
    print("Generating charts...")
    plot_monthly_revenue(analytics.revenue_by_month())
    plot_top_items(analytics.top_items_by_revenue())
    plot_hourly_orders(analytics.orders_by_hour())
    plot_category_pie(analytics.category_breakdown())
    plot_weekend_vs_weekday(analytics.weekend_vs_weekday())
    print("All charts saved to output/charts/")

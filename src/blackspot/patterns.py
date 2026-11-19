"""Pattern analysis and chart generation for temporal and vehicle distributions."""

from pathlib import Path
from typing import Any, Dict, List, Optional
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

# Palette inspired by clean modern UI
CHART_COLOR = "#3D5A80"
ACCENT_COLOR = "#EE6C4D"
GRID_COLOR = "#E0E0E0"


def counts_by(df: pd.DataFrame, column: str) -> pd.Series:
    """Compute value counts for time_bucket, weekday, or exploded vehicle_types.

    Args:
        df: Input DataFrame.
        column: Column to aggregate ('time_bucket', 'weekday', 'vehicle_types').

    Returns:
        Pandas Series of counts.
    """
    if column not in df.columns or df.empty:
        return pd.Series(dtype=int)

    if column == "vehicle_types":
        all_vehicles: List[str] = []
        for val in df["vehicle_types"].dropna():
            parts = str(val).replace(",", ";").split(";")
            all_vehicles.extend([p.strip().lower() for p in parts if p.strip()])
        return pd.Series(all_vehicles).value_counts()

    return df[column].dropna().astype(str).value_counts()


def _style_axis(ax: plt.Axes, title: str, xlabel: str, ylabel: str) -> None:
    """Apply clean, modern styling to a matplotlib axis."""
    ax.set_title(title, fontsize=12, fontweight="bold", pad=12, color="#293241")
    ax.set_xlabel(xlabel, fontsize=10, labelpad=8, color="#293241")
    ax.set_ylabel(ylabel, fontsize=10, labelpad=8, color="#293241")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#CCCCCC")
    ax.spines["bottom"].set_color("#CCCCCC")
    ax.grid(axis="y", linestyle="--", alpha=0.4, color=GRID_COLOR)
    ax.tick_params(colors="#293241", labelsize=9)


def save_charts(
    df: pd.DataFrame,
    clusters: pd.DataFrame,
    out_dir: str | Path,
) -> List[Path]:
    """Generate and save PNG bar charts for overall patterns and top 5 clusters.

    Generates:
    - overall_time_bucket.png
    - overall_weekday.png
    - overall_vehicle.png
    - cluster_<id>_time_bucket.png (for each of top 5 clusters)

    Args:
        df: Clean accidents DataFrame.
        clusters: Ranked clusters DataFrame.
        out_dir: Directory where chart images are saved.

    Returns:
        List of generated file paths.
    """
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    generated: List[Path] = []

    # Filter to active accidents
    active = df.copy()
    if "dup_of" in active.columns:
        active = active[active["dup_of"].isna()]

    # 1. Overall by time bucket
    tb_counts = counts_by(active, "time_bucket")
    fig, ax = plt.subplots(figsize=(6, 4))
    if not tb_counts.empty:
        tb_counts.plot(kind="bar", ax=ax, color=CHART_COLOR, edgecolor="none", width=0.6)
    _style_axis(ax, "Accidents by Time of Day", "Time Bucket", "Count")
    plt.xticks(rotation=0)
    plt.tight_layout()
    p1 = out_path / "overall_time_bucket.png"
    plt.savefig(p1, dpi=150)
    plt.close(fig)
    generated.append(p1)

    # 2. Overall by weekday
    wd_counts = counts_by(active, "weekday")
    # Order weekdays if possible
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    if not wd_counts.empty:
        reordered = [d for d in day_order if d in wd_counts.index]
        if reordered:
            wd_counts = wd_counts.reindex(reordered + [d for d in wd_counts.index if d not in day_order])

    fig, ax = plt.subplots(figsize=(7, 4))
    if not wd_counts.empty:
        wd_counts.plot(kind="bar", ax=ax, color="#48CAE4", edgecolor="none", width=0.6)
    _style_axis(ax, "Accidents by Day of Week", "Day", "Count")
    plt.xticks(rotation=30)
    plt.tight_layout()
    p2 = out_path / "overall_weekday.png"
    plt.savefig(p2, dpi=150)
    plt.close(fig)
    generated.append(p2)

    # 3. Overall by vehicle type
    veh_counts = counts_by(active, "vehicle_types")
    fig, ax = plt.subplots(figsize=(7, 4))
    if not veh_counts.empty:
        veh_counts.head(10).plot(kind="bar", ax=ax, color="#F4A261", edgecolor="none", width=0.6)
    _style_axis(ax, "Accidents by Vehicle Type", "Vehicle", "Count")
    plt.xticks(rotation=30)
    plt.tight_layout()
    p3 = out_path / "overall_vehicle.png"
    plt.savefig(p3, dpi=150)
    plt.close(fig)
    generated.append(p3)

    # 4. Top 5 clusters time bucket charts
    if not clusters.empty:
        top5 = clusters.head(5)
        for _, c_row in top5.iterrows():
            c_id = int(c_row["cluster_id"])
            c_label = str(c_row["label"])
            c_accidents = active[active["cluster_id"] == c_id]
            c_tb = counts_by(c_accidents, "time_bucket")

            fig, ax = plt.subplots(figsize=(6, 4))
            if not c_tb.empty:
                c_tb.plot(kind="bar", ax=ax, color=ACCENT_COLOR, edgecolor="none", width=0.5)
            _style_axis(ax, f"Cluster {c_id} ({c_label[:20]}): Time Breakdown", "Time Bucket", "Count")
            plt.xticks(rotation=0)
            plt.tight_layout()
            cp = out_path / f"cluster_{c_id}_time_bucket.png"
            plt.savefig(cp, dpi=150)
            plt.close(fig)
            generated.append(cp)

    return generated

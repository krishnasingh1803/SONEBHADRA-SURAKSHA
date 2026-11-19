"""Accident and cluster severity scoring and ranking module."""

from typing import Any, Dict, List, Optional, Tuple
import pandas as pd
from blackspot.geo import haversine_m


def accident_severity(
    killed: Any,
    injured: Any,
    cfg: Optional[Dict[str, Any]] = None,
) -> float:
    """Calculate severity score for an individual accident record.

    score = w_killed * killed + w_injured * injured, or w_none when both are 0 or unknown.

    Args:
        killed: Number of deaths (numeric or NaN/None).
        injured: Number of injuries (numeric or NaN/None).
        cfg: Configuration dictionary containing score weights.

    Returns:
        Float severity score.
    """
    score_cfg = (cfg or {}).get("score", {})
    w_killed = float(score_cfg.get("w_killed", 3.0))
    w_injured = float(score_cfg.get("w_injured", 1.0))
    w_none = float(score_cfg.get("w_none", 0.5))

    k = 0.0
    i = 0.0
    if pd.notna(killed):
        try:
            k = max(0.0, float(killed))
        except (ValueError, TypeError):
            k = 0.0

    if pd.notna(injured):
        try:
            i = max(0.0, float(injured))
        except (ValueError, TypeError):
            i = 0.0

    if k == 0.0 and i == 0.0:
        return w_none

    return w_killed * k + w_injured * i


def rank_clusters(
    df: pd.DataFrame,
    cfg: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:
    """Group clustered accidents, compute statistics, and rank by severity score.

    Args:
        df: DataFrame with 'cluster_id', 'lat', 'lon', 'killed', 'injured', etc.
        cfg: Configuration dictionary.

    Returns:
        DataFrame containing ranked clusters sorted by score descending.
    """
    cols = [
        "cluster_id",
        "n_accidents",
        "killed",
        "injured",
        "score",
        "centroid_lat",
        "centroid_lon",
        "radius_m",
        "peak_time_bucket",
        "peak_weekday",
        "top_vehicle",
        "label",
        "rank_by_score",
        "rank_by_count",
    ]

    if "cluster_id" not in df.columns or df.empty:
        return pd.DataFrame(columns=cols)

    # Filter out noise (-1) and duplicates
    mask = (df["cluster_id"] >= 0) & df["lat"].notna() & df["lon"].notna()
    if "dup_of" in df.columns:
        mask = mask & df["dup_of"].isna()

    clustered_pts = df[mask].copy()
    if clustered_pts.empty:
        return pd.DataFrame(columns=cols)

    records: List[Dict[str, Any]] = []

    for c_id, group in clustered_pts.groupby("cluster_id"):
        n_accidents = len(group)
        k_total = int(group["killed"].fillna(0).astype(float).sum())
        i_total = int(group["injured"].fillna(0).astype(float).sum())

        # Total cluster score = sum of scores of accidents in cluster
        c_score = sum(
            accident_severity(r.get("killed"), r.get("injured"), cfg)
            for _, r in group.iterrows()
        )

        c_lat = float(group["lat"].mean())
        c_lon = float(group["lon"].mean())

        # Radius is max distance from centroid
        radius = max(
            haversine_m(c_lat, c_lon, float(r["lat"]), float(r["lon"]))
            for _, r in group.iterrows()
        )

        # Peak time bucket
        tb_series = group["time_bucket"].dropna() if "time_bucket" in group.columns else pd.Series(dtype=str)
        tb_mode = tb_series.mode().iloc[0] if not tb_series.empty else "unknown"

        # Peak weekday
        wd_series = group["weekday"].dropna() if "weekday" in group.columns else pd.Series(dtype=str)
        wd_mode = wd_series.mode().iloc[0] if not wd_series.empty else "unknown"

        # Top vehicle
        all_vehicles = []
        if "vehicle_types" in group.columns:
            for v in group["vehicle_types"].dropna():
                parts = str(v).replace(",", ";").split(";")
                all_vehicles.extend([p.strip().lower() for p in parts if p.strip()])
        top_v = pd.Series(all_vehicles).mode().iloc[0] if all_vehicles else "unknown"

        # Label is the most common place_text
        labels = group["place_text"].dropna().astype(str).str.strip()
        c_label = labels.mode().iloc[0] if not labels.empty else f"Cluster {c_id}"

        records.append(
            {
                "cluster_id": int(c_id),
                "n_accidents": n_accidents,
                "killed": k_total,
                "injured": i_total,
                "score": round(float(c_score), 2),
                "centroid_lat": round(c_lat, 6),
                "centroid_lon": round(c_lon, 6),
                "radius_m": round(float(radius), 1),
                "peak_time_bucket": tb_mode,
                "peak_weekday": wd_mode,
                "top_vehicle": top_v,
                "label": c_label,
            }
        )

    res_df = pd.DataFrame(records)
    if res_df.empty:
        return pd.DataFrame(columns=cols)

    # Rank by score descending
    res_df = res_df.sort_values(by=["score", "n_accidents"], ascending=[False, False]).reset_index(drop=True)
    res_df["rank_by_score"] = res_df.index + 1

    # Rank by count descending
    res_df["rank_by_count"] = (
        res_df["n_accidents"].rank(ascending=False, method="min").astype(int)
    )

    return res_df[cols]


def compare_top5_rankings(ranked_df: pd.DataFrame) -> bool:
    """Check whether the top 5 clusters by score equal top 5 by count.

    Args:
        ranked_df: DataFrame returned by rank_clusters.

    Returns:
        Boolean indicating whether top 5 sets are identical.
    """
    if len(ranked_df) < 5:
        top_score = set(ranked_df.sort_values("rank_by_score")["cluster_id"])
        top_count = set(ranked_df.sort_values("rank_by_count")["cluster_id"])
        return top_score == top_count

    top_score = set(ranked_df.sort_values("rank_by_score").head(5)["cluster_id"])
    top_count = set(ranked_df.sort_values("rank_by_count").head(5)["cluster_id"])
    return top_score == top_count

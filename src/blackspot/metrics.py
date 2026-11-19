"""Validation metrics: geocode accuracy checking and temporal split cluster validation."""

from pathlib import Path
from typing import Any, Dict, Optional
import numpy as np
import pandas as pd
from blackspot.cluster import run_dbscan
from blackspot.geo import haversine_m


def make_geocode_sample(
    df: pd.DataFrame,
    n: int = 30,
    seed: int = 42,
    out_path: str | Path = "outputs/verification/geocode_check.csv",
) -> Path:
    """Sample records for human ground-truth coordinate verification.

    Args:
        df: Geocoded DataFrame.
        n: Number of samples to draw (default 30).
        seed: Random seed for reproducibility (default 42).
        out_path: Destination path for sample CSV.

    Returns:
        Path to generated CSV file.
    """
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)

    valid = df[df["lat"].notna() & df["lon"].notna()].copy()
    sample_size = min(n, len(valid))
    if sample_size > 0:
        sampled = valid.sample(n=sample_size, random_state=seed)
    else:
        sampled = valid

    check_df = pd.DataFrame()
    check_df["id"] = sampled["id"] if "id" in sampled.columns else []
    check_df["place_text"] = sampled["place_text"] if "place_text" in sampled.columns else []
    check_df["lat"] = sampled["lat"] if "lat" in sampled.columns else []
    check_df["lon"] = sampled["lon"] if "lon" in sampled.columns else []
    check_df["true_lat"] = ""
    check_df["true_lon"] = ""

    check_df.to_csv(p, index=False)
    return p


def geocode_accuracy(
    path: str | Path = "outputs/verification/geocode_check.csv",
    within_m: float = 200.0,
) -> Dict[str, Any]:
    """Evaluate geocode accuracy from human ground-truth coordinates.

    Args:
        path: Path to geocode_check.csv.
        within_m: Error threshold in meters (default 200m).

    Returns:
        Dictionary with count checked, share within threshold, and median error.
    """
    p = Path(path)
    if not p.exists():
        return {"checked_count": 0, "accuracy_share": "TBD", "median_error_m": "TBD"}

    df = pd.read_csv(p)
    if "true_lat" not in df.columns or "true_lon" not in df.columns:
        return {"checked_count": 0, "accuracy_share": "TBD", "median_error_m": "TBD"}

    # Drop rows without ground-truth numbers
    df["true_lat_num"] = pd.to_numeric(df["true_lat"], errors="coerce")
    df["true_lon_num"] = pd.to_numeric(df["true_lon"], errors="coerce")
    filled = df.dropna(subset=["lat", "lon", "true_lat_num", "true_lon_num"])

    count_checked = len(filled)
    if count_checked == 0:
        return {"checked_count": 0, "accuracy_share": "TBD", "median_error_m": "TBD"}

    errors_m = [
        haversine_m(float(r["lat"]), float(r["lon"]), float(r["true_lat_num"]), float(r["true_lon_num"]))
        for _, r in filled.iterrows()
    ]

    within_count = sum(1 for e in errors_m if e <= within_m)
    share_within = round(within_count / count_checked, 3)
    median_err = round(float(np.median(errors_m)), 1)

    return {
        "checked_count": count_checked,
        "accuracy_share": share_within,
        "median_error_m": median_err,
    }


def time_split_hit_rate(
    df: pd.DataFrame,
    cfg: Optional[Dict[str, Any]] = None,
    train_fraction: float = 0.67,
    seed: int = 42,
) -> Dict[str, Any]:
    """Test if historical blackspots predict future accident locations.

    Args:
        df: Clean accidents DataFrame.
        cfg: Configuration dictionary with cluster parameters.
        train_fraction: Split ratio for train/test by date (default 0.67).
        seed: Random seed for baseline points (default 42).

    Returns:
        Dictionary with hit_rate and baseline_hit_rate.
    """
    active = df[df["lat"].notna() & df["lon"].notna()].copy()
    if "dup_of" in active.columns:
        active = active[active["dup_of"].isna()]

    if len(active) < 5:
        return {"hit_rate": 0.0, "baseline_hit_rate": 0.0, "test_count": 0, "n_train_clusters": 0}

    # Sort chronologically
    active["parsed_date"] = pd.to_datetime(active["date"], errors="coerce")
    sorted_df = active.sort_values("parsed_date").reset_index(drop=True)

    split_idx = int(len(sorted_df) * train_fraction)
    train_df = sorted_df.iloc[:split_idx].copy()
    test_df = sorted_df.iloc[split_idx:].copy()

    if train_df.empty or test_df.empty:
        return {"hit_rate": 0.0, "baseline_hit_rate": 0.0, "test_count": len(test_df), "n_train_clusters": 0}

    cluster_cfg = (cfg or {}).get("cluster", {})
    eps_m = float(cluster_cfg.get("eps_m", 300.0))
    min_samples = int(cluster_cfg.get("min_samples", 3))

    train_clustered = run_dbscan(train_df, eps_m=eps_m, min_samples=min_samples)
    centroids = []
    for _, g in train_clustered[train_clustered["cluster_id"] >= 0].groupby("cluster_id"):
        centroids.append((float(g["lat"].mean()), float(g["lon"].mean())))

    if not centroids:
        return {"hit_rate": 0.0, "baseline_hit_rate": 0.0, "test_count": len(test_df), "n_train_clusters": 0}

    # Test hit rate
    hits = 0
    test_lats = test_df["lat"].to_numpy(dtype=float)
    test_lons = test_df["lon"].to_numpy(dtype=float)

    for lat, lon in zip(test_lats, test_lons):
        min_dist = min(haversine_m(lat, lon, c_lat, c_lon) for c_lat, c_lon in centroids)
        if min_dist <= eps_m:
            hits += 1

    hit_rate = round(hits / len(test_df), 3)

    # Random baseline inside data bounding box
    rng = np.random.default_rng(seed)
    min_lat, max_lat = float(sorted_df["lat"].min()), float(sorted_df["lat"].max())
    min_lon, max_lon = float(sorted_df["lon"].min()), float(sorted_df["lon"].max())

    baseline_points = list(
        zip(
            rng.uniform(min_lat, max_lat, size=len(centroids)),
            rng.uniform(min_lon, max_lon, size=len(centroids)),
        )
    )

    b_hits = 0
    for lat, lon in zip(test_lats, test_lons):
        min_dist = min(haversine_m(lat, lon, b_lat, b_lon) for b_lat, b_lon in baseline_points)
        if min_dist <= eps_m:
            b_hits += 1

    b_hit_rate = round(b_hits / len(test_df), 3)

    return {
        "hit_rate": hit_rate,
        "baseline_hit_rate": b_hit_rate,
        "test_count": len(test_df),
        "n_train_clusters": len(centroids),
    }

"""Spatial clustering of accidents using DBSCAN with haversine distance."""

from typing import Any, Dict, List, Optional
import numpy as np
import pandas as pd
from sklearn.cluster import DBSCAN
from blackspot.geo import EARTH_RADIUS_M, haversine_m


def run_dbscan(
    df: pd.DataFrame,
    eps_m: float = 300.0,
    min_samples: int = 3,
) -> pd.DataFrame:
    """Cluster accident points using DBSCAN with haversine metric on radian coordinates.

    Args:
        df: DataFrame containing 'lat' and 'lon' columns.
        eps_m: Distance threshold in meters.
        min_samples: Minimum points required to form a core cluster.

    Returns:
        DataFrame with an added 'cluster_id' column (-1 for noise).
    """
    df_out = df.copy()
    if "cluster_id" not in df_out.columns:
        df_out["cluster_id"] = -1

    # Filter eligible points: must have valid lat and lon, and not be a dropped duplicate
    mask = df_out["lat"].notna() & df_out["lon"].notna()
    if "dup_of" in df_out.columns:
        mask = mask & df_out["dup_of"].isna()

    eligible_indices = df_out[mask].index
    if len(eligible_indices) == 0:
        return df_out

    coords = df_out.loc[eligible_indices, ["lat", "lon"]].to_numpy(dtype=float)
    radians_coords = np.radians(coords)
    eps_rad = eps_m / EARTH_RADIUS_M

    db = DBSCAN(eps=eps_rad, min_samples=min_samples, metric="haversine", algorithm="ball_tree")
    labels = db.fit_predict(radians_coords)

    df_out.loc[eligible_indices, "cluster_id"] = labels
    return df_out


def sensitivity(
    df: pd.DataFrame,
    eps_list: List[float],
    min_samples: int = 3,
    top_n: int = 5,
    cfg: Optional[Dict[str, Any]] = None,
) -> pd.DataFrame:
    """Analyze cluster stability across multiple eps values.

    Args:
        df: DataFrame with accidents.
        eps_list: List of eps thresholds in meters (e.g., [200, 300, 500]).
        min_samples: Minimum cluster samples.
        top_n: Number of top clusters to evaluate.
        cfg: Configuration dictionary for scoring weights.

    Returns:
        DataFrame with columns ['eps_m', 'n_clusters', 'noise_share', 'overlap_with_base'].
    """
    from blackspot.score import rank_clusters

    # Base eps is typically 300m or the middle/first element
    base_eps = 300.0 if 300.0 in eps_list else eps_list[0]

    # Precompute runs
    cluster_results: Dict[float, pd.DataFrame] = {}
    top_centroids: Dict[float, List[tuple[float, float]]] = {}
    metrics_by_eps: Dict[float, Dict[str, Any]] = {}

    for eps in eps_list:
        clustered = run_dbscan(df, eps_m=eps, min_samples=min_samples)
        eligible = clustered[clustered["lat"].notna() & clustered["lon"].notna()]
        if "dup_of" in clustered.columns:
            eligible = eligible[eligible["dup_of"].isna()]

        total_pts = len(eligible)
        noise_pts = (eligible["cluster_id"] == -1).sum()
        noise_share = round(float(noise_pts / total_pts), 3) if total_pts > 0 else 0.0

        ranked = rank_clusters(clustered, cfg or {})
        top = ranked.head(top_n)

        centroids = list(zip(top["centroid_lat"], top["centroid_lon"])) if not top.empty else []
        top_centroids[eps] = centroids
        metrics_by_eps[eps] = {
            "n_clusters": len(ranked),
            "noise_share": noise_share,
        }

    base_centroids = top_centroids.get(base_eps, [])
    records = []

    for eps in eps_list:
        n_clusters = metrics_by_eps[eps]["n_clusters"]
        noise_share = metrics_by_eps[eps]["noise_share"]

        # Count how many of base top clusters have centroid within base_eps meters of this eps top clusters
        overlap_count = 0
        if base_centroids and top_centroids[eps]:
            for b_lat, b_lon in base_centroids:
                for t_lat, t_lon in top_centroids[eps]:
                    if haversine_m(b_lat, b_lon, t_lat, t_lon) <= base_eps:
                        overlap_count += 1
                        break
        elif not base_centroids and not top_centroids[eps]:
            overlap_count = 0

        records.append(
            {
                "eps_m": int(eps),
                "n_clusters": n_clusters,
                "noise_share": noise_share,
                "overlap_with_base": overlap_count,
            }
        )

    return pd.DataFrame(records)

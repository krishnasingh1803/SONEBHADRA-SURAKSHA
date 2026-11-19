"""Tests for DBSCAN clustering (B7.5)."""

import pandas as pd
from blackspot.cluster import run_dbscan


def test_dbscan_clustering_and_noise():
    """5 points within 50 m plus 1 point 5 km away, with eps 300 m and min_samples 3, give exactly 1 cluster and 1 noise point."""
    base_lat = 27.50000
    base_lon = 77.60000

    # 5 points within 50m (0.0001 deg lat is ~11 meters)
    points = [
        {"id": 1, "lat": base_lat, "lon": base_lon},
        {"id": 2, "lat": base_lat + 0.0001, "lon": base_lon},
        {"id": 3, "lat": base_lat, "lon": base_lon + 0.0001},
        {"id": 4, "lat": base_lat - 0.0001, "lon": base_lon},
        {"id": 5, "lat": base_lat, "lon": base_lon - 0.0001},
        # 1 point 5 km away (~0.045 degrees lat)
        {"id": 6, "lat": base_lat + 0.045, "lon": base_lon},
    ]
    df = pd.DataFrame(points)

    clustered = run_dbscan(df, eps_m=300.0, min_samples=3)

    # Cluster labels: unique labels excluding -1
    labels = clustered["cluster_id"].tolist()
    unique_clusters = set(l for l in labels if l != -1)
    noise_count = labels.count(-1)

    assert len(unique_clusters) == 1, f"Expected exactly 1 cluster, got {unique_clusters}"
    assert noise_count == 1, f"Expected exactly 1 noise point, got {noise_count}"
    assert clustered.loc[clustered["id"] == 6, "cluster_id"].values[0] == -1
    assert all(clustered.loc[clustered["id"] == i, "cluster_id"].values[0] == 0 for i in range(1, 6))

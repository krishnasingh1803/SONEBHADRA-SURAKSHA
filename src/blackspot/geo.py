"""Geographical distance and spatial calculations using Haversine formula."""

import math
from typing import List, Tuple
import numpy as np
import pandas as pd

EARTH_RADIUS_M = 6371000.0


def haversine_m(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate the great-circle distance between two points in meters.

    Args:
        lat1: Latitude of point 1 in degrees.
        lon1: Longitude of point 1 in degrees.
        lat2: Latitude of point 2 in degrees.
        lon2: Longitude of point 2 in degrees.

    Returns:
        Distance in meters.
    """
    if lat1 == lat2 and lon1 == lon2:
        return 0.0

    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = (
        math.sin(dphi / 2.0) ** 2
        + math.cos(phi1) * math.cos(phi2) * (math.sin(dlambda / 2.0) ** 2)
    )
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(max(0.0, 1.0 - a)))
    return EARTH_RADIUS_M * c


def pairwise_within(df: pd.DataFrame, max_m: float) -> List[Tuple[int, int]]:
    """Find index pairs of records located within max_m meters of each other.

    Args:
        df: DataFrame containing 'lat' and 'lon' columns.
        max_m: Maximum distance threshold in meters.

    Returns:
        List of index tuples (idx_a, idx_b) with idx_a < idx_b.
    """
    valid = df.dropna(subset=["lat", "lon"])
    indices = valid.index.tolist()
    n = len(indices)
    if n < 2:
        return []

    lats = valid["lat"].to_numpy(dtype=float)
    lons = valid["lon"].to_numpy(dtype=float)

    pairs: List[Tuple[int, int]] = []
    for i in range(n):
        lat_i, lon_i = lats[i], lons[i]
        for j in range(i + 1, n):
            dist = haversine_m(lat_i, lon_i, lats[j], lons[j])
            if dist <= max_m:
                pairs.append((indices[i], indices[j]))

    return pairs

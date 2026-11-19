"""Tests for geographic distance calculations (B7.1)."""

import pytest
from blackspot.geo import haversine_m, pairwise_within
import pandas as pd


def test_haversine_same_point():
    """Same point returns 0."""
    dist = haversine_m(27.4924, 77.6737, 27.4924, 77.6737)
    assert dist == 0.0


def test_haversine_approx_one_km():
    """Two points about 1 km apart return within 5% of the expected distance."""
    # 1 km north along meridian: approx 1000m / 111139m/deg ≈ 0.00900 degrees latitude
    lat1, lon1 = 27.4924, 77.6737
    # 0.00899 degrees latitude is ~1000 meters
    lat2, lon2 = lat1 + 0.008993, lon1
    dist = haversine_m(lat1, lon1, lat2, lon2)

    expected = 1000.0
    error_percent = abs(dist - expected) / expected * 100
    assert error_percent < 5.0, f"Expected ~1000m within 5%, got {dist}m"


def test_pairwise_within():
    """Find index pairs within given distance."""
    df = pd.DataFrame(
        {
            "lat": [27.5000, 27.5005, 27.6000],  # Point 0 & 1 are ~55m apart; point 2 is ~11km away
            "lon": [77.6000, 77.6000, 77.6000],
        }
    )
    pairs = pairwise_within(df, max_m=100.0)
    assert pairs == [(0, 1)]

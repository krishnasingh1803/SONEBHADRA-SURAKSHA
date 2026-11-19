"""Tests for duplicate detection and merging rules (B7.4)."""

import pandas as pd
from blackspot.dedup import find_duplicates, merge_duplicates


def test_dedup_criteria():
    """Verify max_m, max_day_gap, and vehicle overlap criteria."""
    # 0.000899 deg latitude is ~100m. 0.0036 deg is ~400m.
    base_lat = 27.5000
    base_lon = 77.6000

    # Pair 1: Same date and 100m apart with overlapping vehicles -> duplicate
    # Pair 2: One day apart and 100m apart with overlapping vehicles -> duplicate
    # Pair 3: Two days apart -> not a duplicate
    # Pair 4: 400m apart -> not a duplicate
    df = pd.DataFrame(
        [
            # Reference
            {
                "id": 1,
                "date": "2026-05-10",
                "lat": base_lat,
                "lon": base_lon,
                "vehicle_types": "truck;bike",
                "injured": 1,
                "killed": 0,
                "source_url": "https://example.com/1",
            },
            # 100m away, same date, overlapping vehicles (bike)
            {
                "id": 2,
                "date": "2026-05-10",
                "lat": base_lat + 0.0009,
                "lon": base_lon,
                "vehicle_types": "bike;car",
                "injured": 2,
                "killed": 0,
                "source_url": "https://example.com/2",
            },
            # 100m away, 1 day apart, overlapping vehicles
            {
                "id": 3,
                "date": "2026-05-11",
                "lat": base_lat + 0.0009,
                "lon": base_lon,
                "vehicle_types": "bike",
                "injured": 0,
                "killed": 1,
                "source_url": "https://example.com/3",
            },
            # 100m away, 2 days apart -> NOT duplicate of 1
            {
                "id": 4,
                "date": "2026-05-12",
                "lat": base_lat + 0.0009,
                "lon": base_lon,
                "vehicle_types": "bike",
                "injured": 0,
                "killed": 0,
                "source_url": "https://example.com/4",
            },
            # 400m away, same date as 1 -> NOT duplicate of 1
            {
                "id": 5,
                "date": "2026-05-10",
                "lat": base_lat + 0.0036,
                "lon": base_lon,
                "vehicle_types": "truck;bike",
                "injured": 0,
                "killed": 0,
                "source_url": "https://example.com/5",
            },
        ]
    )

    pairs = find_duplicates(df, max_m=300.0, max_day_gap=1)
    pair_tuples = list(zip(pairs["id_a"], pairs["id_b"]))

    # Pair (1, 2): same date, ~100m, overlapping vehicle -> duplicate
    assert (1, 2) in pair_tuples
    # Pair (1, 3): 1 day apart, ~100m, overlapping vehicle -> duplicate
    assert (1, 3) in pair_tuples
    # Pair (1, 4): 2 days apart -> NOT duplicate
    assert (1, 4) not in pair_tuples
    # Pair (1, 5): 400m apart -> NOT duplicate
    assert (1, 5) not in pair_tuples


def test_chain_merges_into_one_record():
    """A chain A~B~C merges into one record."""
    df = pd.DataFrame(
        [
            {"id": 1, "date": "2026-05-10", "lat": 27.5, "lon": 77.6, "injured": 1, "killed": 0, "source_url": "https://a.com"},
            {"id": 2, "date": "2026-05-10", "lat": 27.5, "lon": 77.6, "injured": 3, "killed": 0, "source_url": "https://b.com"},
            {"id": 3, "date": "2026-05-10", "lat": 27.5, "lon": 77.6, "injured": 0, "killed": 2, "source_url": "https://c.com"},
        ]
    )
    # Pairs indicating A~B and B~C
    pairs = pd.DataFrame([{"id_a": 1, "id_b": 2}, {"id_a": 2, "id_b": 3}])
    merged = merge_duplicates(df, pairs)

    # Active records (dup_of is null)
    active = merged[merged["dup_of"].isna()]
    assert len(active) == 1
    root = active.iloc[0]
    assert root["id"] == 1
    # Max casualties taken
    assert root["injured"] == 3
    assert root["killed"] == 2
    # Records 2 and 3 marked as duplicate of 1
    assert merged.loc[merged["id"] == 2, "dup_of"].values[0] == 1
    assert merged.loc[merged["id"] == 3, "dup_of"].values[0] == 1

"""Tests for scoring and cluster ranking (B7.6)."""

import pandas as pd
from blackspot.score import accident_severity, rank_clusters


def test_accident_severity_calculation():
    """killed 1 and injured 2 gives 5. Killed 0 and injured 0 gives 0.5."""
    cfg = {"score": {"w_killed": 3.0, "w_injured": 1.0, "w_none": 0.5}}

    score1 = accident_severity(killed=1, injured=2, cfg=cfg)
    assert score1 == 5.0

    score2 = accident_severity(killed=0, injured=0, cfg=cfg)
    assert score2 == 0.5


def test_rank_clusters_sorted_descending():
    """rank_clusters returns clusters sorted by score descending."""
    cfg = {"score": {"w_killed": 3.0, "w_injured": 1.0, "w_none": 0.5}}

    # Cluster 0: low score (0 killed, 1 injured -> 1.0)
    # Cluster 1: high score (2 killed, 1 injured -> 7.0)
    data = [
        # Cluster 0
        {"cluster_id": 0, "lat": 27.50, "lon": 77.60, "killed": 0, "injured": 1, "place_text": "Junction A"},
        {"cluster_id": 0, "lat": 27.50, "lon": 77.60, "killed": 0, "injured": 0, "place_text": "Junction A"},
        # Cluster 1
        {"cluster_id": 1, "lat": 27.60, "lon": 77.70, "killed": 2, "injured": 1, "place_text": "Highway B"},
        {"cluster_id": 1, "lat": 27.60, "lon": 77.70, "killed": 1, "injured": 1, "place_text": "Highway B"},
    ]
    df = pd.DataFrame(data)

    ranked = rank_clusters(df, cfg)
    assert not ranked.empty
    scores = ranked["score"].tolist()
    assert scores == sorted(scores, reverse=True)
    assert ranked.iloc[0]["cluster_id"] == 1
    assert ranked.iloc[0]["rank_by_score"] == 1

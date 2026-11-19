"""Tests for geocoding with caching, bbox rejection, and manual overrides (B7.3)."""

from unittest.mock import MagicMock
import pandas as pd
from blackspot.geocode import geocode_place, apply_overrides


def test_geocode_caching_makes_no_second_api_call():
    """A second call with the same query makes no API call."""
    mock_geocoder = MagicMock()
    mock_loc = MagicMock()
    mock_loc.latitude = 27.50
    mock_loc.longitude = 77.68
    mock_geocoder.geocode.return_value = mock_loc

    cache = {}
    bbox = (27.0, 77.0, 28.0, 78.0)

    # First call - queries mock geocoder
    res1 = geocode_place("Bhuteshwar, Mathura", mock_geocoder, bbox, cache)
    assert res1.quality == "exact"
    assert mock_geocoder.geocode.call_count == 1

    # Second call with identical query string
    res2 = geocode_place("Bhuteshwar, Mathura", mock_geocoder, bbox, cache)
    assert res2.quality == "exact"
    assert res2.lat == 27.50
    # API call count remains 1 because cache was hit
    assert mock_geocoder.geocode.call_count == 1


def test_geocode_outside_bbox_returns_failed():
    """A result outside the bounding box returns failed."""
    mock_geocoder = MagicMock()
    mock_loc = MagicMock()
    mock_loc.latitude = 28.7041  # Delhi, outside Mathura bounding box
    mock_loc.longitude = 77.1025
    mock_geocoder.geocode.return_value = mock_loc

    cache = {}
    bbox = (27.1, 77.2, 27.9, 77.9)  # Mathura district bbox

    res = geocode_place("Connaught Place", mock_geocoder, bbox, cache)
    assert res.quality == "failed"
    assert res.lat is None
    assert res.lon is None


def test_apply_overrides_replaces_and_sets_manual(tmp_path):
    """An override replaces coordinates and sets manual."""
    overrides_file = tmp_path / "geocode_overrides.csv"
    overrides_file.write_text("id,lat,lon,note\n10,27.5123,77.6432,Verified junction\n")

    df = pd.DataFrame(
        [
            {"id": 10, "lat": 27.1000, "lon": 77.1000, "geocode_quality": "approximate"},
            {"id": 11, "lat": 27.2000, "lon": 77.2000, "geocode_quality": "exact"},
        ]
    )

    df_out = apply_overrides(df, overrides_file)
    row10 = df_out[df_out["id"] == 10].iloc[0]
    row11 = df_out[df_out["id"] == 11].iloc[0]

    assert row10["lat"] == 27.5123
    assert row10["lon"] == 77.6432
    assert row10["geocode_quality"] == "manual"

    # Row 11 unchanged
    assert row11["lat"] == 27.2000
    assert row11["geocode_quality"] == "exact"

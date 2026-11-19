"""Tests for validation rules (B7.2)."""

import pandas as pd
from blackspot.validate import validate


def _valid_row():
    return {
        "id": 1,
        "date": "2026-05-10",
        "time": "14:30",
        "place_text": "NH-19 Toll Plaza",
        "district": "Mathura",
        "vehicle_types": "truck;bike",
        "injured": 1,
        "killed": 0,
        "source_url": "https://example.com/news/1",
        "source_name": "Amar Ujala",
        "other_sources": "",
    }


def test_clean_row_gives_none():
    """A clean row gives none (0 errors, 0 warnings)."""
    df = pd.DataFrame([_valid_row()])
    cfg = {"district": "Mathura"}
    report = validate(df, cfg)
    assert len(report.errors) == 0
    assert len(report.warnings) == 0
    assert report.n_valid == 1


def test_missing_source_url_gives_error():
    """Missing source_url gives an error."""
    row = _valid_row()
    row["source_url"] = ""
    df = pd.DataFrame([row])
    report = validate(df, {"district": "Mathura"})
    assert len(report.errors) > 0
    assert any("source_url" in e.lower() for e in report.errors)
    assert report.n_valid == 0


def test_negative_killed_gives_error():
    """Negative killed gives an error."""
    row = _valid_row()
    row["killed"] = -1
    df = pd.DataFrame([row])
    report = validate(df, {"district": "Mathura"})
    assert len(report.errors) > 0
    assert any("killed" in e.lower() for e in report.errors)
    assert report.n_valid == 0


def test_synthetic_row_gives_warning():
    """A SYNTHETIC row gives a warning."""
    row = _valid_row()
    row["source_name"] = "SYNTHETIC"
    df = pd.DataFrame([row])
    report = validate(df, {"district": "Mathura"})
    assert len(report.errors) == 0
    assert len(report.warnings) > 0
    assert any("synthetic" in w.lower() for w in report.warnings)
    assert report.n_valid == 1

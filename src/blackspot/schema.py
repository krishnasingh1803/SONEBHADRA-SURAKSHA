"""Schema definitions and column specifications for accident data."""

from typing import Any, Dict, List, Optional

RAW_COLUMNS: List[str] = [
    "id",
    "date",
    "time",
    "place_text",
    "district",
    "vehicle_types",
    "injured",
    "killed",
    "source_url",
    "source_name",
    "other_sources",
]

CLEAN_COLUMNS: List[str] = RAW_COLUMNS + [
    "lat",
    "lon",
    "geocode_quality",
    "time_bucket",
    "weekday",
    "dup_of",
    "cluster_id",
]

ALLOWED_GEOCODE_QUALITY: List[str] = ["exact", "approximate", "manual", "failed"]


def bucket_for_hour(hour: int, time_buckets: Optional[Dict[str, List[int]]] = None) -> str:
    """Determine time bucket for a given 24-hour hour integer (0-23).

    Handles the wrap-around night bucket (e.g., [21, 4]).

    Args:
        hour: Hour of the day in integer format (0-23).
        time_buckets: Mapping of bucket name to [start_hour, end_hour].

    Returns:
        Bucket name such as 'morning', 'afternoon', 'evening', or 'night'.
    """
    if time_buckets is None:
        time_buckets = {
            "morning": [5, 11],
            "afternoon": [12, 16],
            "evening": [17, 20],
            "night": [21, 4],
        }

    for name, span in time_buckets.items():
        start, end = span[0], span[1]
        if start <= end:
            if start <= hour <= end:
                return name
        else:
            # Wrap-around across midnight (e.g. 21 to 4)
            if hour >= start or hour <= end:
                return name

    return "unknown"

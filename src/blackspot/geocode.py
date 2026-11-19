"""Geocoding module with bounding-box gating, multi-query fallback, caching, and manual overrides."""

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple
import pandas as pd

try:
    from geopy.geocoders import Nominatim
    from geopy.extra.rate_limiter import RateLimiter
except ImportError:
    Nominatim = None
    RateLimiter = None


@dataclass
class GeocodeResult:
    """Result of geocoding a location string."""

    lat: Optional[float]
    lon: Optional[float]
    quality: str  # 'exact', 'approximate', 'manual', 'failed'
    query_used: Optional[str]


def build_queries(
    place_text: str,
    district: str = "Mathura",
    country: str = "India",
) -> List[str]:
    """Build fallback queries ordered from most to least specific.

    Order:
    1. Full place_text + district + country
    2. Landmark only (text after near/at/opposite/के पास/पास) + district + country
    3. Last comma-separated part + district + country

    Args:
        place_text: Raw place description.
        district: Name of the district.
        country: Name of the country.

    Returns:
        List of unique query strings ordered from most to least specific.
    """
    queries: List[str] = []
    clean_place = place_text.strip()
    if not clean_place:
        return []

    # 1. Full text
    q1 = f"{clean_place}, {district}, {country}"
    queries.append(q1)

    # 2. Text after landmark keywords
    pattern = r"(?:near|at|opposite|के\s*पास|पास)\s+(.+)"
    match = re.search(pattern, clean_place, flags=re.IGNORECASE)
    if match:
        landmark = match.group(1).strip()
        if landmark:
            q2 = f"{landmark}, {district}, {country}"
            if q2 not in queries:
                queries.append(q2)

    # 3. Last comma-separated part
    parts = [p.strip() for p in clean_place.split(",") if p.strip()]
    if len(parts) > 1:
        last_part = parts[-1]
        q3 = f"{last_part}, {district}, {country}"
        if q3 not in queries:
            queries.append(q3)

    return queries


def district_bbox(
    geocoder: Any,
    district: str = "Mathura",
    country: str = "India",
    margin_km: float = 5.0,
    cache_path: Optional[Path | str] = None,
) -> Tuple[float, float, float, float]:
    """Compute and cache district bounding box expanded by margin_km.

    Returns:
        Tuple of (min_lat, min_lon, max_lat, max_lon).
    """
    # Mathura default district bounds if offline or fallback needed
    default_bounds = (27.1, 77.2, 27.9, 77.9)
    margin_deg = margin_km / 111.0

    if geocoder is None:
        return (
            default_bounds[0] - margin_deg,
            default_bounds[1] - margin_deg,
            default_bounds[2] + margin_deg,
            default_bounds[3] + margin_deg,
        )

    try:
        loc = geocoder.geocode(f"{district}, {country}")
        if loc and "boundingbox" in loc.raw:
            raw_box = loc.raw["boundingbox"]
            min_lat = float(raw_box[0]) - margin_deg
            max_lat = float(raw_box[1]) + margin_deg
            min_lon = float(raw_box[2]) - margin_deg
            max_lon = float(raw_box[3]) + margin_deg
            return (min_lat, min_lon, max_lat, max_lon)
    except Exception:
        pass

    return (
        default_bounds[0] - margin_deg,
        default_bounds[1] - margin_deg,
        default_bounds[2] + margin_deg,
        default_bounds[3] + margin_deg,
    )


def geocode_place(
    place_text: str,
    geocoder: Any,
    bbox: Tuple[float, float, float, float],
    cache: Dict[str, Dict[str, Any]],
    district: str = "Mathura",
    country: str = "India",
) -> GeocodeResult:
    """Geocode a place string trying queries in order with bbox checking and caching.

    Args:
        place_text: Location text to geocode.
        geocoder: Geopy geocoder instance or callable mock.
        bbox: (min_lat, min_lon, max_lat, max_lon).
        cache: Query string to {'lat': float, 'lon': float} dictionary.
        district: District name.
        country: Country name.

    Returns:
        GeocodeResult.
    """
    queries = build_queries(place_text, district, country)
    if not queries:
        return GeocodeResult(lat=None, lon=None, quality="failed", query_used=None)

    min_lat, min_lon, max_lat, max_lon = bbox

    for idx, query in enumerate(queries):
        lat, lon = None, None
        if query in cache:
            cached_data = cache[query]
            if cached_data is not None:
                lat = cached_data.get("lat")
                lon = cached_data.get("lon")
        else:
            if geocoder is not None:
                try:
                    loc = geocoder.geocode(query)
                    if loc:
                        lat, lon = float(loc.latitude), float(loc.longitude)
                        cache[query] = {"lat": lat, "lon": lon}
                    else:
                        cache[query] = None
                except Exception:
                    cache[query] = None
            else:
                cache[query] = None

        if lat is not None and lon is not None:
            # Check bounding box
            if min_lat <= lat <= max_lat and min_lon <= lon <= max_lon:
                quality = "exact" if idx == 0 else "approximate"
                return GeocodeResult(lat=lat, lon=lon, quality=quality, query_used=query)

    return GeocodeResult(lat=None, lon=None, quality="failed", query_used=None)


def apply_overrides(df: pd.DataFrame, overrides_path: str | Path) -> pd.DataFrame:
    """Apply manual coordinate overrides to DataFrame.

    Args:
        df: DataFrame with 'id', 'lat', 'lon', 'geocode_quality'.
        overrides_path: Path to geocode_overrides.csv.

    Returns:
        Updated DataFrame with overridden coordinates and quality='manual'.
    """
    p = Path(overrides_path)
    if not p.exists():
        return df

    overrides = pd.read_csv(p)
    if overrides.empty or "id" not in overrides.columns:
        return df

    df_out = df.copy()
    override_dict = overrides.set_index("id").to_dict(orient="index")

    for idx_row, row in df_out.iterrows():
        row_id = row.get("id")
        if row_id in override_dict:
            ov = override_dict[row_id]
            if pd.notna(ov.get("lat")) and pd.notna(ov.get("lon")):
                df_out.at[idx_row, "lat"] = float(ov["lat"])
                df_out.at[idx_row, "lon"] = float(ov["lon"])
                df_out.at[idx_row, "geocode_quality"] = "manual"

    return df_out

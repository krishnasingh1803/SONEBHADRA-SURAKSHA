"""Duplicate accident detection and merging module."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Set
import pandas as pd
from blackspot.geo import haversine_m


def _parse_vehicle_set(val: Any) -> Set[str]:
    """Parse vehicle types string into a normalized set of strings."""
    if pd.isna(val) or val is None:
        return set()
    s = str(val).strip()
    if not s:
        return set()
    # Support semicolon and comma separation
    parts = s.replace(",", ";").split(";")
    return {p.strip().lower() for p in parts if p.strip()}


def _vehicles_overlap(v1: Set[str], v2: Set[str]) -> bool:
    """Check if vehicle sets overlap or if either is empty (compatible)."""
    if not v1 or not v2:
        return True
    return len(v1.intersection(v2)) > 0


def find_duplicates(
    df: pd.DataFrame,
    max_m: float = 300.0,
    max_day_gap: int = 1,
) -> pd.DataFrame:
    """Find pairs of accidents that represent duplicate reports of the same event.

    Criteria:
    - Both records have valid lat and lon
    - Calendar day gap <= max_day_gap
    - Distance <= max_m
    - Overlapping vehicle sets (empty set counts as compatible)

    Args:
        df: Input DataFrame.
        max_m: Maximum spatial distance in meters.
        max_day_gap: Maximum temporal distance in days.

    Returns:
        DataFrame with columns: ['id_a', 'id_b', 'distance_m', 'day_gap']
    """
    valid = df.dropna(subset=["lat", "lon"]).copy()
    if len(valid) < 2:
        return pd.DataFrame(columns=["id_a", "id_b", "distance_m", "day_gap"])

    valid["parsed_date"] = pd.to_datetime(valid["date"], errors="coerce")
    valid_indices = valid.index.tolist()
    records = []

    for i in range(len(valid_indices)):
        idx_a = valid_indices[i]
        row_a = valid.loc[idx_a]
        id_a = row_a["id"]
        date_a = row_a["parsed_date"]
        lat_a, lon_a = float(row_a["lat"]), float(row_a["lon"])
        veh_a = _parse_vehicle_set(row_a.get("vehicle_types"))

        for j in range(i + 1, len(valid_indices)):
            idx_b = valid_indices[j]
            row_b = valid.loc[idx_b]
            id_b = row_b["id"]
            date_b = row_b["parsed_date"]

            # Day gap check
            day_gap = abs((date_a - date_b).days)
            if day_gap > max_day_gap:
                continue

            # Vehicle overlap check
            veh_b = _parse_vehicle_set(row_b.get("vehicle_types"))
            if not _vehicles_overlap(veh_a, veh_b):
                continue

            # Distance check
            lat_b, lon_b = float(row_b["lat"]), float(row_b["lon"])
            dist = haversine_m(lat_a, lon_a, lat_b, lon_b)
            if dist <= max_m:
                smaller_id, larger_id = (id_a, id_b) if id_a < id_b else (id_b, id_a)
                records.append(
                    {
                        "id_a": smaller_id,
                        "id_b": larger_id,
                        "distance_m": round(dist, 2),
                        "day_gap": day_gap,
                    }
                )

    return pd.DataFrame(records, columns=["id_a", "id_b", "distance_m", "day_gap"])


def merge_duplicates(
    df: pd.DataFrame,
    pairs: pd.DataFrame,
    review_output_path: Optional[str | Path] = None,
) -> pd.DataFrame:
    """Merge duplicate records using Union-Find to resolve chains.

    Args:
        df: DataFrame with accidents.
        pairs: DataFrame containing 'id_a' and 'id_b'.
        review_output_path: Optional path to save dedup_pairs_to_review.csv.

    Returns:
        DataFrame with 'dup_of' column set on dropped records.
    """
    if review_output_path:
        out_p = Path(review_output_path)
        out_p.parent.mkdir(parents=True, exist_ok=True)
        # Check if already reviewed
        already_reviewed = False
        if out_p.exists():
            try:
                existing_rev = pd.read_csv(out_p)
                if "same_accident" in existing_rev.columns and existing_rev["same_accident"].fillna("").astype(str).str.strip().ne("").any():
                    already_reviewed = True
            except Exception:
                pass

        if not already_reviewed:
            review_df = pairs[["id_a", "id_b"]].copy() if not pairs.empty else pd.DataFrame(columns=["id_a", "id_b"])
            review_df["same_accident"] = ""
            review_df.to_csv(out_p, index=False)

    df_out = df.copy()
    if "dup_of" not in df_out.columns:
        df_out["dup_of"] = None
    df_out["dup_of"] = df_out["dup_of"].astype(object)

    if "other_sources" in df_out.columns:
        df_out["other_sources"] = df_out["other_sources"].fillna("").astype(str).astype(object)
    else:
        df_out["other_sources"] = ""
        df_out["other_sources"] = df_out["other_sources"].astype(object)

    if pairs.empty:
        return df_out

    # Union-find implementation
    parent: Dict[Any, Any] = {}

    def find(x: Any) -> Any:
        parent.setdefault(x, x)
        if parent[x] != x:
            parent[x] = find(parent[x])
        return parent[x]

    def union(x: Any, y: Any) -> None:
        root_x = find(x)
        root_y = find(y)
        if root_x != root_y:
            # Always make smaller ID the parent
            if root_x < root_y:
                parent[root_y] = root_x
            else:
                parent[root_x] = root_y

    for _, row in pairs.iterrows():
        union(row["id_a"], row["id_b"])

    # Group IDs by connected component
    groups: Dict[Any, List[Any]] = {}
    for row_id in df_out["id"]:
        if row_id in parent:
            root = find(row_id)
            groups.setdefault(root, []).append(row_id)

    id_to_idx = {val: idx for idx, val in df_out["id"].items()}

    for root_id, member_ids in groups.items():
        if len(member_ids) <= 1:
            continue
        min_id = min(member_ids)
        root_idx = id_to_idx[min_id]

        gathered_sources: List[str] = []
        max_injured = 0.0
        max_killed = 0.0

        for m_id in member_ids:
            m_idx = id_to_idx[m_id]
            m_row = df_out.loc[m_idx]

            # Sources
            src = str(m_row.get("source_url", "")).strip()
            if src and src != "nan" and src not in gathered_sources:
                gathered_sources.append(src)
            other = str(m_row.get("other_sources", "")).strip()
            if other and other != "nan":
                for o in other.split(";"):
                    o_clean = o.strip()
                    if o_clean and o_clean not in gathered_sources:
                        gathered_sources.append(o_clean)

            # Casualties
            inj = m_row.get("injured")
            if pd.notna(inj):
                try:
                    max_injured = max(max_injured, float(inj))
                except ValueError:
                    pass

            kll = m_row.get("killed")
            if pd.notna(kll):
                try:
                    max_killed = max(max_killed, float(kll))
                except ValueError:
                    pass

            if m_id != min_id:
                df_out.loc[m_idx, "dup_of"] = min_id

        # Update root row
        root_src = str(df_out.loc[root_idx, "source_url"]).strip()
        additional_sources = [s for s in gathered_sources if s != root_src]
        if additional_sources:
            df_out.loc[root_idx, "other_sources"] = "; ".join(additional_sources)
        df_out.loc[root_idx, "injured"] = int(max_injured)
        df_out.loc[root_idx, "killed"] = int(max_killed)

    return df_out

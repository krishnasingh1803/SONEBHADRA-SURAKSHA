"""Main CLI pipeline for Accident Blackspot Mapper."""

import argparse
import json
from pathlib import Path
import sys

# Ensure src is in sys.path
SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from typing import Any, Dict
import pandas as pd

from blackspot.config import load_config
from blackspot.schema import bucket_for_hour
from blackspot.validate import validate
from scripts.make_sample_data import generate_sample_data


def cmd_validate(cfg: Dict[str, Any]) -> int:
    """Validate data/raw/accidents_raw.csv."""
    raw_path = Path(cfg["paths"]["raw"])
    if not raw_path.exists():
        print(f"Error: {raw_path} not found.")
        return 1

    df = pd.read_csv(raw_path)
    if df.empty:
        print("Notice: Raw CSV has only a header row (0 data records). Add records using scripts/add_record.py.")
        return 0

    report = validate(df, cfg)
    print(f"Validation Report for {raw_path}:")
    print(f"  Total records: {report.n_rows}")
    print(f"  Valid records: {report.n_valid}")

    if report.warnings:
        print(f"\nWarnings ({len(report.warnings)}):")
        for w in report.warnings:
            print(f"  [WARN] {w}")

    if report.errors:
        print(f"\nErrors ({len(report.errors)}):")
        for e in report.errors:
            print(f"  [ERROR] {e}")
        return 1

    print("\n✅ Validation passed successfully with 0 errors!")
    return 0


def cmd_geocode(cfg: Dict[str, Any]) -> int:
    """Geocode data/raw/accidents_raw.csv with cache and overrides."""
    raw_path = Path(cfg["paths"]["raw"])
    if not raw_path.exists():
        print(f"Error: {raw_path} not found.")
        return 1

    df = pd.read_csv(raw_path)
    if df.empty:
        print("Notice: Raw CSV has only a header row. Nothing to geocode.")
        return 0

    from geopy.geocoders import Nominatim
    from geopy.extra.rate_limiter import RateLimiter
    from blackspot.geocode import district_bbox, geocode_place, apply_overrides

    geo_cfg = cfg.get("geocoder", {})
    geolocator = Nominatim(user_agent=geo_cfg.get("user_agent", "blackspot-mapper"))
    rate_limited = RateLimiter(
        geolocator.geocode,
        min_delay_seconds=float(geo_cfg.get("min_delay_seconds", 1.1)),
        error_wait_seconds=5.0,
        max_retries=2,
    )

    bbox = district_bbox(
        rate_limited,
        district=cfg.get("district", "Mathura"),
        country=cfg.get("country", "India"),
        margin_km=float(geo_cfg.get("bbox_margin_km", 5)),
    )

    cache_path = Path(cfg["paths"]["cache"])
    cache: Dict[str, Any] = {}
    if cache_path.exists():
        try:
            with open(cache_path, "r", encoding="utf-8") as f:
                cache = json.load(f)
        except Exception:
            cache = {}

    lats, lons, qualities = [], [], []
    for _, row in df.iterrows():
        place = str(row.get("place_text", ""))
        res = geocode_place(
            place,
            rate_limited,
            bbox=bbox,
            cache=cache,
            district=cfg.get("district", "Mathura"),
            country=cfg.get("country", "India"),
        )
        lats.append(res.lat)
        lons.append(res.lon)
        qualities.append(res.quality)

    cache_path.parent.mkdir(parents=True, exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(cache, f, indent=2)

    df["lat"] = lats
    df["lon"] = lons
    df["geocode_quality"] = qualities

    # Apply manual overrides
    df = apply_overrides(df, cfg["paths"]["overrides"])

    clean_path = Path(cfg["paths"]["clean"])
    clean_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(clean_path, index=False)
    print(f"Geocoding complete. Clean data written to {clean_path}.")
    return 0


def _run_pipeline(df: pd.DataFrame, cfg: Dict[str, Any], is_synthetic: bool = False) -> None:
    """Core execution pipeline shared by sample and build."""
    from blackspot.dedup import find_duplicates, merge_duplicates
    from blackspot.cluster import run_dbscan, sensitivity
    from blackspot.score import rank_clusters
    from blackspot.patterns import save_charts
    from blackspot.mapviz import build_map
    from blackspot.report import write_report, write_summary
    from blackspot.metrics import make_geocode_sample, time_split_hit_rate

    # Ensure time buckets and weekdays
    tb_map = cfg.get("time_buckets", {})
    time_buckets = []
    weekdays = []

    for _, row in df.iterrows():
        try:
            dt = pd.to_datetime(row["date"])
            weekdays.append(dt.strftime("%A"))
        except Exception:
            weekdays.append("unknown")

        t_str = str(row.get("time", "")).strip()
        if t_str and ":" in t_str:
            try:
                hour = int(t_str.split(":")[0])
                time_buckets.append(bucket_for_hour(hour, tb_map))
            except Exception:
                time_buckets.append("unknown")
        else:
            time_buckets.append("unknown")

    df["time_bucket"] = time_buckets
    df["weekday"] = weekdays
    if "dup_of" not in df.columns:
        df["dup_of"] = None

    # Deduplication
    dedup_cfg = cfg.get("dedup", {})
    pairs = find_duplicates(
        df,
        max_m=float(dedup_cfg.get("max_distance_m", 300)),
        max_day_gap=int(dedup_cfg.get("max_day_gap", 1)),
    )
    verification_dir = Path(cfg["paths"]["outputs"]) / "verification"
    df = merge_duplicates(df, pairs, review_output_path=verification_dir / "dedup_pairs_to_review.csv")

    # Clustering
    cluster_cfg = cfg.get("cluster", {})
    eps_m = float(cluster_cfg.get("eps_m", 300))
    min_samples = int(cluster_cfg.get("min_samples", 3))
    df = run_dbscan(df, eps_m=eps_m, min_samples=min_samples)

    # Save cleaned dataset
    clean_path = Path(cfg["paths"]["clean"])
    clean_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(clean_path, index=False)

    # Rank clusters
    clusters_df = rank_clusters(df, cfg)
    clusters_path = Path(cfg["paths"]["clusters"])
    clusters_path.parent.mkdir(parents=True, exist_ok=True)
    clusters_df.to_csv(clusters_path, index=False)

    # Charts
    charts_dir = Path(cfg["paths"]["outputs"]) / "charts"
    save_charts(df, clusters_df, charts_dir)

    # Map
    map_cfg = cfg.get("map", {})
    top_n = int(map_cfg.get("top_n", 10))
    m = build_map(
        df,
        clusters_df,
        top_n=top_n,
        title=f"{cfg.get('district', 'Mathura')} Accident Blackspots",
        synthetic=is_synthetic,
    )
    map_file = Path(cfg["paths"]["outputs"]) / "blackspots.html"
    map_file.parent.mkdir(parents=True, exist_ok=True)
    m.save(str(map_file))

    # Reports
    write_report(clusters_df, cfg["paths"]["outputs"])

    # Verification files
    make_geocode_sample(df, n=30, seed=42, out_path=verification_dir / "geocode_check.csv")

    # Metrics
    sens_df = sensitivity(
        df,
        eps_list=cluster_cfg.get("sensitivity_eps_m", [200, 300, 500]),
        min_samples=min_samples,
        cfg=cfg,
    )
    ts_res = time_split_hit_rate(df, cfg)

    active_pts = df[df["lat"].notna() & df["lon"].notna()]
    if "dup_of" in df.columns:
        active_pts = active_pts[active_pts["dup_of"].isna()]

    total_records = len(df)
    unique_accidents = len(active_pts)
    geocoded_share = round(len(df[df["geocode_quality"] != "failed"]) / max(1, total_records), 3)
    noise_count = (active_pts["cluster_id"] == -1).sum() if not active_pts.empty else 0
    noise_share = round(noise_count / max(1, unique_accidents), 3)

    sens_overlap_str = ", ".join(
        [f"{int(r.eps_m)}m: {int(r.overlap_with_base)} overlap" for _, r in sens_df.iterrows()]
    )

    stats = {
        "district": cfg.get("district", "Mathura"),
        "total_records": total_records,
        "unique_accidents": unique_accidents,
        "geocoded_share": geocoded_share,
        "n_clusters": len(clusters_df),
        "noise_share": noise_share,
        "geocode_accuracy": "TBD",
        "duplicate_precision": "TBD",
        "sensitivity_overlap": sens_overlap_str,
        "time_split_hit_rate": ts_res.get("hit_rate", "TBD"),
        "time_split_baseline": ts_res.get("baseline_hit_rate", "TBD"),
        "external_check": "TBD",
        "is_synthetic": is_synthetic,
    }

    write_summary(stats, cfg["paths"]["outputs"])
    print(f"\n🎉 Pipeline completed successfully!")
    print(f"  Clean Data: {clean_path}")
    print(f"  Clusters:   {clusters_path}")
    print(f"  Map:        {map_file}")
    print(f"  Report:     {Path(cfg['paths']['outputs']) / 'blackspots_report.csv'}")
    print(f"  Summary:    {Path(cfg['paths']['outputs']) / 'summary.md'}")


def cmd_sample(cfg: Dict[str, Any]) -> int:
    """Run full pipeline offline on synthetic sample data."""
    sample_path = Path(cfg["paths"]["sample"])
    if not sample_path.exists():
        generate_sample_data(sample_path)

    df = pd.read_csv(sample_path)
    df["geocode_quality"] = "exact"
    _run_pipeline(df, cfg, is_synthetic=True)
    return 0


def cmd_build(cfg: Dict[str, Any]) -> int:
    """Run full pipeline on raw news data."""
    raw_path = Path(cfg["paths"]["raw"])
    if not raw_path.exists():
        print(f"Error: {raw_path} not found.")
        return 1

    df = pd.read_csv(raw_path)
    if df.empty:
        print("Notice: Raw CSV has only a header row (no data records found).")
        print("To populate real data, use scripts/add_record.py or provide records in data/raw/accidents_raw.csv.")
        print("For testing and verification, run: python main.py sample")
        return 0

    cmd_geocode(cfg)
    clean_path = Path(cfg["paths"]["clean"])
    clean_df = pd.read_csv(clean_path)
    _run_pipeline(clean_df, cfg, is_synthetic=False)
    return 0


def cmd_metrics(cfg: Dict[str, Any]) -> int:
    """Compute geocode accuracy and time-split validation hit rate."""
    clean_path = Path(cfg["paths"]["clean"])
    if not clean_path.exists():
        print(f"Error: {clean_path} does not exist. Run 'build' or 'sample' first.")
        return 1

    from blackspot.metrics import geocode_accuracy, time_split_hit_rate

    df = pd.read_csv(clean_path)
    verification_dir = Path(cfg["paths"]["outputs"]) / "verification"

    # Geocode accuracy
    geo_acc = geocode_accuracy(verification_dir / "geocode_check.csv")
    print("\n--- Geocode Accuracy ---")
    print(f"  Records Checked: {geo_acc['checked_count']}")
    print(f"  Accuracy (<=200m): {geo_acc['accuracy_share']}")
    print(f"  Median Error: {geo_acc['median_error_m']} m")

    # Time split hit rate
    ts_res = time_split_hit_rate(df, cfg)
    print("\n--- Time-Split Validation ---")
    print(f"  Historical Cluster Hit Rate: {ts_res['hit_rate']}")
    print(f"  Random Baseline Hit Rate:    {ts_res['baseline_hit_rate']}")
    print(f"  Test Records Evaluated:      {ts_res['test_count']}")
    return 0


def cmd_verify_files(cfg: Dict[str, Any]) -> int:
    """Generate manual verification files for geocoding and duplicate checks."""
    clean_path = Path(cfg["paths"]["clean"])
    if not clean_path.exists():
        print(f"Error: {clean_path} does not exist. Run 'build' or 'sample' first.")
        return 1

    from blackspot.dedup import find_duplicates
    from blackspot.metrics import make_geocode_sample

    df = pd.read_csv(clean_path)
    verification_dir = Path(cfg["paths"]["outputs"]) / "verification"
    p_geo = make_geocode_sample(df, n=30, seed=42, out_path=verification_dir / "geocode_check.csv")

    pairs = find_duplicates(
        df,
        max_m=float(cfg.get("dedup", {}).get("max_distance_m", 300)),
        max_day_gap=int(cfg.get("dedup", {}).get("max_day_gap", 1)),
    )
    p_dup = verification_dir / "dedup_pairs_to_review.csv"
    review_df = pairs[["id_a", "id_b"]].copy() if not pairs.empty else pd.DataFrame(columns=["id_a", "id_b"])
    review_df["same_accident"] = ""
    review_df.to_csv(p_dup, index=False)

    print(f"Verification files written:")
    print(f"  1. {p_geo}")
    print(f"  2. {p_dup}")
    return 0


def main() -> None:
    """Parse CLI arguments and dispatch command."""
    parser = argparse.ArgumentParser(description="Accident Blackspot Mapper CLI")
    parser.add_argument(
        "command",
        choices=["validate", "geocode", "build", "sample", "metrics", "verify-files"],
        help="Command to execute",
    )
    args = parser.parse_args()
    cfg = load_config()

    if args.command == "validate":
        sys.exit(cmd_validate(cfg))
    elif args.command == "geocode":
        sys.exit(cmd_geocode(cfg))
    elif args.command == "build":
        sys.exit(cmd_build(cfg))
    elif args.command == "sample":
        sys.exit(cmd_sample(cfg))
    elif args.command == "metrics":
        sys.exit(cmd_metrics(cfg))
    elif args.command == "verify-files":
        sys.exit(cmd_verify_files(cfg))


if __name__ == "__main__":
    main()

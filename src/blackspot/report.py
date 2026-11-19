"""Reporting module to export CSV summaries and markdown documentation."""

from pathlib import Path
from typing import Any, Dict, Optional
import pandas as pd


def write_report(clusters: pd.DataFrame, out_dir: str | Path) -> Path:
    """Write ranked blackspots report to blackspots_report.csv.

    Columns: rank, label, lat, lon, accidents, killed, injured, score, peak_time, peak_weekday.

    Args:
        clusters: Ranked clusters DataFrame.
        out_dir: Output directory path.

    Returns:
        Path to written CSV file.
    """
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    report_file = out_path / "blackspots_report.csv"

    if clusters.empty:
        df_empty = pd.DataFrame(
            columns=[
                "rank",
                "label",
                "lat",
                "lon",
                "accidents",
                "killed",
                "injured",
                "score",
                "peak_time",
                "peak_weekday",
            ]
        )
        df_empty.to_csv(report_file, index=False)
        return report_file

    report_df = pd.DataFrame()
    report_df["rank"] = clusters["rank_by_score"]
    report_df["label"] = clusters["label"]
    report_df["lat"] = clusters["centroid_lat"]
    report_df["lon"] = clusters["centroid_lon"]
    report_df["accidents"] = clusters["n_accidents"]
    report_df["killed"] = clusters["killed"]
    report_df["injured"] = clusters["injured"]
    report_df["score"] = clusters["score"]
    report_df["peak_time"] = clusters["peak_time_bucket"]
    report_df["peak_weekday"] = clusters["peak_weekday"]

    report_df.to_csv(report_file, index=False)
    return report_file


def write_summary(stats: Dict[str, Any], out_dir: str | Path) -> Path:
    """Write executive summary and metrics to summary.md using TBD for unmeasured values.

    Args:
        stats: Dictionary of measured dataset and cluster statistics.
        out_dir: Output directory path.

    Returns:
        Path to written summary.md file.
    """
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    summary_file = out_path / "summary.md"

    district = stats.get("district", "Mathura")
    n_total = stats.get("total_records", "TBD")
    n_unique = stats.get("unique_accidents", "TBD")
    geocoded_share = stats.get("geocoded_share", "TBD")
    n_clusters = stats.get("n_clusters", "TBD")
    noise_share = stats.get("noise_share", "TBD")
    geocode_accuracy = stats.get("geocode_accuracy", "TBD")
    duplicate_precision = stats.get("duplicate_precision", "TBD")
    sensitivity_overlap = stats.get("sensitivity_overlap", "TBD")
    time_split_hit_rate = stats.get("time_split_hit_rate", "TBD")
    time_split_baseline = stats.get("time_split_baseline", "TBD")
    external_check = stats.get("external_check", "TBD")
    synthetic_note = (
        "> ⚠️ **SYNTHETIC DEMO DATA**: These statistics were computed on synthetic test data.\n\n"
        if stats.get("is_synthetic", False)
        else ""
    )

    content = f"""# Accident Blackspot Mapper: Summary Report

{synthetic_note}Core Claim: "Identifies indicative accident clusters in district {district} from {n_unique} news-reported accidents, validated against {external_check}."

## Key Metrics Table

| Metric | Target | Measured Result | Status |
| :--- | :--- | :--- | :--- |
| **Dataset size** | 150+ unique accidents | {n_unique} | {'Met' if isinstance(n_unique, (int, float)) and n_unique >= 150 else 'Pending'} |
| **Geocoded share** | 85%+ | {geocoded_share} | {'Met' if isinstance(geocoded_share, (int, float)) and geocoded_share >= 0.85 else 'In Progress'} |
| **Geocode accuracy** | 30+ hand-verified points within 200m | {geocode_accuracy} | {'Pending' if geocode_accuracy == 'TBD' else 'Completed'} |
| **Duplicate detection** | Precision on 20 flagged pairs | {duplicate_precision} | {'Pending' if duplicate_precision == 'TBD' else 'Completed'} |
| **Cluster stability** | Top 5 overlap across eps 200, 300, 500 | {sensitivity_overlap} | {'Measured' if sensitivity_overlap != 'TBD' else 'TBD'} |
| **Time-split hit rate** | Hit rate > random baseline | {time_split_hit_rate} (Baseline: {time_split_baseline}) | {'Measured' if time_split_hit_rate != 'TBD' else 'TBD'} |
| **External check** | Matches official traffic list / officer view | {external_check} | {'Pending' if external_check == 'TBD' else 'Completed'} |

## Clustering & Analysis Overview
- **Total Records Processed**: {n_total}
- **Unique Deduplicated Accidents**: {n_unique}
- **Detected Blackspots**: {n_clusters}
- **Noise Accidents (Isolated Points)**: {noise_share}

## Limitations
1. Only news-reported accidents are included, and serious and fatal ones are over-represented.
2. Location accuracy depends on how the reporter wrote the place.
3. Small sample (about 150 to a few hundred) means results are indicative, not statistically proven.
4. The tool does not explain causes.
5. Clusters depend on the chosen eps and min_samples. Sensitivity results are reported.
"""

    with open(summary_file, "w", encoding="utf-8") as f:
        f.write(content)

    return summary_file

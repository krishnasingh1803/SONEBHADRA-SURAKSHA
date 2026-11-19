"""Map generation module using Folium with modern aesthetic styling."""

from typing import Any, Dict, List, Optional
import folium
from folium import Element
import pandas as pd


def _rank_color(rank: int, total: int) -> str:
    """Return color gradient from red to yellow based on rank."""
    colors = [
        "#D90429",  # Deep Red (Rank 1)
        "#EF233C",
        "#F77F00",
        "#FCBF49",
        "#EAE2B7",  # Yellow/Warm
    ]
    if total <= 1:
        return colors[0]
    idx = int((rank - 1) / max(1, total - 1) * (len(colors) - 1))
    idx = max(0, min(idx, len(colors) - 1))
    return colors[idx]


def build_map(
    df: pd.DataFrame,
    clusters: pd.DataFrame,
    top_n: int = 10,
    title: str = "Mathura Accident Blackspots",
    synthetic: bool = False,
) -> folium.Map:
    """Build interactive Folium map of accidents and ranked blackspot clusters.

    Args:
        df: Clean accidents DataFrame with coordinates.
        clusters: Ranked clusters DataFrame.
        top_n: Number of top clusters to highlight.
        title: Title of the map.
        synthetic: Whether the dataset is synthetic.

    Returns:
        folium.Map instance.
    """
    # Determine center
    valid_pts = df[df["lat"].notna() & df["lon"].notna()]
    if not valid_pts.empty:
        center_lat = float(valid_pts["lat"].mean())
        center_lon = float(valid_pts["lon"].mean())
    else:
        center_lat, center_lon = 27.4924, 77.6737  # Default Mathura center

    m = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=11,
        tiles="OpenStreetMap",
        control_scale=True,
    )

    # Feature groups
    fg_individual = folium.FeatureGroup(name="Individual Accidents", show=True)
    fg_clusters = folium.FeatureGroup(name="Ranked Blackspots", show=True)

    # Plot all individual geocoded accidents as small grey circles
    for _, row in valid_pts.iterrows():
        lat, lon = float(row["lat"]), float(row["lon"])
        folium.CircleMarker(
            location=[lat, lon],
            radius=3,
            color="#8D99AE",
            weight=1,
            fill=True,
            fill_color="#8D99AE",
            fill_opacity=0.6,
        ).add_to(fg_individual)

    # Plot top N clusters
    if not clusters.empty:
        top_clusters = clusters.head(top_n)
        n_clusters = len(top_clusters)

        for _, c_row in top_clusters.iterrows():
            c_id = int(c_row["cluster_id"])
            c_lat = float(c_row["centroid_lat"])
            c_lon = float(c_row["centroid_lon"])
            rank = int(c_row.get("rank_by_score", 1))
            score = float(c_row.get("score", 1.0))
            label = str(c_row.get("label", f"Cluster {c_id}"))
            acc_count = int(c_row.get("n_accidents", 0))
            killed = int(c_row.get("killed", 0))
            injured = int(c_row.get("injured", 0))
            peak_time = str(c_row.get("peak_time_bucket", "unknown"))

            # Gather up to 3 sources
            c_accidents = valid_pts[valid_pts["cluster_id"] == c_id]
            source_links: List[str] = []
            for _, r in c_accidents.iterrows():
                src = str(r.get("source_url", "")).strip()
                if src and src.startswith("http") and src not in source_links:
                    source_links.append(src)
                if len(source_links) >= 3:
                    break

            links_html = "".join(
                [
                    f'<div style="margin-top:4px;"><a href="{url}" target="_blank" style="color:#0077B6; text-decoration:none; font-size:11px; font-weight:500;">🔗 Source {idx+1}</a></div>'
                    for idx, url in enumerate(source_links)
                ]
            )

            color = _rank_color(rank, n_clusters)
            # Size proportional to score, clamped
            radius = min(40, max(12, int(score * 2.2)))

            popup_html = f"""
            <div style="font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,sans-serif; width:220px; padding:6px 4px; color:#1F2937;">
                <div style="font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.5px; color:{color}; margin-bottom:2px;">
                    Rank #{rank} Blackspot
                </div>
                <div style="font-size:14px; font-weight:700; margin-bottom:8px; line-height:1.2;">
                    {label}
                </div>
                <div style="display:flex; justify-content:space-between; background:#F3F4F6; border-radius:8px; padding:6px 10px; margin-bottom:8px; font-size:12px;">
                    <span><b>Accidents:</b> {acc_count}</span>
                    <span><b>Score:</b> {score}</span>
                </div>
                <div style="font-size:11px; line-height:1.6; color:#4B5563;">
                    <div>• <b>Casualties:</b> {killed} killed, {injured} injured</div>
                    <div>• <b>Peak Window:</b> {peak_time.capitalize()}</div>
                </div>
                {links_html}
            </div>
            """

            folium.CircleMarker(
                location=[c_lat, c_lon],
                radius=radius,
                color=color,
                weight=2,
                fill=True,
                fill_color=color,
                fill_opacity=0.65,
                popup=folium.Popup(popup_html, max_width=260),
                tooltip=f"Rank #{rank}: {label} ({acc_count} accidents)",
            ).add_to(fg_clusters)

    fg_individual.add_to(m)
    fg_clusters.add_to(m)
    folium.LayerControl().add_to(m)

    # HTML Legend & Banner Element
    banner_html = ""
    if synthetic:
        banner_html = """
        <div style="
            position: fixed;
            top: 15px;
            left: 50%;
            transform: translateX(-50%);
            z-index: 9999;
            background-color: #111827;
            color: #FFFFFF;
            padding: 8px 20px;
            border-radius: 9999px;
            font-size: 13px;
            font-weight: 800;
            letter-spacing: 1px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.25);
            pointer-events: none;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        ">
            ⚠️ SYNTHETIC DEMO DATA
        </div>
        """

    legend_html = f"""
    {banner_html}
    <div style="
        position: fixed;
        bottom: 25px;
        right: 25px;
        z-index: 9998;
        background: rgba(255, 255, 255, 0.95);
        border: 1px solid #E5E7EB;
        padding: 12px 16px;
        border-radius: 16px;
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        font-size: 11px;
        line-height: 1.6;
        color: #1F2937;
    ">
        <div style="font-weight: 700; margin-bottom: 6px; font-size: 12px;">Map Legend</div>
        <div><span style="display:inline-block; width:10px; height:10px; border-radius:50%; background:#8D99AE; margin-right:6px;"></span>Single Accident Point</div>
        <div><span style="display:inline-block; width:12px; height:12px; border-radius:50%; background:#D90429; margin-right:6px;"></span>Top Blackspot (High Severity)</div>
        <div><span style="display:inline-block; width:10px; height:10px; border-radius:50%; background:#FCBF49; margin-right:6px;"></span>Moderate Blackspot</div>
    </div>
    """
    m.get_root().html.add_child(Element(legend_html))

    return m

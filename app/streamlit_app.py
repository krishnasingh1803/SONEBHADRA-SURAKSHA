"""Streamlit interactive web dashboard for Accident Blackspot Mapper.

UI styled with soft-card neumorphic design aesthetic matching the user specifications:
- Warm off-white/cream tones (#F8F8F6, #FFF6E5, #DCEEF7)
- Rounded pill containers (border-radius: 20-24px)
- High contrast dark charcoal actions (#1A1A1A)
- Clean typography and micro-interactions
- Strictly reads data from data/processed/ only
"""

from pathlib import Path
import sys

# Ensure src is in sys.path
SRC_DIR = Path(__file__).resolve().parent.parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import folium
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

from blackspot.config import load_config
from blackspot.mapviz import build_map
from blackspot.patterns import counts_by, _style_axis
from blackspot.score import rank_clusters

# Configure page
st.set_page_config(
    page_title="Accident Blackspot Mapper",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling matching the exact UI reference image
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    color: #1E1E1E;
}

/* Background canvas */
.stApp {
    background-color: #F7F7F5;
}

/* Sidebar styling */
section[data-testid="stSidebar"] {
    background-color: #EFEFEA;
    border-right: 1px solid #E2E2DC;
    padding-top: 1rem;
}

/* Card components */
.ui-card {
    background: #FFFFFF;
    border-radius: 24px;
    padding: 22px 26px;
    border: 1px solid #E8E8E4;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
    margin-bottom: 20px;
}

.ui-card-cream {
    background: #FFF6E5;
    border-radius: 24px;
    padding: 22px 26px;
    border: 1px solid #F5E8CE;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02);
    margin-bottom: 20px;
}

.ui-card-blue {
    background: #DCEEF7;
    border-radius: 24px;
    padding: 22px 26px;
    border: 1px solid #C8E3F2;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02);
    margin-bottom: 20px;
}

.ui-card-mint {
    background: #E4F5EB;
    border-radius: 24px;
    padding: 22px 26px;
    border: 1px solid #D1ECD9;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02);
    margin-bottom: 20px;
}

/* Banner pill */
.synthetic-banner-pill {
    display: inline-flex;
    align-items: center;
    background-color: #1A1A1A;
    color: #FFFFFF;
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 0.8px;
    padding: 8px 24px;
    border-radius: 9999px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    margin-bottom: 18px;
}

/* Filter Tag Pills */
.pill-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 11px;
    font-weight: 600;
    margin-right: 6px;
    margin-bottom: 6px;
}
.pill-neutral { background: #EFEFEA; color: #4A4A4A; }
.pill-red { background: #FFE5E5; color: #C5221F; }
.pill-yellow { background: #FEF3D6; color: #B06000; }
.pill-blue { background: #E1F0FA; color: #10669E; }

/* Metrics value text */
.metric-value {
    font-size: 32px;
    font-weight: 800;
    line-height: 1.1;
    margin-top: 6px;
    color: #1A1A1A;
}
.metric-label {
    font-size: 13px;
    font-weight: 600;
    color: #6A6A66;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}
.metric-sub {
    font-size: 12px;
    color: #7A7A76;
    margin-top: 4px;
}

/* Table container styling */
div[data-testid="stDataFrame"] {
    border-radius: 20px;
    overflow: hidden;
    border: 1px solid #E8E8E4;
}

/* Header title */
.app-title {
    font-size: 28px;
    font-weight: 800;
    letter-spacing: -0.5px;
    color: #111111;
    margin-bottom: 4px;
}
.app-sub {
    font-size: 14px;
    color: #666662;
    margin-bottom: 20px;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


@st.cache_data
def load_processed_data():
    """Load cleaned accidents and clusters from data/processed/ directory only."""
    clean_path = Path("data/processed/accidents_clean.csv")
    clusters_path = Path("data/processed/clusters.csv")

    if not clean_path.exists() or not clusters_path.exists():
        return None, None

    clean_df = pd.read_csv(clean_path)
    clusters_df = pd.read_csv(clusters_path)
    return clean_df, clusters_df


# Load Data
clean_df, clusters_df = load_processed_data()

if clean_df is None or clusters_df is None or clean_df.empty:
    st.markdown(
        """
        <div class="ui-card" style="text-align: center; padding: 40px;">
            <h3>📍 No Processed Data Found</h3>
            <p style="color: #666;">Please build the dataset first using the CLI pipeline.</p>
            <code>python main.py sample</code> or <code>python main.py build</code>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

# Config
try:
    cfg = load_config()
except Exception:
    cfg = {}

district_name = cfg.get("district", "Mathura")
is_synthetic = bool((clean_df.get("source_name", "") == "SYNTHETIC").any())

# Top Banner
if is_synthetic:
    st.markdown(
        '<div style="text-align:center;"><div class="synthetic-banner-pill">⚠️ SYNTHETIC DEMO DATA</div></div>',
        unsafe_allow_html=True,
    )

# Header Section
st.markdown(
    f"""
    <div>
        <div class="app-title">{district_name} Road Safety & Blackspot Analysis</div>
        <div class="app-sub">Spatial cluster intelligence derived from local news reports and geocoded incident logs</div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar Filters
st.sidebar.markdown("### 🔍 Filter Blackspots")

# 1. Date Range
if "date" in clean_df.columns and not clean_df["date"].dropna().empty:
    clean_df["parsed_date"] = pd.to_datetime(clean_df["date"], errors="coerce")
    min_date = clean_df["parsed_date"].min().date()
    max_date = clean_df["parsed_date"].max().date()
    date_range = st.sidebar.date_input(
        "Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
    )
else:
    date_range = None

# 2. Time Bucket Filter
time_bucket_options = ["All"] + sorted([b for b in clean_df["time_bucket"].dropna().unique() if b != "unknown"])
selected_time_bucket = st.sidebar.selectbox("Time Window", time_bucket_options, index=0)

# 3. Vehicle Type Filter
all_vehicles = set()
for v in clean_df["vehicle_types"].dropna():
    parts = str(v).replace(",", ";").split(";")
    for p in parts:
        cleaned_p = p.strip().lower()
        if cleaned_p:
            all_vehicles.add(cleaned_p)
vehicle_options = sorted(list(all_vehicles))
selected_vehicles = st.sidebar.multiselect("Vehicle Involved", vehicle_options, default=[])

# 4. Severity Score Filter
min_score = float(clusters_df["score"].min()) if not clusters_df.empty else 0.0
max_score = float(clusters_df["score"].max()) if not clusters_df.empty else 10.0
score_threshold = st.sidebar.slider(
    "Minimum Cluster Severity Score",
    min_value=0.0,
    max_value=max(10.0, max_score),
    value=float(min_score),
    step=0.5,
)

# Apply Filters
filtered_df = clean_df.copy()

# Date filter
if date_range and len(date_range) == 2:
    start_d, end_d = date_range
    filtered_df = filtered_df[
        (filtered_df["parsed_date"].dt.date >= start_d) & (filtered_df["parsed_date"].dt.date <= end_d)
    ]

# Time bucket filter
if selected_time_bucket != "All":
    filtered_df = filtered_df[filtered_df["time_bucket"] == selected_time_bucket]

# Vehicle filter
if selected_vehicles:
    def has_matching_vehicle(val):
        if pd.isna(val):
            return False
        parts = [p.strip().lower() for p in str(val).replace(",", ";").split(";")]
        return any(v in parts for v in selected_vehicles)

    filtered_df = filtered_df[filtered_df["vehicle_types"].apply(has_matching_vehicle)]

# Filter Clusters by Score
filtered_clusters = clusters_df[clusters_df["score"] >= score_threshold].copy()
if not filtered_clusters.empty:
    filtered_clusters["rank_by_score"] = range(1, len(filtered_clusters) + 1)

# Stat Cards Row (Cards inspired by the uploaded mockup: Cream, Soft Blue, Soft Mint)
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(
        f"""
        <div class="ui-card-cream">
            <div class="metric-label">Identified Blackspots</div>
            <div class="metric-value">{len(filtered_clusters)}</div>
            <div class="metric-sub">Ranked high-risk locations</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c2:
    active_count = len(filtered_df[filtered_df["dup_of"].isna()])
    st.markdown(
        f"""
        <div class="ui-card-blue">
            <div class="metric-label">Active Incidents</div>
            <div class="metric-value">{active_count}</div>
            <div class="metric-sub">Filtered from {len(clean_df)} records</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c3:
    total_killed = int(filtered_df["killed"].fillna(0).sum())
    total_injured = int(filtered_df["injured"].fillna(0).sum())
    st.markdown(
        f"""
        <div class="ui-card-mint">
            <div class="metric-label">Reported Casualties</div>
            <div class="metric-value">{total_killed + total_injured}</div>
            <div class="metric-sub">{total_killed} killed • {total_injured} injured</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with c4:
    peak_time_overall = (
        filtered_df["time_bucket"].mode().iloc[0].capitalize()
        if not filtered_df["time_bucket"].dropna().empty
        else "N/A"
    )
    st.markdown(
        f"""
        <div class="ui-card">
            <div class="metric-label">High-Risk Window</div>
            <div class="metric-value" style="font-size:24px; padding-top:4px;">{peak_time_overall}</div>
            <div class="metric-sub">Highest incident frequency</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Map & Blackspot Details Section
st.markdown("### 🗺️ Interactive Blackspot Cluster Map")
st.caption("Circles represent ranked accident blackspots. Click any hotspot circle to inspect casualties, peak time, and news sources.")

map_obj = build_map(
    filtered_df,
    filtered_clusters,
    top_n=len(filtered_clusters),
    title=f"{district_name} Blackspots",
    synthetic=is_synthetic,
)

st_folium(map_obj, width=None, height=480)

# Ranked Clusters Table
st.markdown("### 📋 Ranked Blackspots Breakdown")
if not filtered_clusters.empty:
    display_table = filtered_clusters[
        [
            "rank_by_score",
            "label",
            "n_accidents",
            "killed",
            "injured",
            "score",
            "peak_time_bucket",
            "peak_weekday",
            "top_vehicle",
        ]
    ].rename(
        columns={
            "rank_by_score": "Rank",
            "label": "Blackspot Landmark",
            "n_accidents": "Accidents",
            "killed": "Killed",
            "injured": "Injured",
            "score": "Severity Score",
            "peak_time_bucket": "Peak Time",
            "peak_weekday": "Peak Day",
            "top_vehicle": "Primary Vehicle",
        }
    )
    st.dataframe(display_table, use_container_width=True, hide_index=True)
else:
    st.info("No clusters match the current severity threshold and filter options.")

# Overall Visual Pattern Charts
st.markdown("### 📊 Distribution Patterns")
tab1, tab2, tab3 = st.columns(3)

with tab1:
    st.markdown('<div class="ui-card">', unsafe_allow_html=True)
    fig1, ax1 = plt.subplots(figsize=(5, 3.5))
    tb_c = counts_by(filtered_df[filtered_df["dup_of"].isna()], "time_bucket")
    if not tb_c.empty:
        tb_c.plot(kind="bar", ax=ax1, color="#3D5A80", width=0.6)
    _style_axis(ax1, "Time of Day", "Time Window", "Accidents")
    plt.xticks(rotation=0)
    plt.tight_layout()
    st.pyplot(fig1)
    plt.close(fig1)
    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="ui-card">', unsafe_allow_html=True)
    fig2, ax2 = plt.subplots(figsize=(5, 3.5))
    wd_c = counts_by(filtered_df[filtered_df["dup_of"].isna()], "weekday")
    day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    if not wd_c.empty:
        reordered = [d for d in day_order if d in wd_c.index]
        if reordered:
            wd_c = wd_c.reindex(reordered + [d for d in wd_c.index if d not in day_order])
        wd_c.plot(kind="bar", ax=ax2, color="#48CAE4", width=0.6)
    _style_axis(ax2, "Day of Week", "Weekday", "Accidents")
    plt.xticks(rotation=30)
    plt.tight_layout()
    st.pyplot(fig2)
    plt.close(fig2)
    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="ui-card">', unsafe_allow_html=True)
    fig3, ax3 = plt.subplots(figsize=(5, 3.5))
    veh_c = counts_by(filtered_df[filtered_df["dup_of"].isna()], "vehicle_types")
    if not veh_c.empty:
        veh_c.head(8).plot(kind="bar", ax=ax3, color="#F4A261", width=0.6)
    _style_axis(ax3, "Vehicle Type", "Vehicle", "Accidents")
    plt.xticks(rotation=30)
    plt.tight_layout()
    st.pyplot(fig3)
    plt.close(fig3)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    """
    <div style="margin-top: 30px; text-align: center; color: #888884; font-size: 12px;">
        Accident Blackspot Mapper • Second-Year Road Safety Project • Data sourced from news-reported incidents
    </div>
    """,
    unsafe_allow_html=True,
)

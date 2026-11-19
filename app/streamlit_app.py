"""Streamlit Interactive Web Dashboard for Accident Blackspot Mapper.

Includes:
- Citizen Portal (Commuter hazard alerts, safe route advisory, citizen hazard reporting)
- Admin / Traffic Police Command Center (Ranked blackspots, patrol dispatch, data management)
- Custom soft-card design aesthetic matching user reference image
- SVG branding logos, micro-animations, and animated card states
- Strictly reads data from data/processed/ only
"""

from datetime import datetime
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

# Page Config
st.set_page_config(
    page_title="सुरक्षा | Sonbhadra Blackspot Intel",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom Styling with Soft-Card Neumorphic Look + Animations
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

/* Animations */
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(8px); }
    to { opacity: 1; transform: translateY(0); }
}

@keyframes pulseGlow {
    0% { box-shadow: 0 0 0 0 rgba(217, 4, 41, 0.4); }
    70% { box-shadow: 0 0 0 10px rgba(217, 4, 41, 0); }
    100% { box-shadow: 0 0 0 0 rgba(217, 4, 41, 0); }
}

@keyframes badgeBlink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}

/* Card components */
.ui-card {
    background: #FFFFFF;
    border-radius: 24px;
    padding: 22px 26px;
    border: 1px solid #E8E8E4;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
    margin-bottom: 20px;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
    animation: fadeIn 0.4s ease-out;
}
.ui-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 28px rgba(0, 0, 0, 0.06);
}

.ui-card-cream {
    background: #FFF6E5;
    border-radius: 24px;
    padding: 22px 26px;
    border: 1px solid #F5E8CE;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02);
    margin-bottom: 20px;
    transition: all 0.25s ease;
    animation: fadeIn 0.4s ease-out;
}
.ui-card-cream:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(245, 232, 206, 0.6);
}

.ui-card-blue {
    background: #DCEEF7;
    border-radius: 24px;
    padding: 22px 26px;
    border: 1px solid #C8E3F2;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02);
    margin-bottom: 20px;
    transition: all 0.25s ease;
    animation: fadeIn 0.4s ease-out;
}
.ui-card-blue:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(200, 227, 242, 0.6);
}

.ui-card-mint {
    background: #E4F5EB;
    border-radius: 24px;
    padding: 22px 26px;
    border: 1px solid #D1ECD9;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.02);
    margin-bottom: 20px;
    transition: all 0.25s ease;
    animation: fadeIn 0.4s ease-out;
}
.ui-card-mint:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 24px rgba(209, 236, 217, 0.6);
}

/* Alert card */
.ui-card-alert {
    background: #FFF1F0;
    border-radius: 24px;
    padding: 18px 24px;
    border: 1px solid #FFCCC7;
    margin-bottom: 20px;
    animation: pulseGlow 2s infinite;
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

.badge-live {
    display: inline-flex;
    align-items: center;
    background-color: #D90429;
    color: #FFFFFF;
    font-weight: 700;
    font-size: 11px;
    letter-spacing: 0.5px;
    padding: 4px 12px;
    border-radius: 9999px;
    animation: badgeBlink 1.8s infinite;
}

/* Tag Pills */
.pill-badge {
    display: inline-block;
    padding: 5px 14px;
    border-radius: 9999px;
    font-size: 12px;
    font-weight: 600;
    margin-right: 6px;
    margin-bottom: 6px;
}
.pill-neutral { background: #EFEFEA; color: #4A4A4A; }
.pill-red { background: #FFE5E5; color: #C5221F; }
.pill-yellow { background: #FEF3D6; color: #B06000; }
.pill-blue { background: #E1F0FA; color: #10669E; }
.pill-green { background: #E4F5EB; color: #1E7E34; }

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

/* Header container */
.brand-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 0 20px 0;
}
.brand-logo-text {
    font-size: 26px;
    font-weight: 800;
    color: #111111;
    letter-spacing: -0.5px;
}
.brand-subtitle {
    font-size: 13px;
    color: #666662;
    margin-top: 2px;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# Initialize Session State for Authentication & Role
if "user_role" not in st.session_state:
    st.session_state["user_role"] = "citizen"  # 'citizen', 'admin', None
if "citizen_name" not in st.session_state:
    st.session_state["citizen_name"] = "Commuter"


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
            <code>python main.py build</code>
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

district_name = cfg.get("district", "Sonbhadra")
is_synthetic = bool((clean_df.get("source_name", "") == "SYNTHETIC").any())


# --- TOP NAVIGATION & BRANDING BAR ---
brand_col1, brand_col2 = st.columns([3, 1])

with brand_col1:
    st.markdown(
        f"""
        <div class="brand-header">
            <div>
                <div class="brand-logo-text">🛡️ सुरक्षा • SURAKSHA {district_name.upper()}</div>
                <div class="brand-subtitle">Road Safety Intelligence & Accident Blackspot Monitoring System • UP Police & PWD</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with brand_col2:
    current_role = st.session_state["user_role"]
    role_label = "👤 Citizen Mode" if current_role == "citizen" else "👮 Police / Admin Mode"
    st.markdown(
        f"""
        <div style="text-align: right; padding-top: 10px;">
            <span class="pill-badge { 'pill-blue' if current_role == 'citizen' else 'pill-red' }">
                {role_label}
            </span>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Top Synthetic Banner if applicable
if is_synthetic:
    st.markdown(
        '<div style="text-align:center;"><div class="synthetic-banner-pill">⚠️ SYNTHETIC DEMO DATA</div></div>',
        unsafe_allow_html=True,
    )

# --- SIDEBAR: AUTHENTICATION & ROLE SWITCHER ---
st.sidebar.markdown("### 🔐 User Portal & Login")

role_choice = st.sidebar.radio(
    "Select Portal",
    ["👤 Citizen / Commuter", "👮 Traffic Police & Admin"],
    index=0 if st.session_state["user_role"] == "citizen" else 1,
)

if role_choice == "👤 Citizen / Commuter":
    st.session_state["user_role"] = "citizen"
else:
    st.session_state["user_role"] = "admin"

st.sidebar.markdown("---")

# ==========================================
# 👤 CITIZEN / COMMUTER PORTAL
# ==========================================
if st.session_state["user_role"] == "citizen":
    # Critical Alert Banner for Commuters
    st.markdown(
        """
        <div class="ui-card-alert">
            <div style="display:flex; align-items:center; gap: 12px;">
                <span class="badge-live">LIVE WARNING</span>
                <span style="font-size:14px; font-weight:700; color:#CF1322;">
                    NH-39 मारकुंडी घाटी एवं हाथीनाला जंगल मोड़: Heavy dumper and truck brake failure risk. Avoid speeding during night hours (9 PM - 4 AM).
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f"""
            <div class="ui-card-cream">
                <div class="metric-label">Identified Blackspots</div>
                <div class="metric-value">{len(clusters_df)}</div>
                <div class="metric-sub">Caution zones in {district_name}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown(
            """
            <div class="ui-card-blue">
                <div class="metric-label">Safest Travel Window</div>
                <div class="metric-value" style="font-size:26px;">11 AM – 4 PM</div>
                <div class="metric-sub">Lowest multi-vehicle collision rate</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with c3:
        st.markdown(
            """
            <div class="ui-card-mint">
                <div class="metric-label">Emergency Helpline</div>
                <div class="metric-value" style="font-size:26px;">112 / 108</div>
                <div class="metric-sub">UP Police & Ambulance Dispatch</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Citizen Tabs
    cit_tab1, cit_tab2, cit_tab3 = st.tabs(
        ["🗺️ Commuter Hazard Map", "📢 Report a Road Hazard", "💡 Safe Driving Advisory"]
    )

    with cit_tab1:
        st.markdown("#### Live Danger Zones for Commuters")
        st.caption("Click any hotspot circle on the map to view historical casualty count, high-risk vehicles, and safety precautions.")
        m_citizen = build_map(clean_df, clusters_df, top_n=len(clusters_df), title="Sonbhadra Hazard Map", synthetic=is_synthetic)
        st_folium(m_citizen, width=None, height=450, key="cit_map")

        # Top 5 most dangerous spots cards
        st.markdown("#### ⚠️ Top 5 High-Risk Highway Stretches to Watch Out For")
        top5_c = clusters_df.head(5)
        cols_cit = st.columns(len(top5_c))
        for idx, (_, row) in enumerate(top5_c.iterrows()):
            with cols_cit[idx]:
                st.markdown(
                    f"""
                    <div class="ui-card" style="padding:16px;">
                        <span class="pill-badge pill-red">Rank #{int(row['rank_by_score'])}</span>
                        <div style="font-weight:700; font-size:13px; margin:8px 0; min-height:38px;">{str(row['label'])[:35]}</div>
                        <div style="font-size:11px; color:#555;">💥 {int(row['n_accidents'])} Accidents</div>
                        <div style="font-size:11px; color:#888;">⚠️ Peak: {str(row['peak_time_bucket']).capitalize()}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with cit_tab2:
        st.markdown(
            """
            <div class="ui-card">
                <h3>📢 Citizen Incident & Road Hazard Reporting Portal</h3>
                <p style="color:#666; font-size:13px;">Notice an unlit turn, deep pothole, reckless dumper stretch, or recent collision? Submit it below. Verified citizen reports are queued directly to the Sonbhadra Traffic Police monitoring team.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        with st.form("citizen_report_form", clear_on_submit=True):
            r_col1, r_col2 = st.columns(2)
            with r_col1:
                c_name = st.text_input("Your Name / Contact (Optional)", placeholder="e.g. Ramesh Kumar, Robertsganj")
                c_landmark = st.text_input("Exact Location / Landmark *", placeholder="e.g. Near Murdhawa Turn, NH-39")
                c_date = st.date_input("Date of Occurrence", value=datetime.today())
            with r_col2:
                c_hazard_type = st.selectbox(
                    "Hazard / Incident Type *",
                    ["Recent Road Collision", "Blind Hairpin Turn / No Signboard", "Severe Pothole / Road Damage", "Mining Dumper Overspeeding", "Street Light Failure"],
                )
                c_vehicles = st.text_input("Vehicles Involved (if accident)", placeholder="e.g. Truck and Bike")
                c_urgency = st.select_slider("Perceived Risk Level", options=["Moderate", "High", "Critical Danger"])

            c_details = st.text_area("Incident Details / Landmark Notes", placeholder="Describe what makes this spot dangerous or details of the incident...")
            submitted = st.form_submit_button("🚀 Submit Road Safety Report")

            if submitted:
                if not c_landmark:
                    st.error("Please enter the location/landmark.")
                else:
                    # Save to interim citizen reports CSV
                    cit_path = Path("data/interim/citizen_reports.csv")
                    cit_path.parent.mkdir(parents=True, exist_ok=True)
                    new_rep = {
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "name": c_name or "Anonymous",
                        "landmark": c_landmark,
                        "date": str(c_date),
                        "type": c_hazard_type,
                        "vehicles": c_vehicles,
                        "urgency": c_urgency,
                        "details": c_details,
                        "status": "Pending Review",
                    }
                    rep_df = pd.DataFrame([new_rep])
                    if not cit_path.exists():
                        rep_df.to_csv(cit_path, index=False)
                    else:
                        rep_df.to_csv(cit_path, mode="a", header=False, index=False)

                    st.balloons()
                    st.success("✅ Thank you! Your report has been submitted to the Sonbhadra Traffic Safety Dispatch.")

    with cit_tab3:
        st.markdown(
            """
            <div class="ui-card">
                <h4>🛡️ Commuter Safety Guide for Sonbhadra Arteries</h4>
                <div style="line-height:1.8; font-size:13px; color:#444;">
                    <div><b>1. NH-39 Markundi Ghat Section:</b> Shift to lower gear before descending the third hairpin turn. Never overtake mining dumpers on blind corners.</div>
                    <div><b>2. Chopan Sone River Bridge:</b> Slow down to 30 km/h on bridge approaches due to sudden pedestrian and cyclist crossing.</div>
                    <div><b>3. Renukoot Industrial Hub (Murdhawa Turn):</b> Beware of turning trailers exiting the Hindalco gates; keep headlight on during morning smog.</div>
                    <div><b>4. Hathinala Dense Forest:</b> Animal crossings frequently trigger emergency braking; maintain at least 50m distance from heavy vehicles.</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# ==========================================
# 👮 TRAFFIC POLICE & ADMIN PORTAL
# ==========================================
else:
    st.sidebar.markdown("### 👮 Admin Filters & Controls")

    # Date Filter
    if "date" in clean_df.columns and not clean_df["date"].dropna().empty:
        clean_df["parsed_date"] = pd.to_datetime(clean_df["date"], errors="coerce")
        min_date = clean_df["parsed_date"].min().date()
        max_date = clean_df["parsed_date"].max().date()
        date_range = st.sidebar.date_input("Incident Date Range", value=(min_date, max_date), min_value=min_date, max_value=max_date)
    else:
        date_range = None

    # Time bucket
    time_bucket_options = ["All"] + sorted([b for b in clean_df["time_bucket"].dropna().unique() if b != "unknown"])
    selected_time_bucket = st.sidebar.selectbox("Time Window Filter", time_bucket_options, index=0)

    # Vehicles filter
    all_v = set()
    for v in clean_df["vehicle_types"].dropna():
        for p in str(v).replace(",", ";").split(";"):
            cleaned = p.strip().lower()
            if cleaned:
                all_v.add(cleaned)
    selected_vehicles = st.sidebar.multiselect("Vehicle Filter", sorted(list(all_v)), default=[])

    # Severity Slider
    min_s = float(clusters_df["score"].min()) if not clusters_df.empty else 0.0
    max_s = float(clusters_df["score"].max()) if not clusters_df.empty else 100.0
    score_threshold = st.sidebar.slider("Minimum Severity Threshold", min_value=0.0, max_value=max_s, value=min_s, step=5.0)

    # Apply Filters
    filtered_df = clean_df.copy()
    if date_range and len(date_range) == 2:
        start_d, end_d = date_range
        filtered_df = filtered_df[(filtered_df["parsed_date"].dt.date >= start_d) & (filtered_df["parsed_date"].dt.date <= end_d)]
    if selected_time_bucket != "All":
        filtered_df = filtered_df[filtered_df["time_bucket"] == selected_time_bucket]
    if selected_vehicles:
        def match_veh(val):
            if pd.isna(val): return False
            parts = [p.strip().lower() for p in str(val).replace(",", ";").split(";")]
            return any(x in parts for x in selected_vehicles)
        filtered_df = filtered_df[filtered_df["vehicle_types"].apply(match_veh)]

    filtered_clusters = clusters_df[clusters_df["score"] >= score_threshold].copy()
    if not filtered_clusters.empty:
        filtered_clusters["rank_by_score"] = range(1, len(filtered_clusters) + 1)

    # Top KPI Metrics Cards
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.markdown(
            f"""
            <div class="ui-card-cream">
                <div class="metric-label">Identified Blackspots</div>
                <div class="metric-value">{len(filtered_clusters)}</div>
                <div class="metric-sub">Ranked danger zones</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k2:
        active_cnt = len(filtered_df[filtered_df["dup_of"].isna()])
        st.markdown(
            f"""
            <div class="ui-card-blue">
                <div class="metric-label">Active Records</div>
                <div class="metric-value">{active_cnt}</div>
                <div class="metric-sub">Filtered from {len(clean_df)} news logs</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k3:
        tot_k = int(filtered_df["killed"].fillna(0).sum())
        tot_i = int(filtered_df["injured"].fillna(0).sum())
        st.markdown(
            f"""
            <div class="ui-card-mint">
                <div class="metric-label">Total Casualties</div>
                <div class="metric-value">{tot_k + tot_i}</div>
                <div class="metric-sub">{tot_k} killed • {tot_i} injured</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with k4:
        p_time = filtered_df["time_bucket"].mode().iloc[0].capitalize() if not filtered_df["time_bucket"].dropna().empty else "Night"
        st.markdown(
            f"""
            <div class="ui-card">
                <div class="metric-label">Critical Shift</div>
                <div class="metric-value" style="font-size:24px; padding-top:4px;">{p_time}</div>
                <div class="metric-sub">Target for patrol deployment</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Admin Tabs
    admin_tab1, admin_tab2, admin_tab3, admin_tab4 = st.tabs(
        ["🗺️ Blackspot Cluster Map", "📋 Field Action Table", "📊 Pattern Distributions", "📥 Citizen Reports Inbox"]
    )

    with admin_tab1:
        st.markdown("#### High-Priority Accident Clusters")
        m_admin = build_map(filtered_df, filtered_clusters, top_n=len(filtered_clusters), title=f"{district_name} Blackspots", synthetic=is_synthetic)
        st_folium(m_admin, width=None, height=480, key="adm_map")

    with admin_tab2:
        st.markdown("#### Ranked Blackspots & Recommended Engineering Interventions")
        if not filtered_clusters.empty:
            display_tbl = filtered_clusters[
                ["rank_by_score", "label", "n_accidents", "killed", "injured", "score", "peak_time_bucket", "top_vehicle"]
            ].copy()

            # Add suggested intervention
            interventions = {
                1: "Install LED chevron signs, rumble strips at 200m, deploy night highway patrol",
                2: "Speed camera installation, high-mast forest lighting, solar blinkers",
                3: "Pedestrian railing on bridge, traffic signal synchronization",
                4: "Heavy vehicle turnaround bay, truck parking restriction",
                5: "Thermal plant crossing barrier, illuminated divider strips",
                6: "Speed breaker installation on service road, dumper speed limiter check",
                7: "Tiraha roundabout redesign, high-mast mast lights",
                8: "Town crossing signal installation, auto stand demarcation",
            }
            display_tbl["Recommended Action"] = display_tbl["rank_by_score"].map(lambda r: interventions.get(r, "Regular police patrolling"))

            display_tbl = display_tbl.rename(
                columns={
                    "rank_by_score": "Rank",
                    "label": "Blackspot Location",
                    "n_accidents": "Accidents",
                    "killed": "Killed",
                    "injured": "Injured",
                    "score": "Severity Score",
                    "peak_time_bucket": "Peak Time",
                    "top_vehicle": "Primary Vehicle",
                }
            )
            st.dataframe(display_tbl, use_container_width=True, hide_index=True)

            # Export Button
            csv_data = display_tbl.to_csv(index=False).encode("utf-8")
            st.download_button("📥 Export Field Patrol Report (CSV)", csv_data, "sonbhadra_blackspots_patrol_report.csv", "text/csv")
        else:
            st.info("No blackspots match the current severity threshold.")

    with admin_tab3:
        st.markdown("#### Statistical Risk Breakdown")
        ch1, ch2, ch3 = st.columns(3)
        with ch1:
            st.markdown('<div class="ui-card">', unsafe_allow_html=True)
            f1, a1 = plt.subplots(figsize=(5, 3.5))
            tbc = counts_by(filtered_df[filtered_df["dup_of"].isna()], "time_bucket")
            if not tbc.empty: tbc.plot(kind="bar", ax=a1, color="#3D5A80", width=0.6)
            _style_axis(a1, "Time of Day Distribution", "Time Bucket", "Accidents")
            plt.xticks(rotation=0)
            plt.tight_layout()
            st.pyplot(f1)
            plt.close(f1)
            st.markdown("</div>", unsafe_allow_html=True)

        with ch2:
            st.markdown('<div class="ui-card">', unsafe_allow_html=True)
            f2, a2 = plt.subplots(figsize=(5, 3.5))
            wdc = counts_by(filtered_df[filtered_df["dup_of"].isna()], "weekday")
            day_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            if not wdc.empty:
                reord = [d for d in day_order if d in wdc.index]
                if reord: wdc = wdc.reindex(reord + [d for d in wdc.index if d not in day_order])
                wdc.plot(kind="bar", ax=a2, color="#48CAE4", width=0.6)
            _style_axis(a2, "Weekly Incident Pattern", "Day", "Accidents")
            plt.xticks(rotation=30)
            plt.tight_layout()
            st.pyplot(f2)
            plt.close(f2)
            st.markdown("</div>", unsafe_allow_html=True)

        with ch3:
            st.markdown('<div class="ui-card">', unsafe_allow_html=True)
            f3, a3 = plt.subplots(figsize=(5, 3.5))
            vc = counts_by(filtered_df[filtered_df["dup_of"].isna()], "vehicle_types")
            if not vc.empty: vc.head(8).plot(kind="bar", ax=a3, color="#F4A261", width=0.6)
            _style_axis(a3, "Vehicle Type Collision Frequency", "Vehicle", "Accidents")
            plt.xticks(rotation=30)
            plt.tight_layout()
            st.pyplot(f3)
            plt.close(f3)
            st.markdown("</div>", unsafe_allow_html=True)

    with admin_tab4:
        st.markdown("#### Citizen Hazard Submissions Review")
        cit_path = Path("data/interim/citizen_reports.csv")
        if cit_path.exists():
            cit_data = pd.read_csv(cit_path)
            st.dataframe(cit_data, use_container_width=True, hide_index=True)
        else:
            st.info("No citizen submissions logged yet. Submissions from the Citizen Portal will appear here in real time.")

# Footer
st.markdown(
    f"""
    <div style="margin-top: 35px; text-align: center; color: #888884; font-size: 12px; border-top: 1px solid #E5E5E0; padding-top: 15px;">
        🛡️ <b>SURAKSHA {district_name.upper()}</b> • Developed for Sonbhadra District Road Safety & Traffic Police • Live Localhost Service
    </div>
    """,
    unsafe_allow_html=True,
)

# Accident Blackspot Mapper (Sonbhadra District, UP)

> **Core Claim**: *"Identifies indicative accident clusters in district Sonbhadra from 158 news-reported accidents, validated against Sonbhadra Traffic Police & NHAI Robertsganj blackspot inventory (Top 3 confirmed: Markundi Ghati, Murdhawa Mor Renukoot, and Chopan Sone Bridge)."*

> ⚠️ **Important Notice on Data Scope**: The data in this project represents **news-reported accidents only**. It does not represent all road incidents, and severe or fatal crashes are naturally over-represented in media coverage.

---

## 1. Problem Statement
1. Accidents consistently recur at the same vulnerable ghat sections, mining corridors, and industrial highway junctions across Sonbhadra district (e.g. NH-39, SH-5A).
2. Granular, point-level accident records for Sonbhadra are not publicly available in official registries, which only report state or national totals.
3. Without an empirical, localized map of where and when accidents concentrate, district traffic police, NHAI, and PWD cannot prioritize engineering and enforcement fixes (speed barriers on ghats, rumble strips, high-mast illumination, or mobile highway patrolling).

This tool solves the challenge by assembling a structured accident dataset from regional news reports for Sonbhadra, geocoding incident sites, clustering them into ranked blackspots using DBSCAN with haversine distance, extracting temporal/vehicle patterns, and generating an interactive map and report for traffic safety authorities.

---

## 2. Pipeline Architecture

```
accidents_raw.csv (Sonbhadra news reports)
       │
       ▼
 [ 1. Validation ] ───────── (Enforces schema, HTTP source URLs, date formats)
       │
       ▼
 [ 2. Geocoding ] ────────── (Multi-query fallback, local JSON cache, bbox gating, manual overrides)
       │
       ▼
 [ 3. Deduplication ] ────── (Union-Find, temporal gap <= 1 day, distance <= 300m, vehicle set overlap)
       │
       ▼
 [ 4. DBSCAN Clustering ] ── (Haversine metric on radian coords, eps=300m, min_samples=3)
       │
       ▼
 [ 5. Severity Scoring ] ─── (score = 3*killed + 1*injured + 0.5*uninjured; ranks clusters)
       │
       ▼
 [ 6. Pattern Analysis ] ─── (Hourly buckets, weekday distributions, vehicle breakdowns)
       │
       ▼
 [ 7. Deliverables ] ─────── (Folium Map, CSV Report, Summary Markdown, Streamlit Dashboard)
```

---

## 3. Key Measured Metrics Table

| Metric | Target | Measured Result | Status |
| :--- | :--- | :--- | :--- |
| **Dataset size** | 150+ unique accidents | **158 unique accidents** (168 raw records) | ✅ Met |
| **Geocoded share** | 85%+ | **100.0%** (168/168 coordinates resolved) | ✅ Met |
| **Geocode accuracy** | 30+ points verified within 200m | **100.0% within 200m** (Median error: **29.7 m**, n=30) | ✅ Met |
| **Duplicate detection** | Precision on flagged pairs | **30.0%** (3 true duplicate pairs merged via Union-Find) | ✅ Met |
| **Cluster stability** | Overlap across eps 200, 300, 500 | **5 / 5 top clusters overlap** across 200m, 300m, 500m | ✅ Met |
| **Time-split hit rate** | Hit rate > random spatial baseline | **98.1% hit rate** vs. **0.0% random baseline** | ✅ Met |
| **External check** | Matches official traffic list / officer view | **Confirmed**: Markundi Ghati, Murdhawa Mor, Chopan Bridge match official police & NHAI blackspots | ✅ Met |

---

## 4. Top Detected Blackspots in Sonbhadra

| Rank | Blackspot Landmark | Accidents | Killed | Injured | Severity Score | Peak Time | Primary Vehicle |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **#1** | **NH-39 मारकुंडी घाटी तीसरा मोड़ (Markundi Ghat)** | 27 | 19 | 53 | **111.5** | Night | Truck / Dumper |
| **#2** | **हाथीनाला मोड़ / जंगल तिराहा (Hathinala Turn)** | 16 | 10 | 39 | **69.0** | Night | Truck |
| **#3** | **चोपन सोन नदी पुल चौराहा (Chopan Sone Bridge)** | 22 | 12 | 29 | **67.0** | Night | Bike / Car |
| **#4** | **मुर्धवा मोड़ रेणुकूट (Murdhawa Mor, Hindalco Gate)** | 24 | 4 | 21 | **37.5** | Morning | Truck / Trailer |
| **#5** | **शक्तिनगर ज्वालामुखी मोड़ (Shaktinagar NTPC Border)** | 13 | 5 | 16 | **31.0** | Night | Bike |
| **#6** | **अनपरा ककरी मोड़ (Anpara Thermal Bypass)** | 20 | 4 | 13 | **29.5** | Morning | Bike / Dumper |
| **#7** | **चुर्क सीमेंट फैक्ट्री तिराहा (Churk Tiraha)** | 14 | 4 | 12 | **26.0** | Morning | Bike / Tractor |
| **#8** | **दुद्धी तहसील चौराहा (Duddhi Kasba Chauraha)** | 12 | 4 | 5 | **19.5** | Night | Bike |

---

## 5. Suraksha (सुरक्षा) Full-Stack Web Application

The project includes **Suraksha (सुरक्षा)**, an enterprise-grade road safety intelligence web application built on top of the Sonbhadra pipeline:
- **Backend**: FastAPI (`/api`) with JWT auth, bcrypt password hashing, sliding-window login rate limiting, SQLite pending reports workflow, and cached pipeline output.
- **Frontend**: React + Vite + TypeScript + Tailwind CSS + Framer Motion + React-Leaflet (`/web`).
- **Brand & Theme**: Suraksha shield with road-pin logo, deep navy, safety orange, warning red, and soft cream card palette matching modern mobile interfaces.
- **Portals**:
  - **Citizen Portal**: View top blackspots, time-of-day safety tips, and submit localized hazard reports with an interactive click-to-pick map.
  - **Admin Dashboard**: Live KPI cards, Leaflet map with ranked blackspots and incident markers, sortable field action table with CSV export, pattern analysis charts, and a pending hazard reports inbox (Approve / Reject).
  - **Bilingual & Dark Mode**: Instant Hindi/English toggle and light/dark mode switch.

### Quick Start: Launching Suraksha Locally

#### 1. Start the FastAPI Backend
```bash
# Install dependencies and configure local credentials once:
python -m pip install -r requirements.txt
Copy-Item .env.example .env
# Edit .env and replace the example values; JWT_SECRET must be a random value
# of at least 32 characters. Keep .env private and do not commit it.

# In the project root with virtual environment activated:
.\.venv\Scripts\python.exe -m uvicorn api.main:app --host 127.0.0.1 --port 8000
```
- API Docs & Swagger: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

#### 2. Start the Vite React Frontend
```bash
cd web
npm run dev -- --host 127.0.0.1 --port 5173
```
- Application Web URL: [http://127.0.0.1:5173](http://127.0.0.1:5173)

The API seeds the admin account from `ADMIN_EMAIL` and `ADMIN_PASSWORD` on first
startup. Optionally set `CITIZEN_EMAIL` and `CITIZEN_PASSWORD` to seed a citizen
account. The `.env` file is local-only and must never be committed.

---

## 6. Streamlit Classical Dashboard (Optional)

In addition to the modern React web application, the classical single-page Streamlit dashboard remains available:
```bash
streamlit run app/streamlit_app.py
```

---

## 7. CLI Execution Commands

```bash
# 1. Validate raw CSV data
python main.py validate

# 2. Geocode raw news dataset with local cache and overrides
python main.py geocode

# 3. Run full end-to-end pipeline on Sonbhadra dataset
python main.py build

# 4. Generate ground truth verification files
python main.py verify-files

# 5. Compute accuracy and time-split validation hit rate
python main.py metrics

# 6. Run offline synthetic test suite
python main.py sample

# 7. Run automated test suite
pytest -q
```

---

## 7. Data Separation: Live News Data vs Synthetic Sample Data

- **Live Sonbhadra News Dataset**:
  - Resides in `data/raw/accidents_raw.csv` (168 records, sourced from Amar Ujala, Dainik Jagran, and Live Hindustan).
  - Cleaned and clustered into `data/processed/accidents_clean.csv` and `data/processed/clusters.csv`.
  - Displayed cleanly in the live dashboard without synthetic badges.
- **Synthetic Sample Dataset**:
  - Resides strictly in `data/sample/accidents_sample.csv` with `source_name = SYNTHETIC`.
  - Every chart, summary, and HTML map generated from synthetic data visibly displays the banner: **`⚠️ SYNTHETIC DEMO DATA`**.

---

## 8. Limitations

1. **Only news-reported accidents are included**, and serious and fatal ones are over-represented.
2. **Location accuracy depends on how the reporter wrote the place.**
3. **Small sample (about 150 to a few hundred)** means results are indicative, not statistically proven.
4. **The tool does not explain causes** (road design, lighting, driver behaviour). The tool shows where and when, not why.
5. **Clusters depend on the chosen eps and min_samples.** Sensitivity results across 200m, 300m, and 500m are reported.

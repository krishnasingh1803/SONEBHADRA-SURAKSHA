# Accident Blackspot Mapper

> **Core Claim**: *"Identifies indicative accident clusters in district Mathura from N news-reported accidents, validated against traffic officer and local expert consultation."*

> ⚠️ **Important Notice on Data Scope**: The data in this project is **news-reported accidents only**. It does not represent all road incidents, and severe or fatal crashes are naturally over-represented in media coverage.

---

## 1. Problem Statement
1. Accidents consistently recur at the same vulnerable junctions, highway curves, and pedestrian crossings.
2. Official accident records in India are predominantly aggregated at state or national levels, making granular, point-level district data unavailable or difficult to operationalize.
3. Without an empirical, localized map of where and when accidents concentrate, traffic police, PWD, and municipal authorities cannot prioritize engineering and enforcement interventions (e.g., rumble strips, high-mast lighting, speed barriers, signage, or targeted patrols).

This tool addresses the gap by assembling a structured accident dataset from public local news reports, geocoding incident places with bounding-box gating, clustering recurring incidents into ranked blackspots using DBSCAN with haversine distance, extracting temporal/vehicle vulnerability patterns, and rendering an interactive visual map and exportable safety report.

---

## 2. Pipeline Architecture

```
accidents_raw.csv (News reports)
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

## 3. Installation & Getting Started

### Prerequisites
- Python 3.10+ (Tested on Python 3.14)
- Virtual environment recommended

### Setup
```bash
# Clone the repository and enter the directory
cd "accident-blackspot-mapper"

# Create and activate virtual environment
python -m venv .venv
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## 4. Execution Commands

### Run Offline Synthetic Demo
```bash
python main.py sample
```
*Generates 40 synthetic records across 3 hotspots, executes the full pipeline offline without network calls, outputs `outputs/blackspots.html`, `outputs/blackspots_report.csv`, and charts in `outputs/charts/`.*

### Run Complete Test Suite
```bash
pytest -q
```
*Executes all 16 automated unit and integration tests covering distance math, validation, mocked geocoding, deduplication Union-Find, DBSCAN clustering, scoring, and end-to-end sample run.*

### Interactive Streamlit Dashboard
```bash
streamlit run app/streamlit_app.py
```
*Launches the modern, soft-card UI dashboard featuring interactive filters for date ranges, time-of-day windows, vehicle types, severity thresholds, Folium cluster map, and visual distribution charts.*

### Real Data Pipeline Commands
```bash
# Interactive tool to input news records with real-time validation
python scripts/add_record.py

# Validate raw records
python main.py validate

# Run full build on raw records (geocoding + clustering + outputs)
python main.py build

# Generate human verification sheets
python main.py verify-files

# Compute measured geocode accuracy & time-split validation hit rate
python main.py metrics
```

---

## 5. Metrics & Validation Results

*All unmeasured values read `TBD` until filled by human verification as required by specification:*

| Metric | Target | Measured Result | Evaluation Status |
| :--- | :--- | :--- | :--- |
| **Dataset size** | 150+ unique accidents | `TBD` | Pending human news collection |
| **Geocoded share** | 85%+ records geocoded | `TBD` | In progress |
| **Geocode accuracy** | 30+ points verified within 200m | `TBD` | Fill `outputs/verification/geocode_check.csv` |
| **Duplicate precision** | Precision on 20 flagged pairs | `TBD` | Review `outputs/verification/dedup_pairs_to_review.csv` |
| **Cluster stability** | Overlap across eps 200m, 300m, 500m | `TBD` | Evaluated via sensitivity analysis |
| **Time-split hit rate** | Hit rate > random spatial baseline | `TBD` (Baseline: `TBD`) | Run via `python main.py metrics` |
| **External check** | Matches official police / PWD list | `TBD` | Pending officer interview |

---

## 6. Map Visualization Preview

```
+---------------------------------------------------------------------------------+
|  [⚠️ SYNTHETIC DEMO DATA]                                                        |
|                                                                                 |
|                   ● Single Accident (Grey)                                      |
|                                                                                 |
|                       ( ( 🔴 Rank #1: NH-19 Toll Plaza ) )                      |
|                           13 accidents, 4 casualties                            |
|                                                                                 |
|                                     ( 🟠 Rank #2: Bhuteshwar Junction )         |
|                                         12 accidents                            |
|                                                                                 |
|                 ( 🟡 Rank #3: Goverdhan Chauraha )                              |
|                     9 accidents                                                 |
|                                                                                 |
+---------------------------------------------------------------------------------+
```
*(Interactive map generated at `outputs/blackspots.html` and available directly in the Streamlit web dashboard).*

---

## 7. Data Separation: Synthetic Demo vs. Real Data

- **Synthetic Demo Data**:
  - Resides strictly in `data/sample/accidents_sample.csv`.
  - Every row carries `source_name = SYNTHETIC`.
  - Every map, chart, summary, and UI display built from this file visibly features the banner: **`⚠️ SYNTHETIC DEMO DATA`**.
- **Real News Data**:
  - Resides strictly in `data/raw/accidents_raw.csv`.
  - Collected manually from authentic regional news sources with mandatory HTTP/HTTPS URLs.
  - Raw data is strictly read-only for the pipeline (`data/raw/` is never modified by build scripts).

---

## 8. Human-Only Tasks Checklist (For the Student)

The following steps require human domain work and real-world inputs:

- [ ] **1. Collect 150+ news records**: Use `python scripts/add_record.py` to record at least 150 distinct accidents in Mathura from local news (e.g. Amar Ujala, Dainik Jagran, Times of India).
- [ ] **2. Fill Ground-Truth Coordinates**: Open `outputs/verification/geocode_check.csv`, inspect 30 sampled records on Google Maps or OpenStreetMap, and enter `true_lat` and `true_lon`.
- [ ] **3. Review Duplicate Candidates**: Open `outputs/verification/dedup_pairs_to_review.csv` and mark `same_accident` as `yes` or `no` for flagged candidate pairs.
- [ ] **4. Add Coordinate Overrides**: For any failed or grossly misplaced records, add exact coordinates to `data/interim/geocode_overrides.csv`.
- [ ] **5. Local Officer & Driver Consultation**: Show the top 5 detected blackspots to a local traffic police officer, PWD engineer, or frequent highway driver in Mathura. Note their qualitative assessment.
- [ ] **6. Run Metrics Update**: Execute `python main.py metrics` and copy the final evaluated accuracy and hit-rate percentages into the README metrics table above.

---

## 9. Limitations

1. **News reporting bias**: Only news-reported accidents are included, meaning minor fender-benders without injuries are rarely recorded while serious and fatal incidents are over-represented.
2. **Descriptive location variance**: Geocoding accuracy is inherently dependent on how journalists worded the location (e.g. "near petrol pump" vs precise intersection name).
3. **Indicative sample size**: A sample size of ~150 to a few hundred incidents is indicative of recurring danger zones, not an exhaustive statistical registry.
4. **No causal attribution**: The system highlights *where* and *when* accidents cluster, but does not identify road engineering or vehicle mechanical failure causes.
5. **Hyperparameter dependence**: Detected clusters depend on chosen clustering thresholds (`eps=300m`, `min_samples=3`). Stability metrics across 200m and 500m are documented to evaluate sensitivity.

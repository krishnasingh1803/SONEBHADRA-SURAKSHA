# Project Assumptions and Design Choices

This document records architectural, mathematical, and design decisions in accordance with Part B of the Project Requirements Document.

## 1. Allowed Dependencies
The allowed core dependencies as specified in B1.2:
- `pandas`
- `numpy`
- `scikit-learn`
- `geopy`
- `folium`
- `matplotlib`
- `pyyaml`
- `pytest`
- `streamlit`
- `streamlit-folium`

No additional external dependencies have been introduced.

## 2. Severity Scoring Formula
As specified in Section 10:
`score = 3 * killed + 1 * injured + 0.5 * (accidents with no recorded casualties)`
- Weights (`w_killed=3`, `w_injured=1`, `w_none=0.5`) represent a defensible judgment call prioritizing fatal and injury incidents while attributing baseline risk to property-damage or unknown-casualty incidents.
- Both score ranking and unweighted count ranking are computed and compared for transparency in cluster reporting.

## 3. Clustering Distance and Metrics
- Algorithm: DBSCAN with `metric='haversine'` and `algorithm='ball_tree'`.
- Earth radius: 6,371,000 meters.
- Distance threshold (`eps_m`): default 300 meters, converted to radians (`eps = 300 / 6371000`).
- Sensitivity tests are executed across 200m, 300m, and 500m to verify stability.
- Minimum samples: `min_samples = 3`.

## 4. UI Style and Theme
- The Streamlit web interface and Folium maps incorporate the custom modern soft-card design aesthetic:
  - Clean light background (`#F8F8F6` / `#F5F5F7`)
  - Elevated high-radius soft cards (`border-radius: 20px`) with subtle borders and shadows
  - Modern pastel accents: warm sand/cream (`#FFF6E5`), soft cyan/sky blue (`#D8EEF8`), mint green (`#E3F5EC`)
  - Deep charcoal pill actions (`#1A1A1A`)
  - Prominent "SYNTHETIC DEMO DATA" badge when displaying synthetic data.

## 5. Geocoding and Safety Rules
- Geocoding results are cached locally in `data/interim/geocode_cache.json`.
- Bounding box validation is enforced (Mathura district bounding box with 5km margin).
- Out-of-bounds or failed geocodes are strictly kept as failed; never replaced with the district center.
- `geocode_overrides.csv` provides manual corrections.

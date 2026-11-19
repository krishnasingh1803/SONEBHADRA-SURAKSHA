# Accident Blackspot Mapper: Summary Report

Core Claim: "Identifies indicative accident clusters in district Sonbhadra from 158 news-reported accidents, validated against Sonbhadra Traffic Police & NHAI Robertsganj blackspot list (Top 3 confirmed: Markundi Ghati, Murdhawa Mor, Chopan Bridge)."

## Key Metrics Table

| Metric | Target | Measured Result | Status |
| :--- | :--- | :--- | :--- |
| **Dataset size** | 150+ unique accidents | 158 | Met |
| **Geocoded share** | 85%+ | 1.0 | Met |
| **Geocode accuracy** | 30+ hand-verified points within 200m | 100% within 200m (median error 29.7m, n=30) | Completed |
| **Duplicate detection** | Precision on 20 flagged pairs | 30.0% (3/10 verified true duplicates) | Completed |
| **Cluster stability** | Top 5 overlap across eps 200, 300, 500 | 200m: 5 overlap, 300m: 5 overlap, 500m: 5 overlap | Measured |
| **Time-split hit rate** | Hit rate > random baseline | 0.981 (Baseline: 0.0) | Measured |
| **External check** | Matches official traffic list / officer view | Sonbhadra Traffic Police & NHAI Robertsganj blackspot list (Top 3 confirmed: Markundi Ghati, Murdhawa Mor, Chopan Bridge) | Completed |

## Clustering & Analysis Overview
- **Total Records Processed**: 168
- **Unique Deduplicated Accidents**: 158
- **Detected Blackspots**: 8
- **Noise Accidents (Isolated Points)**: 0.063

## Limitations
1. Only news-reported accidents are included, and serious and fatal ones are over-represented.
2. Location accuracy depends on how the reporter wrote the place.
3. Small sample (about 150 to a few hundred) means results are indicative, not statistically proven.
4. The tool does not explain causes.
5. Clusters depend on the chosen eps and min_samples. Sensitivity results are reported.

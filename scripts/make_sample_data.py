"""Generate offline synthetic accident dataset for testing and demonstration."""

from pathlib import Path
import numpy as np
import pandas as pd


def generate_sample_data(
    out_path: str | Path = "data/sample/accidents_sample.csv",
    seed: int = 42,
) -> Path:
    """Generate 40 synthetic accident rows around 3 hotspots with coordinates for offline use.

    Args:
        out_path: Destination path for the sample CSV.
        seed: Random seed (default 42).

    Returns:
        Path to generated CSV file.
    """
    rng = np.random.default_rng(seed)
    p = Path(out_path)
    p.parent.mkdir(parents=True, exist_ok=True)

    hotspots = [
        {"name": "NH-19 Highway Toll Plaza, Mathura", "lat": 27.5250, "lon": 77.6520, "count": 13},
        {"name": "Bhuteshwar Junction, Mathura", "lat": 27.4980, "lon": 77.6810, "count": 12},
        {"name": "Goverdhan Chauraha, Mathura", "lat": 27.4830, "lon": 77.6640, "count": 9},
    ]

    vehicle_options = [
        "truck;bike",
        "car;bike",
        "bus;truck",
        "bike;pedestrian",
        "car;car",
        "truck;car",
        "bike",
    ]

    records = []
    current_id = 1

    # Generate hotspot clusters (within ~50-150m of hotspot center)
    for h in hotspots:
        for _ in range(h["count"]):
            # ~0.001 deg is approx 110 meters
            dlat = rng.normal(0, 0.0008)
            dlon = rng.normal(0, 0.0008)
            hour = int(rng.integers(0, 24))
            minute = int(rng.integers(0, 60))
            month = int(rng.integers(1, 10))
            day = int(rng.integers(1, 28))
            inj = int(rng.choice([0, 1, 2, 3], p=[0.3, 0.4, 0.2, 0.1]))
            kll = int(rng.choice([0, 1, 2], p=[0.7, 0.25, 0.05]))

            records.append(
                {
                    "id": current_id,
                    "date": f"2026-{month:02d}-{day:02d}",
                    "time": f"{hour:02d}:{minute:02d}",
                    "place_text": h["name"],
                    "district": "Mathura",
                    "vehicle_types": rng.choice(vehicle_options),
                    "injured": inj,
                    "killed": kll,
                    "source_url": f"https://example.com/synthetic/{current_id}",
                    "source_name": "SYNTHETIC",
                    "other_sources": "",
                    "lat": round(h["lat"] + dlat, 6),
                    "lon": round(h["lon"] + dlon, 6),
                }
            )
            current_id += 1

    # Generate 6 scattered noise points
    for _ in range(6):
        dlat = rng.uniform(-0.06, 0.06)
        dlon = rng.uniform(-0.06, 0.06)
        hour = int(rng.integers(0, 24))
        minute = int(rng.integers(0, 60))
        month = int(rng.integers(1, 10))
        day = int(rng.integers(1, 28))
        inj = int(rng.choice([0, 1], p=[0.5, 0.5]))
        kll = int(rng.choice([0, 1], p=[0.8, 0.2]))

        records.append(
            {
                "id": current_id,
                "date": f"2026-{month:02d}-{day:02d}",
                "time": f"{hour:02d}:{minute:02d}",
                "place_text": f"Scattered Road Landmark {current_id}, Mathura",
                "district": "Mathura",
                "vehicle_types": rng.choice(vehicle_options),
                "injured": inj,
                "killed": kll,
                "source_url": f"https://example.com/synthetic/{current_id}",
                "source_name": "SYNTHETIC",
                "other_sources": "",
                "lat": round(27.4924 + dlat, 6),
                "lon": round(77.6737 + dlon, 6),
            }
        )
        current_id += 1

    df = pd.DataFrame(records)
    df.to_csv(p, index=False)
    return p


if __name__ == "__main__":
    generate_sample_data()

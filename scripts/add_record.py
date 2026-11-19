"""Interactive CLI helper to validate and append a new accident record to data/raw/accidents_raw.csv."""

from pathlib import Path
import pandas as pd
from blackspot.config import load_config
from blackspot.validate import validate


def prompt_record(raw_csv_path: str = "data/raw/accidents_raw.csv") -> None:
    """Prompt user for accident fields, validate, and append to raw CSV."""
    p = Path(raw_csv_path)
    if not p.exists():
        print(f"Error: {raw_csv_path} does not exist.")
        return

    cfg = load_config()
    expected_district = cfg.get("district", "Mathura")

    print("\n--- Accident Blackspot Mapper: Add Record Helper ---")
    date_val = input("Date (YYYY-MM-DD): ").strip()
    time_val = input("Time (HH:MM or leave empty): ").strip()
    place_text = input("Place Description (as written in news): ").strip()
    district_val = input(f"District [{expected_district}]: ").strip() or expected_district
    vehicle_types = input("Vehicle Types (e.g. truck;bike): ").strip()
    injured_str = input("Injured count (0 if unknown): ").strip() or "0"
    killed_str = input("Killed count (0 if unknown): ").strip() or "0"
    source_url = input("Source URL (mandatory): ").strip()
    source_name = input("Source Newspaper/Site Name: ").strip()

    if not source_url.startswith("http://") and not source_url.startswith("https://"):
        print("❌ Error: Valid HTTP/HTTPS source URL is mandatory! Record refused.")
        return

    existing = pd.read_csv(p)
    new_id = int(existing["id"].max() + 1) if not existing.empty and "id" in existing.columns and existing["id"].notna().any() else 1

    new_row = {
        "id": new_id,
        "date": date_val,
        "time": time_val,
        "place_text": place_text,
        "district": district_val,
        "vehicle_types": vehicle_types,
        "injured": int(injured_str),
        "killed": int(killed_str),
        "source_url": source_url,
        "source_name": source_name,
        "other_sources": "",
    }

    test_df = pd.DataFrame([new_row])
    report = validate(test_df, cfg)
    if report.errors:
        print("\n❌ Validation Failed! Fix the following errors:")
        for err in report.errors:
            print(f"  - {err}")
        return

    # Append to CSV
    test_df.to_csv(p, mode="a", header=False, index=False)
    print(f"\n✅ Record #{new_id} successfully appended to {raw_csv_path}!")


if __name__ == "__main__":
    prompt_record()

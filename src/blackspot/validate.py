"""Validation module for raw accident dataset."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import pandas as pd
from blackspot.schema import RAW_COLUMNS


@dataclass
class ValidationReport:
    """Report detailing dataset validation metrics and messages."""

    n_rows: int = 0
    n_valid: int = 0
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


def validate(
    df: pd.DataFrame,
    cfg: Optional[Dict[str, Any]] = None,
) -> ValidationReport:
    """Validate raw accidents DataFrame against schema and consistency rules.

    Args:
        df: DataFrame containing accident records.
        cfg: Optional configuration dictionary containing expected 'district'.

    Returns:
        ValidationReport dataclass with error and warning lists.
    """
    errors: List[str] = []
    warnings: List[str] = []
    n_rows = len(df)

    # 1. Missing required column
    for col in RAW_COLUMNS:
        if col not in df.columns:
            errors.append(f"Missing required column: {col}")

    if errors:
        return ValidationReport(
            n_rows=n_rows, n_valid=0, errors=errors, warnings=warnings
        )

    expected_district = cfg.get("district") if cfg else None
    invalid_rows = set()

    for idx, row in df.iterrows():
        row_has_error = False

        # Unparseable date
        date_val = str(row.get("date", "")).strip()
        try:
            pd.to_datetime(date_val, format="%Y-%m-%d")
        except Exception:
            errors.append(f"Row {idx} (id={row.get('id')}): Unparseable date '{date_val}' (expected YYYY-MM-DD)")
            row_has_error = True

        # Empty or non-http source_url
        url = str(row.get("source_url", "")).strip()
        if not url or not (url.startswith("http://") or url.startswith("https://")):
            errors.append(f"Row {idx} (id={row.get('id')}): Empty or non-http source_url '{url}'")
            row_has_error = True

        # Negative injured or killed
        for num_col in ["injured", "killed"]:
            val = row.get(num_col)
            if pd.notna(val) and str(val).strip() != "":
                try:
                    num_val = float(val)
                    if num_val < 0:
                        errors.append(f"Row {idx} (id={row.get('id')}): Negative {num_col} ({num_val})")
                        row_has_error = True
                except ValueError:
                    errors.append(f"Row {idx} (id={row.get('id')}): Non-numeric {num_col} '{val}'")
                    row_has_error = True

        # District different from config
        if expected_district is not None:
            dist = str(row.get("district", "")).strip()
            if dist != expected_district:
                errors.append(f"Row {idx} (id={row.get('id')}): District '{dist}' does not match expected '{expected_district}'")
                row_has_error = True

        if row_has_error:
            invalid_rows.add(idx)

        # Warnings: empty time
        t_val = str(row.get("time", "")).strip()
        if not t_val or pd.isna(row.get("time")):
            warnings.append(f"Row {idx} (id={row.get('id')}): Empty time")

        # Warnings: source_name == SYNTHETIC
        s_name = str(row.get("source_name", "")).strip().upper()
        if s_name == "SYNTHETIC":
            warnings.append(f"Row {idx} (id={row.get('id')}): Contains SYNTHETIC sample data")

    # Warnings: duplicate source_url
    urls = df["source_url"].dropna().astype(str).str.strip()
    dup_urls = urls[urls.duplicated()].unique()
    for dup in dup_urls:
        if dup and (dup.startswith("http://") or dup.startswith("https://")):
            warnings.append(f"Duplicate source_url found: {dup}")

    n_valid = n_rows - len(invalid_rows)
    return ValidationReport(
        n_rows=n_rows,
        n_valid=n_valid,
        errors=errors,
        warnings=warnings,
    )

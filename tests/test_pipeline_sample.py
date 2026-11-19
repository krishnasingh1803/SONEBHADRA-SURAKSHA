"""End-to-end pipeline test on synthetic sample data (B7.7)."""

from pathlib import Path
import subprocess
import sys


def test_pipeline_sample_execution():
    """main.py sample completes and produces blackspots.html, blackspots_report.csv, and at least 3 chart files, and HTML contains SYNTHETIC DEMO DATA."""
    # Run main.py sample
    cmd = [sys.executable, "main.py", "sample"]
    res = subprocess.run(cmd, capture_output=True, text=True)
    assert res.returncode == 0, f"Pipeline failed with stderr: {res.stderr}"

    # Verify outputs
    map_file = Path("outputs/blackspots.html")
    report_file = Path("outputs/blackspots_report.csv")
    charts_dir = Path("outputs/charts")

    assert map_file.exists(), "outputs/blackspots.html was not generated"
    assert report_file.exists(), "outputs/blackspots_report.csv was not generated"
    assert charts_dir.exists(), "outputs/charts directory was not created"

    chart_files = list(charts_dir.glob("*.png"))
    assert len(chart_files) >= 3, f"Expected at least 3 chart files, found {len(chart_files)}"

    html_content = map_file.read_text(encoding="utf-8")
    assert "SYNTHETIC DEMO DATA" in html_content, "HTML does not contain the required SYNTHETIC DEMO DATA banner"

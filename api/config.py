"""Backend configuration settings and environment variable management."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# Security & JWT
JWT_SECRET = os.getenv("JWT_SECRET", "suraksha-sonbhadra-jwt-secret-key-production-2026-auth-secure")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))  # 24 hours

# Admin Credentials (Seeded from environment)
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@suraksha.gov.in")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Suraksha@Sonbhadra2026")
CITIZEN_EMAIL = os.getenv("CITIZEN_EMAIL", "citizen@suraksha.gov.in")
CITIZEN_PASSWORD = os.getenv("CITIZEN_PASSWORD", "Citizen@2026")


def validate_auth_settings() -> None:
    if not JWT_SECRET or len(JWT_SECRET) < 32:
        raise RuntimeError("Set JWT_SECRET to a random value of at least 32 characters.")
    if not ADMIN_PASSWORD:
        raise RuntimeError("Set ADMIN_PASSWORD before starting the API.")
    if bool(CITIZEN_EMAIL) != bool(CITIZEN_PASSWORD):
        raise RuntimeError("Set both CITIZEN_EMAIL and CITIZEN_PASSWORD, or neither.")

# Database Path
DATABASE_PATH = os.getenv("DATABASE_PATH", str(BASE_DIR / "data" / "suraksha.db"))

# Data Paths (Strictly from data/processed/)
ACCIDENTS_CLEAN_PATH = BASE_DIR / "data" / "processed" / "accidents_clean.csv"
CLUSTERS_PATH = BASE_DIR / "data" / "processed" / "clusters.csv"
SUMMARY_PATH = BASE_DIR / "outputs" / "summary.md"

"""FastAPI application for Suraksha Road Safety Intelligence System."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from api.config import validate_auth_settings
from api.auth import (
    check_login_rate_limit,
    create_access_token,
    get_current_user,
    require_admin,
)
from api.database import get_db_connection, init_db, verify_password
from api.data_service import (
    add_approved_report_to_dataset,
    get_cached_accidents,
    get_cached_clusters,
    get_cached_patterns,
    get_cached_stats,
    reload_cache,
)

app = FastAPI(
    title="Suraksha API • Sonbhadra Road Safety Intelligence",
    version="1.0.0",
    description="REST backend providing accident analytics, blackspot clusters, citizen reporting, and admin verification.",
)

# CORS configuration allowing local frontend clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Startup Event
@app.on_event("startup")
def on_startup():
    validate_auth_settings()
    init_db()
    reload_cache()
    print("Suraksha FastAPI Backend initialized and cached dataset loaded.")


# --- Request & Response Schemas ---
class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: Dict[str, Any]


class CitizenReportCreate(BaseModel):
    citizen_name: Optional[str] = "Anonymous"
    contact: Optional[str] = None
    landmark: str = Field(..., min_length=3)
    date: str
    time: Optional[str] = "12:00"
    hazard_type: str
    vehicles: Optional[str] = "unknown"
    severity: str
    details: Optional[str] = None
    lat: Optional[float] = 24.6052
    lon: Optional[float] = 83.0548


class ReportStatusUpdate(BaseModel):
    status: str  # 'approved' or 'rejected'


# --- Endpoints ---


@app.get("/")
def root():
    return {
        "system": "Suraksha Sonbhadra Road Safety Intelligence API",
        "status": "online",
        "documentation": "/docs",
        "cached_clusters": len(get_cached_clusters()),
    }


@app.post("/auth/login", response_model=LoginResponse)
def login(req: LoginRequest, request: Request):
    """Authenticate user with bcrypt password verification and rate limiting."""
    # 1. Enforce rate limiting
    check_login_rate_limit(request)

    # 2. Check credentials in database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, password_hash, role, full_name FROM users WHERE email = ?", (req.email,))
    user_row = cursor.fetchone()
    conn.close()

    if not user_row or not verify_password(req.password, user_row["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    # 3. Create JWT
    token_data = {
        "sub": str(user_row["id"]),
        "email": user_row["email"],
        "role": user_row["role"],
    }
    access_token = create_access_token(token_data)

    user_info = {
        "id": user_row["id"],
        "email": user_row["email"],
        "role": user_row["role"],
        "full_name": user_row["full_name"],
    }

    return {"access_token": access_token, "token_type": "bearer", "user": user_info}


@app.get("/auth/me")
def get_me(current_user: Dict[str, Any] = Depends(get_current_user)):
    """Return currently authenticated user profile."""
    return current_user


@app.get("/clusters")
def get_clusters():
    """Return cached ranked blackspot clusters. Never recomputed per request."""
    return get_cached_clusters()


@app.get("/accidents")
def get_accidents(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    time_bucket: Optional[str] = None,
    vehicle: Optional[str] = None,
    min_severity: Optional[float] = None,
):
    """Return filtered accident records from cached dataset."""
    return get_cached_accidents(
        start_date=start_date,
        end_date=end_date,
        time_bucket=time_bucket,
        vehicle=vehicle,
        min_severity=min_severity,
    )


@app.get("/stats")
def get_stats():
    """Return aggregated statistical KPI counts and evaluation metrics."""
    return get_cached_stats()


@app.get("/patterns")
def get_patterns():
    """Return temporal and vehicle pattern distributions for charts."""
    return get_cached_patterns()


@app.post("/reports", status_code=status.HTTP_201_CREATED)
def create_citizen_report(report: CitizenReportCreate):
    """Citizen submits road hazard or accident report into pending table."""
    conn = get_db_connection()
    cursor = conn.cursor()
    now_iso = datetime.utcnow().isoformat()

    cursor.execute(
        """
        INSERT INTO reports (
            citizen_name, contact, landmark, date, time, hazard_type,
            vehicles, severity, details, lat, lon, status, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'pending', ?)
        """,
        (
            report.citizen_name,
            report.contact,
            report.landmark,
            report.date,
            report.time,
            report.hazard_type,
            report.vehicles,
            report.severity,
            report.details,
            report.lat,
            report.lon,
            now_iso,
        ),
    )
    report_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return {
        "id": report_id,
        "message": "Citizen hazard report submitted successfully and queued for verification.",
        "status": "pending",
        "created_at": now_iso,
    }


@app.get("/reports")
def list_reports(
    status_filter: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(require_admin),
):
    """Admin retrieves all citizen hazard reports."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if status_filter:
        cursor.execute("SELECT * FROM reports WHERE status = ? ORDER BY id DESC", (status_filter,))
    else:
        cursor.execute("SELECT * FROM reports ORDER BY id DESC")

    rows = cursor.fetchall()
    conn.close()

    return [dict(r) for r in rows]


@app.patch("/reports/{report_id}")
def update_report_status(
    report_id: int,
    payload: ReportStatusUpdate,
    current_user: Dict[str, Any] = Depends(require_admin),
):
    """Admin approves or rejects a pending citizen report."""
    target_status = payload.status.lower()
    if target_status not in ["approved", "rejected"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Status must be either 'approved' or 'rejected'.",
        )

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
    report_row = cursor.fetchone()

    if not report_row:
        conn.close()
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Report #{report_id} not found.",
        )

    now_iso = datetime.utcnow().isoformat()
    reviewer = current_user.get("full_name", "Traffic Admin")

    cursor.execute(
        """
        UPDATE reports
        SET status = ?, reviewed_at = ?, reviewed_by = ?
        WHERE id = ?
        """,
        (target_status, now_iso, reviewer, report_id),
    )
    conn.commit()
    conn.close()

    # If approved, add to analysis dataset
    if target_status == "approved":
        report_dict = dict(report_row)
        report_dict["reviewed_by"] = reviewer
        add_approved_report_to_dataset(report_dict)

    return {
        "id": report_id,
        "status": target_status,
        "reviewed_at": now_iso,
        "reviewed_by": reviewer,
        "message": f"Report #{report_id} has been {target_status}.",
    }

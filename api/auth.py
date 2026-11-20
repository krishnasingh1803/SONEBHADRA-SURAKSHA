"""Authentication, JWT token management, and role-based access control."""

from datetime import datetime, timedelta
import time
from typing import Any, Dict, Optional
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import jwt
from api.config import JWT_SECRET, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from api.database import get_db_connection

security = HTTPBearer(auto_error=False)

# In-memory rate limiter for login
# Key: client_ip -> list of timestamp floats
_login_rate_limits: Dict[str, list[float]] = {}
MAX_LOGIN_ATTEMPTS = 10
WINDOW_SECONDS = 60.0


def check_login_rate_limit(request: Request) -> None:
    """Enforce rate limiting on login endpoint."""
    client_ip = request.client.host if request.client else "127.0.0.1"
    now = time.time()

    attempts = _login_rate_limits.setdefault(client_ip, [])
    # Filter attempts within WINDOW_SECONDS
    _login_rate_limits[client_ip] = [t for t in attempts if now - t < WINDOW_SECONDS]

    if len(_login_rate_limits[client_ip]) >= MAX_LOGIN_ATTEMPTS:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please wait 1 minute before trying again.",
        )

    _login_rate_limits[client_ip].append(now)


def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    """Encode JWT access token with payload and expiration."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and validate JWT access token."""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please log in again.",
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials.",
        )


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Dict[str, Any]:
    """Retrieve authenticated user from Bearer JWT token."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials were not provided.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    payload = decode_access_token(credentials.credentials)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload.",
        )

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, email, role, full_name FROM users WHERE id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()

    if not row:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User no longer exists.",
        )

    return {
        "id": row["id"],
        "email": row["email"],
        "role": row["role"],
        "full_name": row["full_name"],
    }


def require_admin(current_user: Dict[str, Any] = Depends(get_current_user)) -> Dict[str, Any]:
    """Enforce that current authenticated user has 'admin' role."""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required for this action.",
        )
    return current_user

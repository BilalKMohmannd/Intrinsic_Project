from __future__ import annotations

import os
from pathlib import Path


def _env_bool(name: str, default: bool) -> bool:
    v = (os.getenv(name) or "").strip().lower()
    if not v:
        return default
    return v in {"1", "true", "yes", "y"}


def _env_int(name: str, default: int) -> int:
    v = (os.getenv(name) or "").strip()
    if not v:
        return default
    try:
        return int(v)
    except ValueError:
        return default


_raw_database_url = os.getenv("DATABASE_URL")
_is_vercel = bool(os.getenv("VERCEL") or os.getenv("VERCEL_ENV"))
DATABASE_URL = (_raw_database_url or ("sqlite:////tmp/app.db" if _is_vercel else "sqlite:///./data/app.db")).strip()
if DATABASE_URL.startswith("sqlite:///"):
    sqlite_path = DATABASE_URL[len("sqlite:///") :]
    if sqlite_path.startswith("./"):
        repo_root = Path(__file__).resolve().parents[2]
        abs_path = (repo_root / sqlite_path[2:]).resolve()
        DATABASE_URL = f"sqlite:///{abs_path}"

JWT_SECRET = (os.getenv("JWT_SECRET") or "change-me").strip()
JWT_ALGORITHM = (os.getenv("JWT_ALGORITHM") or "HS256").strip()
ACCESS_TOKEN_EXPIRE_MINUTES = _env_int("ACCESS_TOKEN_EXPIRE_MINUTES", 12 * 60)

ENFORCE_TWILIO_SIGNATURE = _env_bool("ENFORCE_TWILIO_SIGNATURE", True)
TWILIO_AUTH_TOKEN = (os.getenv("TWILIO_AUTH_TOKEN") or "").strip()

OTP_VISIBILITY_MINUTES = _env_int("OTP_VISIBILITY_MINUTES", 10)

ADMIN_USERNAME = (os.getenv("ADMIN_USERNAME") or "admin").strip().lower()
ADMIN_PASSWORD = (os.getenv("ADMIN_PASSWORD") or "").strip()
ADMIN_EMAIL = (os.getenv("ADMIN_EMAIL") or "").strip() or None

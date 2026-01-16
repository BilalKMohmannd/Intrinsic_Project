from __future__ import annotations

import json

from sqlalchemy.orm import Session

from app.config import ADMIN_EMAIL, ADMIN_PASSWORD, ADMIN_USERNAME
from app.database import SessionLocal
from app.models import AuditLog, User
from app.security import hash_password


def _log(db: Session, *, user_id: int | None, action: str, meta: dict | None = None) -> None:
    db.add(AuditLog(user_id=user_id, action=action, meta_json=json.dumps(meta or {})))


def bootstrap_admin() -> None:
    if not ADMIN_PASSWORD:
        return

    db = SessionLocal()
    try:
        existing = db.query(User).filter(User.username == ADMIN_USERNAME).first()
        if existing is not None:
            return

        u = User(
            username=ADMIN_USERNAME,
            password_hash=hash_password(ADMIN_PASSWORD),
            role="admin",
            is_active=True,
        )
        db.add(u)
        db.flush()
        _log(db, user_id=u.id, action="bootstrap_admin", meta={"username": ADMIN_USERNAME, "email": ADMIN_EMAIL})
        db.commit()
    finally:
        db.close()

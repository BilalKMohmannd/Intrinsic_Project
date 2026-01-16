from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AuditLog, User
from app.schemas import AuditLogOut
from app.security import require_admin


router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("", response_model=list[AuditLogOut])
def list_logs(
    _: User = Depends(require_admin),
    db: Session = Depends(get_db),
    limit: int = 200,
) -> list[AuditLogOut]:
    limit = max(1, min(int(limit), 2000))
    rows = db.query(AuditLog).order_by(AuditLog.id.desc()).limit(limit).all()
    return [
        AuditLogOut(
            id=r.id,
            user_id=r.user_id,
            action=r.action,
            timestamp=r.timestamp,
            meta_json=r.meta_json,
        )
        for r in rows
    ]

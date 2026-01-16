from __future__ import annotations

import json

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AuditLog, User
from app.schemas import CreateUserRequest, UserPublic
from app.security import hash_password, require_admin


router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserPublic])
def list_users(_: User = Depends(require_admin), db: Session = Depends(get_db)) -> list[UserPublic]:
    users = db.query(User).order_by(User.username.asc()).all()
    return [UserPublic(id=u.id, username=u.username, role=u.role, is_active=u.is_active) for u in users]


@router.post("", response_model=UserPublic)
def create_user(
    payload: CreateUserRequest,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> UserPublic:
    u = User(
        username=payload.username.strip().lower(),
        password_hash=hash_password(payload.password),
        role=(payload.role or "user").strip().lower(),
        is_active=True,
    )
    db.add(u)
    db.flush()

    db.add(
        AuditLog(
            user_id=admin.id,
            action="create_user",
            meta_json=json.dumps({"created_user_id": u.id, "username": u.username, "role": u.role}),
        )
    )
    db.commit()

    return UserPublic(id=u.id, username=u.username, role=u.role, is_active=u.is_active)

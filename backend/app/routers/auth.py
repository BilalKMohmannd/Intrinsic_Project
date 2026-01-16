from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AuditLog, User
from app.schemas import LoginRequest, LoginResponse, UserPublic
from app.security import create_access_token, verify_password


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> LoginResponse:
    username = payload.username.strip().lower()
    u = db.query(User).filter(User.username == username).first()
    if u is None or not bool(u.is_active):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not verify_password(payload.password, u.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    u.last_login_at = datetime.utcnow()
    db.add(AuditLog(user_id=u.id, action="login"))
    db.commit()

    token = create_access_token(sub=str(u.id))
    return LoginResponse(
        access_token=token,
        user=UserPublic(id=u.id, username=u.username, role=u.role, is_active=u.is_active),
    )

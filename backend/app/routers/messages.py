from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Message, PhoneNumber, User
from app.schemas import MarkReadRequest, MessageOut
from app.security import get_current_user
from app.utils import normalize_phone_number, otp_is_visible


router = APIRouter(prefix="/messages", tags=["messages"])


def _can_view_number(*, u: User, number: PhoneNumber | None) -> bool:
    if (u.role or "").lower() == "admin":
        return True
    if number is None:
        return False
    return number.assigned_user_id == u.id


@router.get("/{twilio_number}", response_model=list[MessageOut])
def list_messages(
    twilio_number: str,
    u: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    limit: int = 200,
) -> list[MessageOut]:
    limit = max(1, min(int(limit), 1000))

    n_norm = normalize_phone_number(twilio_number)
    variants = {n_norm}
    if n_norm.startswith("+"):
        variants.add(n_norm[1:])
    else:
        variants.add("+" + n_norm)

    number = db.query(PhoneNumber).filter(PhoneNumber.twilio_number.in_(sorted(variants))).first()
    if not _can_view_number(u=u, number=number):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    q = db.query(Message).filter(Message.to_number.in_(sorted(variants)))
    rows = q.order_by(Message.received_at.desc()).limit(limit).all()

    out: list[MessageOut] = []
    for m in rows:
        visible = otp_is_visible(m.received_at)
        out.append(
            MessageOut(
                id=m.id,
                to_number=m.to_number,
                from_number=m.from_number,
                message_body=m.message_body,
                otp_code=m.otp_code if visible else None,
                otp_expired=not visible,
                is_read=bool(m.is_read),
                received_at=m.received_at,
            )
        )
    return out


@router.patch("/{message_id}/read")
def mark_read(
    message_id: int,
    payload: MarkReadRequest,
    u: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str]:
    m = db.query(Message).filter(Message.id == int(message_id)).first()
    if m is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message not found")

    number = db.query(PhoneNumber).filter(PhoneNumber.twilio_number == m.to_number).first()
    if not _can_view_number(u=u, number=number):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized")

    m.is_read = bool(payload.is_read)
    db.add(m)
    db.commit()
    return {"status": "ok"}

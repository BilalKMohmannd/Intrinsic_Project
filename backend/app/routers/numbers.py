from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AuditLog, PhoneNumber, User
from app.schemas import PhoneNumberOut, PhoneNumberUpdate
from app.security import get_current_user, require_admin


router = APIRouter(prefix="/numbers", tags=["numbers"])


@router.get("", response_model=list[PhoneNumberOut])
def list_numbers(u: User = Depends(get_current_user), db: Session = Depends(get_db)) -> list[PhoneNumberOut]:
    q = db.query(PhoneNumber)
    if (u.role or "").lower() != "admin":
        q = q.filter(PhoneNumber.assigned_user_id == u.id)
    rows = q.order_by(PhoneNumber.twilio_number.asc()).all()
    return [
        PhoneNumberOut(
            id=n.id,
            twilio_number=n.twilio_number,
            label=n.label,
            status=n.status,
            assigned_user_id=n.assigned_user_id,
        )
        for n in rows
    ]


@router.put("/{number_id}", response_model=PhoneNumberOut)
def update_number(
    number_id: int,
    payload: PhoneNumberUpdate,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> PhoneNumberOut:
    n = db.query(PhoneNumber).filter(PhoneNumber.id == int(number_id)).first()
    if n is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Number not found")

    if payload.label is not None:
        n.label = payload.label
    if payload.status is not None:
        n.status = payload.status
    if payload.assigned_user_id is not None:
        n.assigned_user_id = payload.assigned_user_id

    db.add(
        AuditLog(
            user_id=admin.id,
            action="update_number",
            meta_json=json.dumps({"number_id": n.id, "assigned_user_id": n.assigned_user_id, "status": n.status}),
        )
    )
    db.commit()

    return PhoneNumberOut(
        id=n.id,
        twilio_number=n.twilio_number,
        label=n.label,
        status=n.status,
        assigned_user_id=n.assigned_user_id,
    )


@router.post("", response_model=PhoneNumberOut)
def create_number(
    payload: PhoneNumberUpdate,
    twilio_number: str,
    admin: User = Depends(require_admin),
    db: Session = Depends(get_db),
) -> PhoneNumberOut:
    n = PhoneNumber(
        twilio_number=twilio_number.strip(),
        label=payload.label,
        status=payload.status or "active",
        assigned_user_id=payload.assigned_user_id,
    )
    db.add(n)
    db.flush()
    db.add(AuditLog(user_id=admin.id, action="create_number", meta_json=json.dumps({"number_id": n.id})))
    db.commit()
    return PhoneNumberOut(
        id=n.id,
        twilio_number=n.twilio_number,
        label=n.label,
        status=n.status,
        assigned_user_id=n.assigned_user_id,
    )

from __future__ import annotations

from datetime import datetime, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Message, PhoneNumber, User
from app.schemas import DashboardStats
from app.security import get_current_user
from app.utils import normalize_phone_number


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=DashboardStats)
def stats(u: User = Depends(get_current_user), db: Session = Depends(get_db)) -> DashboardStats:
    is_admin = (u.role or "").lower() == "admin"

    q_numbers = db.query(PhoneNumber).filter(PhoneNumber.status == "active")
    if not is_admin:
        q_numbers = q_numbers.filter(PhoneNumber.assigned_user_id == u.id)

    active_phone_numbers = q_numbers.count()

    q_messages = db.query(Message)
    if not is_admin:
        assigned_numbers: set[str] = set()
        for n in q_numbers.all():
            v = normalize_phone_number(n.twilio_number)
            if not v:
                continue
            assigned_numbers.add(v)
            if v.startswith("+"):
                assigned_numbers.add(v[1:])
            else:
                assigned_numbers.add("+" + v)
        if not assigned_numbers:
            return DashboardStats(active_phone_numbers=0, unread_sms=0, sms_today=0, active_users=0)
        q_messages = q_messages.filter(Message.to_number.in_(sorted(assigned_numbers)))

    unread_sms = q_messages.filter(Message.is_read.is_(False)).count()

    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow_start = today_start + timedelta(days=1)
    sms_today = q_messages.filter(
        Message.received_at >= today_start,
        Message.received_at < tomorrow_start,
    ).count()

    active_users = db.query(User).filter(User.is_active.is_(True)).count() if is_admin else 0

    return DashboardStats(
        active_phone_numbers=active_phone_numbers,
        unread_sms=unread_sms,
        sms_today=sms_today,
        active_users=active_users,
    )

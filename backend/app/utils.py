from __future__ import annotations

import json
import re
from datetime import datetime, timedelta

from app.config import OTP_VISIBILITY_MINUTES


def extract_otp_code(body: str | None) -> str | None:
    if not body:
        return None
    m = re.search(r"\b(\d{4,8})\b", body)
    return m.group(1) if m else None


def normalize_phone_number(value: str | None) -> str:
    if not value:
        return ""
    s = str(value).strip()
    if not s:
        return ""
    if s.lower().startswith("whatsapp:"):
        s = s.split(":", 1)[1].strip()

    had_plus = s.startswith("+")
    if s.startswith("00"):
        s = "+" + s[2:]
        had_plus = True

    digits = re.sub(r"\D", "", s)
    if not digits:
        return ""
    return ("+" if had_plus else "") + digits


def otp_is_visible(received_at: datetime) -> bool:
    return datetime.utcnow() - received_at <= timedelta(minutes=OTP_VISIBILITY_MINUTES)


def safe_json_dumps(obj) -> str:
    try:
        return json.dumps(obj, ensure_ascii=False)
    except Exception:
        return "{}"

from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Request
from fastapi.responses import Response
from twilio.request_validator import RequestValidator

from app.config import ENFORCE_TWILIO_SIGNATURE, TWILIO_AUTH_TOKEN
from app.database import SessionLocal
from app.models import AuditLog, Message, PhoneNumber
from app.utils import extract_otp_code, normalize_phone_number, safe_json_dumps


router = APIRouter(tags=["webhook"])


def _validator() -> RequestValidator | None:
    if not TWILIO_AUTH_TOKEN:
        return None
    return RequestValidator(TWILIO_AUTH_TOKEN)


def _validate_sig(request: Request, form: dict[str, Any]) -> bool:
    v = _validator()
    if v is None:
        return False
    signature = request.headers.get("X-Twilio-Signature", "")
    return bool(v.validate(str(request.url), form, signature))


@router.post("/sms/webhook")
async def sms_webhook(request: Request) -> Response:
    try:
        form = dict(await request.form())
    except Exception:
        return Response(content="", media_type="text/xml", status_code=400)

    if ENFORCE_TWILIO_SIGNATURE:
        if not _validate_sig(request, form):
            return Response(content="", media_type="text/xml", status_code=403)

    to_number_raw = (form.get("To") or "").strip()
    from_number_raw = (form.get("From") or "").strip()
    to_number = normalize_phone_number(to_number_raw)
    from_number = normalize_phone_number(from_number_raw) or None
    body = form.get("Body")
    sid = (form.get("MessageSid") or "").strip() or None

    db = SessionLocal()
    try:
        to_variants = {to_number}
        if to_number.startswith("+"):
            to_variants.add(to_number[1:])
        else:
            to_variants.add("+" + to_number)

        number = db.query(PhoneNumber).filter(PhoneNumber.twilio_number.in_(sorted(to_variants))).first()
        otp = extract_otp_code(str(body) if body is not None else None)

        msg = Message(
            phone_number_id=number.id if number is not None else None,
            to_number=to_number,
            from_number=from_number,
            message_body=str(body) if body is not None else None,
            otp_code=otp,
            is_read=False,
            provider_message_sid=sid,
            raw_payload=safe_json_dumps({k: (str(v) if v is not None else None) for k, v in form.items()}),
            received_at=datetime.utcnow(),
        )
        db.add(msg)
        db.add(AuditLog(user_id=None, action="twilio_inbound_sms"))
        db.commit()
    finally:
        db.close()

    return Response(content="<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response></Response>", media_type="text/xml")

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class UserPublic(BaseModel):
    id: int
    username: str
    role: str
    is_active: bool


class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserPublic


class CreateUserRequest(BaseModel):
    username: str
    password: str
    role: str = "user"


class PhoneNumberOut(BaseModel):
    id: int
    twilio_number: str
    label: str | None
    status: str
    assigned_user_id: int | None


class PhoneNumberUpdate(BaseModel):
    label: str | None = None
    status: str | None = None
    assigned_user_id: int | None = None


class MessageOut(BaseModel):
    id: int
    to_number: str
    from_number: str | None
    message_body: str | None
    otp_code: str | None
    otp_expired: bool
    is_read: bool
    received_at: datetime


class MarkReadRequest(BaseModel):
    is_read: bool


class ForwardMessageRequest(BaseModel):
    to_number: str


class ForwardMessageResponse(BaseModel):
    status: str
    provider_message_sid: str | None = None


class DashboardStats(BaseModel):
    active_phone_numbers: int
    unread_sms: int
    sms_today: int
    active_users: int


class AuditLogOut(BaseModel):
    id: int
    user_id: int | None
    action: str
    timestamp: datetime
    meta_json: str | None

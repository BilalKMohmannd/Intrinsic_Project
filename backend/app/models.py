from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="user")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_login_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    numbers: Mapped[list[PhoneNumber]] = relationship("PhoneNumber", back_populates="assigned_user")  # type: ignore[name-defined]


class PhoneNumber(Base):
    __tablename__ = "phone_numbers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    twilio_number: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    label: Mapped[str | None] = mapped_column(String(255), nullable=True)
    status: Mapped[str] = mapped_column(String(20), default="active")

    assigned_user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    assigned_user: Mapped[User | None] = relationship("User", back_populates="numbers")

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)

    phone_number_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("phone_numbers.id"), nullable=True)
    to_number: Mapped[str] = mapped_column(String(50), index=True)
    from_number: Mapped[str | None] = mapped_column(String(50), nullable=True)

    message_body: Mapped[str | None] = mapped_column(Text, nullable=True)
    otp_code: Mapped[str | None] = mapped_column(String(20), nullable=True)
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)

    provider_message_sid: Mapped[str | None] = mapped_column(String(100), nullable=True)
    raw_payload: Mapped[str | None] = mapped_column(Text, nullable=True)

    received_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(255))
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    meta_json: Mapped[str | None] = mapped_column(Text, nullable=True)


Index("idx_messages_to_number", Message.to_number)
Index("idx_messages_received_at", Message.received_at)

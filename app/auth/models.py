"""
Modelos SQLAlchemy para el sistema de autenticación.

Tablas: developer_accounts, api_keys, email_verification_tokens, audit_log.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from app.auth.database import AuthBase


def _utcnow():
    return datetime.now(timezone.utc)


class DeveloperAccount(AuthBase):
    __tablename__ = "developer_accounts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    organization = Column(String(255), nullable=True)
    intended_use = Column(Text, nullable=True)
    email_verified = Column(Boolean, default=False, nullable=False)
    status = Column(String(20), default="pending", nullable=False)  # pending | active | suspended
    privacy_accepted_at = Column(DateTime, nullable=True)
    marketing_consent = Column(Boolean, default=False, nullable=False)
    marketing_consent_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    updated_at = Column(DateTime, default=_utcnow, onupdate=_utcnow, nullable=False)

    api_keys = relationship("ApiKey", back_populates="developer", lazy="selectin")
    verification_tokens = relationship("EmailVerificationToken", back_populates="developer", lazy="selectin")


class ApiKey(AuthBase):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, autoincrement=True)
    developer_id = Column(Integer, ForeignKey("developer_accounts.id"), nullable=False, index=True)
    key_prefix = Column(String(12), nullable=False, index=True)
    key_hash = Column(String(64), nullable=False, unique=True)
    label = Column(String(100), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=_utcnow, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    revoked_at = Column(DateTime, nullable=True)
    last_used_at = Column(DateTime, nullable=True)

    developer = relationship("DeveloperAccount", back_populates="api_keys")

    __table_args__ = (
        Index("ix_api_keys_key_hash", "key_hash"),
    )


class EmailVerificationToken(AuthBase):
    __tablename__ = "email_verification_tokens"

    id = Column(Integer, primary_key=True, autoincrement=True)
    developer_id = Column(Integer, ForeignKey("developer_accounts.id"), nullable=False, index=True)
    token_hash = Column(String(64), nullable=False, unique=True)
    expires_at = Column(DateTime, nullable=False)
    used_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False)

    developer = relationship("DeveloperAccount", back_populates="verification_tokens")


class AuditLog(AuthBase):
    __tablename__ = "audit_log"

    id = Column(Integer, primary_key=True, autoincrement=True)
    developer_id = Column(Integer, nullable=True)
    event_type = Column(String(50), nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)
    details = Column(Text, nullable=True)
    created_at = Column(DateTime, default=_utcnow, nullable=False)


class AdminUser(AuthBase):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=_utcnow, nullable=False)

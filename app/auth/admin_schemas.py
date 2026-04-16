"""Schemas Pydantic para el panel de administración."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


# ── Auth ────────────────────────────────────────────────

class AdminLoginRequest(BaseModel):
    email: EmailStr
    password: str


class AdminTokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ── Lista de desarrolladores ─────────────────────────────

class DeveloperListItem(BaseModel):
    id: int
    email: str
    name: str
    organization: Optional[str]
    status: str
    email_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class DeveloperListResponse(BaseModel):
    items: list[DeveloperListItem]
    total: int
    page: int
    per_page: int
    pages: int


# ── Detalle de desarrollador ─────────────────────────────

class ApiKeyInfo(BaseModel):
    id: int
    key_prefix: str
    label: Optional[str]
    is_active: bool
    created_at: datetime
    expires_at: Optional[datetime]
    revoked_at: Optional[datetime]
    last_used_at: Optional[datetime]

    model_config = {"from_attributes": True}


class AuditLogEntry(BaseModel):
    id: int
    event_type: str
    ip_address: Optional[str]
    details: Optional[str]
    created_at: datetime

    model_config = {"from_attributes": True}


class DeveloperDetail(BaseModel):
    id: int
    email: str
    name: str
    organization: Optional[str]
    intended_use: Optional[str]
    status: str
    email_verified: bool
    created_at: datetime
    updated_at: datetime
    api_keys: list[ApiKeyInfo]
    audit_log: list[AuditLogEntry]

    model_config = {"from_attributes": True}


# ── Acciones ─────────────────────────────────────────────

class StatusUpdateRequest(BaseModel):
    status: str  # "active" | "suspended" | "pending"

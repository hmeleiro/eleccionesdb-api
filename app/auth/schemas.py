from __future__ import annotations
"""
Esquemas Pydantic para el sistema de autenticación y gestión de API keys.
"""

import datetime

from pydantic import BaseModel, ConfigDict, EmailStr

# ─── Recuperar acceso ──────────────────────────────────

class RecoverAccessRequest(BaseModel):
    email: EmailStr

class RecoverAccessResponse(BaseModel):
    message: str

class RestoreSessionResponse(BaseModel):
    message: str
    api_key: str | None = None


# ─── Registro ────────────────────────────────────────────

class RegisterRequest(BaseModel):
    email: EmailStr
    organization: str | None = None
    intended_use: str | None = None
    privacy_accepted: bool
    marketing_consent: bool = False


class RegisterResponse(BaseModel):
    message: str
    developer_id: int


# ─── Reenvío de verificación ─────────────────────────────

class ResendVerificationRequest(BaseModel):
    email: EmailStr


class ResendVerificationResponse(BaseModel):
    message: str


# ─── Verificación ────────────────────────────────────────

class VerificationResponse(BaseModel):
    message: str
    api_key: str


# ─── API Keys ────────────────────────────────────────────

class ApiKeyResponse(BaseModel):
    api_key: str
    key_prefix: str
    message: str


class RevokeResponse(BaseModel):
    message: str


class DeleteAccountResponse(BaseModel):
    message: str


# ─── Perfil de desarrollador ─────────────────────────────

class DeveloperProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: str
    organization: str | None = None
    status: str
    created_at: datetime.datetime
    api_key_prefix: str | None = None
    api_key_created_at: datetime.datetime | None = None

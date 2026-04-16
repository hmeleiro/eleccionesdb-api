"""
Rutas del panel de administración.

Prefijo : /admin
Seguridad: JWT Bearer (excluido de OpenAPI pública)
"""

import math
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse, HTMLResponse
from sqlalchemy.orm import Session

from app.auth.admin_crud import (
    delete_developer,
    get_admin_by_email,
    get_developer_audit_log,
    get_developer_detail,
    list_developers,
    revoke_all_keys,
    update_developer_status,
)
from app.auth.admin_dependencies import get_current_admin
from app.auth.admin_schemas import (
    AdminLoginRequest,
    AdminTokenResponse,
    AuditLogEntry,
    DeveloperDetail,
    DeveloperListItem,
    DeveloperListResponse,
    StatusUpdateRequest,
    ApiKeyInfo,
)
from app.auth.admin_service import create_access_token, verify_password
from app.auth.database import get_auth_db

router = APIRouter(prefix="/admin", tags=["admin"], include_in_schema=False)

_STATIC_DIR = None  # se configura desde main.py


def _admin_html_path() -> str:
    import pathlib
    return str(pathlib.Path(__file__).parent.parent / "static" / "admin.html")


# ── UI ───────────────────────────────────────────────────

@router.get("/", include_in_schema=False)
def admin_ui():
    return FileResponse(_admin_html_path(), media_type="text/html")


# ── Auth ─────────────────────────────────────────────────

@router.post("/api/login", response_model=AdminTokenResponse, include_in_schema=False)
def admin_login(body: AdminLoginRequest, db: Session = Depends(get_auth_db)):
    admin = get_admin_by_email(db, body.email)
    if admin is None or not verify_password(body.password, admin.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )
    token = create_access_token(admin.id, admin.email)
    return AdminTokenResponse(access_token=token)


# ── Desarrolladores ───────────────────────────────────────

@router.get("/api/developers", response_model=DeveloperListResponse, include_in_schema=False)
def admin_list_developers(
    status_filter: Optional[str] = Query(None, alias="status"),
    email: Optional[str] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(25, ge=1, le=100),
    db: Session = Depends(get_auth_db),
    _admin: dict = Depends(get_current_admin),
):
    items, total = list_developers(
        db,
        status=status_filter,
        email_search=email,
        date_from=date_from,
        date_to=date_to,
        page=page,
        per_page=per_page,
    )
    pages = math.ceil(total / per_page) if per_page else 1
    return DeveloperListResponse(
        items=[DeveloperListItem.model_validate(d) for d in items],
        total=total,
        page=page,
        per_page=per_page,
        pages=pages,
    )


@router.get("/api/developers/{developer_id}", response_model=DeveloperDetail, include_in_schema=False)
def admin_get_developer(
    developer_id: int,
    db: Session = Depends(get_auth_db),
    _admin: dict = Depends(get_current_admin),
):
    dev = get_developer_detail(db, developer_id)
    if dev is None:
        raise HTTPException(status_code=404, detail="Desarrollador no encontrado")

    audit = get_developer_audit_log(db, developer_id)
    return DeveloperDetail(
        id=dev.id,
        email=dev.email,
        name=dev.name,
        organization=dev.organization,
        intended_use=dev.intended_use,
        status=dev.status,
        email_verified=dev.email_verified,
        created_at=dev.created_at,
        updated_at=dev.updated_at,
        api_keys=[ApiKeyInfo.model_validate(k) for k in dev.api_keys],
        audit_log=[AuditLogEntry.model_validate(e) for e in audit],
    )


@router.patch("/api/developers/{developer_id}/status", response_model=DeveloperListItem, include_in_schema=False)
def admin_update_status(
    developer_id: int,
    body: StatusUpdateRequest,
    db: Session = Depends(get_auth_db),
    _admin: dict = Depends(get_current_admin),
):
    allowed = {"active", "suspended", "pending"}
    if body.status not in allowed:
        raise HTTPException(status_code=422, detail=f"Estado inválido. Valores permitidos: {allowed}")
    dev = update_developer_status(db, developer_id, body.status)
    if dev is None:
        raise HTTPException(status_code=404, detail="Desarrollador no encontrado")
    return DeveloperListItem.model_validate(dev)


@router.post("/api/developers/{developer_id}/api-keys/revoke", include_in_schema=False)
def admin_revoke_keys(
    developer_id: int,
    db: Session = Depends(get_auth_db),
    _admin: dict = Depends(get_current_admin),
):
    dev = get_developer_detail(db, developer_id)
    if dev is None:
        raise HTTPException(status_code=404, detail="Desarrollador no encontrado")
    count = revoke_all_keys(db, developer_id)
    return {"revoked": count}


@router.delete("/api/developers/{developer_id}", include_in_schema=False)
def admin_delete_developer(
    developer_id: int,
    db: Session = Depends(get_auth_db),
    _admin: dict = Depends(get_current_admin),
):
    ok = delete_developer(db, developer_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Desarrollador no encontrado")
    return {"deleted": True}

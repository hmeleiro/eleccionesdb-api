# Auditoría de privacidad y cumplimiento RGPD/LOPDGDD

**Proyecto:** EleccionesDB API
**Fecha de auditoría:** 17 de abril de 2026
**Alcance:** Revisión técnica y legal del tratamiento de datos personales

---

## 1. Estado actual detectado

### Stack técnico
- **Backend:** FastAPI (Python 3.12), SQLAlchemy, uvicorn
- **BD electoral:** PostgreSQL (solo lectura, datos públicos electorales)
- **BD auth:** SQLite (cuentas de desarrollador, API keys, audit log)
- **Email transaccional:** Resend (nodo Irlanda, UE)
- **Hosting:** IONOS Cloud S.L.U. (EEE)
- **Frontend docs:** Hugo (sitio estático en GitHub Pages)
- **Despliegue:** Docker (contenedor único + volumen para SQLite)

### Datos personales tratados

| Dato | Recogido en | Almacenado en | Obligatorio |
|------|-------------|---------------|-------------|
| Email | Registro | `developer_accounts.email` | Sí |
| Organización | Registro | `developer_accounts.organization` | No |
| Uso previsto | Registro | `developer_accounts.intended_use` | No |
| Aceptación de privacidad | Registro | `developer_accounts.privacy_accepted_at` | Sí |
| Consentimiento marketing | Registro | `developer_accounts.marketing_consent` + `marketing_consent_at` | No |
| IP del cliente | Registro, verificación, rotación, revocación | `audit_log.ip_address` | Automático |
| Prefijo de API key | Generación de clave | `api_keys.key_prefix` | Automático |
| Hash de API key | Generación de clave | `api_keys.key_hash` (SHA-256) | Automático |
| Timestamps de uso | Autenticación | `api_keys.last_used_at` | Automático |

### Medidas de seguridad existentes (pre-auditoría)

| Medida | Estado |
|--------|--------|
| API keys: `secrets.token_urlsafe(32)` + SHA-256 hash | ✅ Implementado |
| Clave completa mostrada solo una vez | ✅ Implementado |
| Prefijo visible para trazabilidad | ✅ Implementado |
| Rotación con periodo de gracia (1h) | ✅ Implementado |
| Revocación inmediata | ✅ Implementado |
| Rate limiting en registro (5/IP, 3/email por hora) | ✅ Implementado |
| Admin: PBKDF2-HMAC-SHA256 (600k iteraciones) | ✅ Implementado |
| Admin: JWT con expiración configurable | ✅ Implementado |
| Comparación en tiempo constante (`hmac.compare_digest`) | ✅ Implementado |
| Anti-enumeración en recover/resend | ✅ Implementado |
| Audit log con tipo de evento, IP, detalles | ✅ Implementado |
| CORS con orígenes explícitos | ✅ Implementado |
| Restricción de origen en endpoints sensibles | ✅ Implementado |
| XSS: `textContent` en frontend, `escHtml()` en admin | ✅ Implementado |
| API key nunca en logs | ✅ Implementado |
| sessionStorage (no localStorage) para API key en cliente | ✅ Implementado |

---

## 2. Riesgos encontrados y medidas aplicadas

### Riesgos corregidos en esta auditoría

| Riesgo | Severidad | Medida aplicada |
|--------|-----------|-----------------|
| **No se recogía consentimiento de privacidad** | Alta | Campos `privacy_accepted_at`, `marketing_consent`, `marketing_consent_at` en modelo. Validación en backend (422 si no se acepta). Checkboxes en formulario de registro. |
| **Política de privacidad existía pero no estaba publicada** | Alta | Página `/privacidad/` en Hugo. Enlace en footer de todas las páginas. Cláusula informativa en formulario de registro. |
| **No existía derecho de supresión self-service** | Alta | `DELETE /v1/developers/me` — anonimiza cuenta, revoca todas las keys. |
| **No existía derecho de portabilidad self-service** | Media | `GET /v1/developers/me/data-export` — exporta todos los datos en JSON. |
| **Emails en claro en logs** | Media | Función `_mask_email()` enmascara emails en todos los logs (`h***@domain.com`). |
| **Sin cabeceras de seguridad HTTP** | Media | Middleware que añade `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`, `Permissions-Policy`. |
| **`ADMIN_JWT_SECRET` con valor por defecto sin advertencia** | Media | Warning en startup si `ADMIN_JWT_SECRET == "change-me-in-production"` y `APP_ENV != "development"`. |
| **Sin funciones de limpieza de datos** | Baja | `cleanup_expired_tokens()` y `cleanup_old_audit_logs()` para mantenimiento. |

### Riesgos aceptados / pendientes

| Riesgo | Severidad | Justificación / Acción recomendada |
|--------|-----------|-------------------------------------|
| **Sin CAPTCHA en registro** | Media | TODO ya presente en el código. Recomendado implementar (Turnstile, hCaptcha) como siguiente paso. |
| **Rate limiter in-memory** | Baja | Adecuado para despliegue single-process actual. Documentar limitación para escalado futuro. |
| **`X-Forwarded-For` sin validación** | Baja | Aceptable si el reverse proxy (IONOS/Nginx) es el único que establece el header. Documentar que el rate limiter depende de este header. |
| **HSTS no configurado en la aplicación** | Baja | Debe configurarse a nivel de reverse proxy/load balancer, no en la aplicación. |
| **Campo `name` — ¿es necesario?** | ~~Baja~~ | ~~Debatible desde el punto de vista de minimización.~~ **Resuelto: campo eliminado.** |
| **Campo `intended_use` — ¿debe ser obligatorio?** | Baja | Útil para prevención de abuso (interés legítimo). Actualmente opcional en el schema. Correcto. |
| **Sin DPIA formal** | Info | No es obligatorio para este tratamiento (pequeña escala, datos no sensibles, sin perfilado sistemático). Documentar esta decisión. |
| **Sin cookie banner** | Info | El sitio estático no usa cookies ni analytics. No es necesario banner. Si se añaden en el futuro, será necesario. |

---

## 3. Auditoría de cumplimiento RGPD/LOPDGDD

### 3.1 Datos personales tratados y base jurídica

| Dato | Finalidad | Base jurídica | Referencia RGPD |
|------|-----------|---------------|-----------------|
| Email | Gestión de cuenta, verificación, comunicación de seguridad | Ejecución contractual (Art. 6.1.b) | Necesario para prestar el servicio |

| Organización | Contexto del uso del servicio | Interés legítimo (Art. 6.1.f) | Opcional, proporcionado voluntariamente |
| Uso previsto | Prevención de abuso, contexto | Interés legítimo (Art. 6.1.f) | Opcional |
| Hash de API key | Autenticación | Ejecución contractual (Art. 6.1.b) | Dato pseudonimizado (hash irreversible) |
| Prefijo de API key | Trazabilidad y soporte | Interés legítimo (Art. 6.1.f) | Dato parcial, no permite acceso |
| IP del cliente | Seguridad, prevención de abuso, audit trail | Interés legítimo (Art. 6.1.f) | Proporcional al riesgo |
| Timestamps de uso | Seguridad, monitorización | Interés legítimo (Art. 6.1.f) | Mínimamente invasivo |
| Consentimiento marketing | Comunicaciones informativas | Consentimiento (Art. 6.1.a) | Libre, específico, informado, revocable |

### 3.2 Encargados del tratamiento

| Proveedor | Servicio | Ubicación datos | DPA |
|-----------|----------|-----------------|-----|
| **IONOS Cloud S.L.U.** | Hosting, infraestructura | EEE | ✅ DPA firmado (Art. 28 RGPD + Art. 33 LOPDGDD), ISO 27001, versión 1.2 (12/2023) |
| **Resend** | Email transaccional | Irlanda (UE) | ✅ DPA pre-firmado al registrarse |

### 3.3 Transferencias internacionales

**No hay transferencias internacionales.** Ambos proveedores procesan datos dentro del EEE.

### 3.4 Derechos de los interesados — Implementación

| Derecho | Implementación | Estado |
|---------|----------------|--------|
| **Acceso** (Art. 15) | `GET /v1/developers/me/data-export` + email de contacto | ✅ Implementado |
| **Rectificación** (Art. 16) | Vía email de contacto | ⚠️ Manual (proporcionado al volumen) |
| **Supresión** (Art. 17) | `DELETE /v1/developers/me` (anonimización) | ✅ Implementado |
| **Limitación** (Art. 18) | Vía email de contacto | ⚠️ Manual |
| **Portabilidad** (Art. 20) | `GET /v1/developers/me/data-export` (JSON) | ✅ Implementado |
| **Oposición** (Art. 21) | Vía email de contacto | ⚠️ Manual |

### 3.5 Documentación mínima recomendada

| Documento | Estado | Prioridad |
|-----------|--------|-----------|
| Política de privacidad pública | ✅ Implementada (`/privacidad/`) | Must have |
| Cláusula informativa en registro | ✅ Implementada | Must have |
| Registro de actividades de tratamiento (Art. 30 RGPD) | ❌ No existe | Must have (este informe puede servir como base) |
| DPA con IONOS | ✅ Firmado | Must have |
| DPA con Resend | ✅ Vigente | Must have |
| Procedimiento de respuesta a ejercicio de derechos | ❌ No formalizado | Nice to have (para un proyecto pequeño, el email de contacto es suficiente) |
| Evaluación de impacto (DPIA) | No aplicable | No requerida |

---

## 4. Política de conservación de datos

| Dato / categoría | Finalidad | Base jurídica | Plazo de conservación | Criterio de borrado / anonimización |
|------------------|-----------|---------------|----------------------|-------------------------------------|
| Email | Gestión de cuenta | Ejecución contractual | Mientras la cuenta esté activa + 30 días tras eliminación | Anonimización al ejercer derecho de supresión (`DELETE /me`) |
| Organización, uso previsto | Gestión del servicio | Interés legítimo | Mientras la cuenta esté activa | Eliminación al borrar la cuenta |
| Hash de API key | Autenticación | Ejecución contractual | Mientras la key esté activa o en periodo de gracia | Las keys revocadas se marcan como inactivas; se pueden purgar tras 30 días |
| Prefijo de API key | Trazabilidad / soporte | Interés legítimo | Mientras la cuenta esté activa | Anonimización al borrar la cuenta |
| Audit log (IP, eventos) | Seguridad, prevención de abuso | Interés legítimo | 12 meses desde el evento | Anonimización de IPs (`cleanup_old_audit_logs`); los registros sin IP se conservan como traza anónima |
| Tokens de verificación | Activación de cuenta | Ejecución contractual | Hasta uso o expiración (24h) | Eliminación (`cleanup_expired_tokens`) |
| Consentimiento marketing | Comunicaciones | Consentimiento | Hasta revocación por el usuario | Flag desactivado inmediatamente al revocar; timestamp conservado como evidencia |
| Credenciales admin | Control de acceso interno | Interés legítimo | Mientras el admin esté activo | Eliminación al desactivar la cuenta admin |
| Consentimiento de privacidad | Evidencia legal | Obligación legal | Mientras la cuenta exista + periodo de prescripción (3 años) | Se conserva como evidencia tras la anonimización |

**Nota sobre plazos:** Estos plazos son propuestas técnico-organizativas razonables, no plazos legales imperativos. Se recomienda revisión periódica y ajuste según necesidad.

---

## 5. Proveedores a revisar desde el punto de vista de privacidad

| Proveedor | Revisado | Acción |
|-----------|----------|--------|
| **IONOS Cloud S.L.U.** | ✅ | DPA firmado, ISO 27001, datos en EEE. Sin acción pendiente. |
| **Resend** | ✅ | DPA automático, nodo Irlanda. Sin acción pendiente. |
| **GitHub Pages** (docs site) | ⚠️ | El sitio estático está en GitHub Pages. No procesa datos personales del servicio (no hay formularios que envíen a GitHub). Revisar si GitHub recoge alguna telemetría del visitante. |

---

## 6. Archivos modificados

### Nuevos
| Archivo | Propósito |
|---------|-----------|
| `docs/content/privacidad.md` | Página de política de privacidad (Hugo) |
| `PRIVACY-AUDIT.md` | Este informe de auditoría |

### Modificados

| Archivo | Cambios |
|---------|---------|
| `app/auth/models.py` | Añadidos campos `privacy_accepted_at`, `marketing_consent`, `marketing_consent_at` a `DeveloperAccount` |
| `app/auth/schemas.py` | Añadidos `privacy_accepted` (bool, requerido), `marketing_consent` (bool, opcional) a `RegisterRequest`. Añadido `DeleteAccountResponse`. |
| `app/auth/crud.py` | `create_developer()` acepta campos de consentimiento. Nuevas funciones: `anonymize_developer()`, `get_developer_data_export()`, `cleanup_expired_tokens()`, `cleanup_old_audit_logs()`. |
| `app/auth/admin_schemas.py` | Añadidos `privacy_accepted_at`, `marketing_consent`, `marketing_consent_at` a `DeveloperDetail`. |
| `app/api/routes_auth.py` | Validación de `privacy_accepted == True` en registro. Paso de campos de consentimiento a CRUD. |
| `app/api/routes_developers.py` | Nuevos endpoints: `GET /me/data-export`, `DELETE /me`. |
| `app/services/email.py` | Método `_mask_email()` para enmascarar emails en logs. Aplicado a todos los `logger.info/warning/error`. |
| `app/main.py` | Middleware de cabeceras de seguridad. Warning de `ADMIN_JWT_SECRET` en startup. |
| `app/static/admin.html` | Campos de consentimiento en el detalle de desarrollador (privacidad, marketing con timestamps). |
| `docs/content/developers/register.md` | Cláusula informativa de privacidad. Checkbox obligatorio de aceptación. Checkbox opcional de marketing. |
| `docs/content/developers/account.md` | Nuevas tarjetas: "Exportar mis datos" y "Eliminar cuenta". |
| `docs/assets/js/api-client.js` | Envío de `privacy_accepted` y `marketing_consent` en registro. Validación client-side del checkbox de privacidad. Funciones de exportación de datos y eliminación de cuenta. |
| `docs/layouts/partials/footer.html` | Enlace a Política de privacidad en el pie de todas las páginas. |
| `tests/test_auth.py` | `privacy_accepted: True` en todos los registros de test. Override de `require_frontend_origin`. Fix de `_activate_and_get_key` (detached instance). 5 tests nuevos: privacidad rechazada, marketing consent, data export, delete account, security headers. |

---

## 7. Decisiones tomadas y justificación

| Decisión | Justificación |
|----------|---------------|
| **SHA-256 para API keys (sin cambio)** | Las keys tienen 256 bits de entropía (`secrets.token_urlsafe(32)`). Fuerza bruta inviable. bcrypt/scrypt no aporta mejora real aquí: los hashes lentos son necesarios para secretos de baja entropía (contraseñas), no para tokens aleatorios de alta entropía. |
| **Campo `name` eliminado (minimización)** | El email es suficiente para la gestión técnica. Eliminar el campo `name` reduce la superficie de datos personales tratados sin impacto funcional. |
| **Audit log: anonimizar IPs a 12 meses, no borrar entradas** | El tipo de evento y timestamp sin IP no es dato personal. Mantenerlo permite detectar patrones de abuso a largo plazo sin riesgo de privacidad. |
| **Anonimización en lugar de borrado físico** | Preserva la integridad referencial del audit log (interés legítimo de seguridad). Los datos identificativos se eliminan; queda un registro anónimo de eventos. |
| **Marketing: opt-in explícito con timestamp separado** | RGPD Art. 7 exige consentimiento demostrable. El timestamp de `marketing_consent_at` sirve como evidencia. |
| **No implementar expiración de API keys** | No es requisito legal. La revocación y rotación existentes son suficientes. Evita fricción innecesaria para los usuarios de un servicio con datos públicos. |
| **No implementar DPIA** | Tratamiento de pequeña escala, datos no sensibles, sin perfilado sistemático ni monitorización de personas. Art. 35 RGPD no aplica. |
| **Limpieza manual (no cron)** | Funciones `cleanup_*` disponibles para invocación manual o desde el panel admin. Un scheduler sería sobreingeniería para el volumen actual. |

---

## 8. Puntos pendientes de revisión humana

1. ~~**Rellenar placeholders** en la política de privacidad~~ — Completados con datos reales.
2. ~~**Decidir si mantener el campo `name`**~~ — Eliminado (minimización de datos).
3. **Revisar plazos de retención** con asesor legal si se considera necesario.
4. **GitHub Pages** — confirmar que no recoge datos personales de los visitantes del sitio de documentación. Si lo hace, valorar aviso de cookies.
5. **CAPTCHA** — implementar como siguiente paso para prevención de abuso en registro.
6. **Registro de actividades de tratamiento (Art. 30 RGPD)** — este informe puede servir como base, pero conviene formalizarlo en un documento separado si se requiere.

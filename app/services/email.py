"""
Servicio de email transaccional mediante Resend.

Usa la API HTTP de Resend (no SMTP). La interfaz es suficientemente limpia
para cambiar de proveedor reemplazando sólo este módulo.
"""

import logging

import httpx

from app.config import settings

logger = logging.getLogger("uvicorn.error")

RESEND_API_URL = "https://api.resend.com/emails"


class EmailService:
    """Cliente para enviar emails transaccionales vía Resend."""

    def __init__(self, api_key: str, from_email: str):
        self._api_key = api_key
        self._from_email = from_email

    def send_verification_email(
        self,
        to_email: str,
        developer_name: str,
        verification_url: str,
    ) -> bool:
        """Envía el email de verificación.

        Returns:
            True si el envío fue exitoso, False en caso de error.
        """
        if not self._api_key:
            logger.warning(
                "RESEND_API_KEY no configurada — email de verificación NO enviado a %s",
                to_email,
            )
            return False

        html_body = self._build_html(developer_name, verification_url)
        text_body = self._build_text(developer_name, verification_url)

        payload = {
            "from": self._from_email,
            "to": [to_email],
            "subject": "Verifica tu email — Elecciones DB API",
            "html": html_body,
            "text": text_body,
        }

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.post(
                    RESEND_API_URL,
                    json=payload,
                    headers={
                        "Authorization": f"Bearer {self._api_key}",
                        "Content-Type": "application/json",
                    },
                )
            if response.status_code in (200, 201):
                logger.info("Email de verificación enviado a %s", to_email)
                return True

            logger.error(
                "Error de Resend (%s): %s", response.status_code, response.text
            )
            return False

        except httpx.HTTPError as exc:
            logger.error("Error de red al enviar email a %s: %s", to_email, exc)
            return False

    def _build_html(self, name: str, url: str) -> str:
        return f"""\
<!DOCTYPE html>
<html lang='es'>
<head>
    <meta charset='utf-8'>
    <meta name='viewport' content='width=device-width, initial-scale=1'>
    <title>Verifica tu email — Spain Electoral Project</title>
    <style>
        body {{
            background: #fafbfc;
            font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            color: #1a1a2e;
            max-width: 560px;
            margin: 0 auto;
            padding: 40px 0;
            line-height: 1.6;
        }}
        .container {{
            background: #fff;
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.06);
            border: 1px solid #e5e7eb;
            padding: 2.5rem 2rem 2rem 2rem;
            margin: 0 auto;
        }}
        h1 {{ font-size: 2.25rem; margin-bottom: 0.5rem; font-weight: 700; line-height: 1.25; }}
        h2 {{ font-size: 1.25rem; color: #2d5bff; margin-bottom: 1.5rem; font-weight: 600; }}
        p {{ font-size: 1rem; color: #1a1a2e; margin: 0.5rem 0 1.25rem 0; }}
        .button {{
            display: inline-block;
            background: #2d5bff;
            color: #fff;
            font-weight: 600;
            font-size: 1rem;
            padding: 0.75rem 2rem;
            border-radius: 8px;
            text-decoration: none;
            box-shadow: 0 1px 2px rgba(45,91,255,0.08);
            margin: 1.5rem 0;
            transition: background 0.2s;
        }}
        .button:hover {{ background: #2563eb; }}
        .meta {{ color: #5a5a7a; font-size: 0.875rem; margin-top: 2rem; }}
        .footer {{ color: #9ca3af; font-size: 0.875rem; margin-top: 2.5rem; text-align: center; }}
    </style>
</head>
<body>
    <div class='container'>
        <h2>Spain Electoral Project</h2>
        <h1>Verifica tu email</h1>
        <p>Hola {name},</p>
        <p>Gracias por registrarte en la API de datos electorales de España.<br>
        Para activar tu cuenta y recibir tu API key, confirma tu dirección de email haciendo clic en el siguiente botón:</p>
        <a href='{url}' class='button'>Verificar email</a>
        <p class='meta'>Si no solicitaste este registro, puedes ignorar este mensaje.<br>El enlace expira en 24 horas.</p>
        <div class='footer'>Spain Electoral Project &mdash; API</div>
    </div>
</body>
</html>"""

    def _build_text(self, name: str, url: str) -> str:
        return (
            f"Hola {name},\n\n"
            f"Gracias por registrarte en Elecciones DB API.\n\n"
            f"Para verificar tu email y recibir tu API key, abre el siguiente enlace:\n\n"
            f"{url}\n\n"
            f"El enlace expira en 24 horas.\n\n"
            f"Si no solicitaste este registro, puedes ignorar este mensaje.\n\n"
            f"— Elecciones DB API"
        )


# ── Singleton inicializado desde settings ────────────────

email_service = EmailService(
    api_key=settings.RESEND_API_KEY,
    from_email=settings.RESEND_FROM_EMAIL,
)

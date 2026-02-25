"""
Módulo de emails transaccionales usando SendGrid.
Todos los emails tienen diseño branded de Hacienda La Carmelita.
"""

import os
from typing import Optional
from app.config import settings


# ─────────────────────────────────────────────────────────────
#  TEMPLATES HTML
# ─────────────────────────────────────────────────────────────

def _html_base(contenido: str, titulo: str = "Hacienda La Carmelita") -> str:
    """Template HTML base con branding de la hacienda."""
    return f"""
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{titulo}</title>
<style>
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f4f7f0; margin: 0; padding: 20px; }}
  .container {{ max-width: 600px; margin: 0 auto; background: white; border-radius: 16px; overflow: hidden; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
  .header {{ background: linear-gradient(135deg, #2D5016, #4a6d33); padding: 32px 40px; text-align: center; }}
  .header h1 {{ color: white; margin: 0; font-size: 22px; font-family: Georgia, serif; }}
  .header p {{ color: #a9c390; margin: 8px 0 0; font-size: 13px; }}
  .body {{ padding: 40px; }}
  .code-box {{ background: #f4f7f0; border: 2px solid #2D5016; border-radius: 12px; padding: 24px; text-align: center; margin: 24px 0; }}
  .code {{ font-size: 42px; font-weight: bold; color: #2D5016; letter-spacing: 8px; font-family: monospace; }}
  .code-label {{ font-size: 13px; color: #666; margin-top: 8px; }}
  .btn {{ display: inline-block; background: #2D5016; color: white; padding: 14px 32px; border-radius: 8px; text-decoration: none; font-weight: 600; margin: 16px 0; }}
  .footer {{ background: #f4f7f0; padding: 24px 40px; text-align: center; font-size: 12px; color: #888; }}
  .divider {{ height: 1px; background: #f0f0f0; margin: 24px 0; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>Hacienda La Carmelita</h1>
    <p>Lerida, Tolima &middot; Origen del Arroz Colombiano</p>
  </div>
  <div class="body">
    {contenido}
  </div>
  <div class="footer">
    <p>Este email fue enviado por Hacienda La Carmelita</p>
    <p>Lerida, Tolima, Colombia &middot; reservas@haciendalacarmelita.com</p>
  </div>
</div>
</body>
</html>
"""


def _html_otp(codigo: str, nombre: str = "") -> str:
    saludo = f"Hola {nombre}," if nombre else "Hola,"
    return _html_base(f"""
<p style="font-size:16px; color:#333;">{saludo}</p>
<p style="color:#555;">Tu código de verificación para completar tu reserva es:</p>
<div class="code-box">
  <div class="code">{codigo}</div>
  <div class="code-label">Válido por 10 minutos &middot; No lo compartas con nadie</div>
</div>
<p style="color:#888; font-size:13px;">Si no solicitaste este código, ignora este mensaje.</p>
<div class="divider"></div>
<p style="color:#888; font-size:12px;">¿Necesitas ayuda? Escríbenos por WhatsApp o a reservas@haciendalacarmelita.com</p>
""", titulo="Código de verificación · Hacienda La Carmelita")


def _html_confirmacion(codigo_reserva: str, nombre: str, checkin: str, checkout: str, noches: int, precio: str) -> str:
    return _html_base(f"""
<h2 style="color:#2D5016; font-family:Georgia,serif;">¡Reserva Confirmada!</h2>
<p style="color:#555;">Hola <strong>{nombre}</strong>, tu reserva en Hacienda La Carmelita ha sido confirmada.</p>
<div class="code-box">
  <div style="font-size:13px; color:#666; margin-bottom:8px;">Código de reserva</div>
  <div class="code" style="font-size:28px;">{codigo_reserva}</div>
</div>
<table style="width:100%; border-collapse:collapse; margin:24px 0;">
  <tr><td style="padding:8px 0; color:#666; font-size:14px;">Check-in:</td><td style="padding:8px 0; font-weight:600; font-size:14px;">{checkin}</td></tr>
  <tr><td style="padding:8px 0; color:#666; font-size:14px;">Check-out:</td><td style="padding:8px 0; font-weight:600; font-size:14px;">{checkout}</td></tr>
  <tr><td style="padding:8px 0; color:#666; font-size:14px;">Noches:</td><td style="padding:8px 0; font-weight:600; font-size:14px;">{noches}</td></tr>
  <tr><td style="padding:8px 0; color:#666; font-size:14px;">Total pagado:</td><td style="padding:8px 0; font-weight:600; color:#2D5016; font-size:14px;">{precio}</td></tr>
</table>
<a href="https://haciendalacarmelita.com/reservas/{codigo_reserva}" class="btn">Ver mi reserva</a>
<div class="divider"></div>
<p style="color:#888; font-size:13px;">Te enviaremos un recordatorio 48 horas antes de tu llegada con instrucciones detalladas.</p>
""", titulo=f"Reserva confirmada {codigo_reserva} · Hacienda La Carmelita")


def _html_recordatorio(nombre: str, checkin: str, codigo_reserva: str) -> str:
    return _html_base(f"""
<h2 style="color:#2D5016; font-family:Georgia,serif;">¡Nos vemos en 2 días!</h2>
<p style="color:#555;">Hola <strong>{nombre}</strong>, tu check-in en Hacienda La Carmelita es <strong>mañana</strong>.</p>
<div class="code-box">
  <p style="margin:0; font-size:15px; color:#2D5016; font-weight:600;">Check-in: {checkin}</p>
</div>
<h3 style="color:#333;">Cómo llegar</h3>
<p style="color:#555; font-size:14px;">
  Lerida, Tolima, Colombia.<br>
  Desde Ibagué: toma la vía hacia Honda por aproximadamente 45 minutos.<br>
  Coordenadas GPS: 4.8623, -74.9308
</p>
<a href="https://maps.google.com/?q=Lerida+Tolima+Colombia" class="btn">Abrir en Google Maps</a>
<div class="divider"></div>
<p style="color:#888; font-size:13px;">¿Tienes preguntas? Escríbenos por WhatsApp antes de tu llegada.</p>
<p style="color:#888; font-size:12px;">Reserva: {codigo_reserva}</p>
""", titulo="Recordatorio de llegada · Hacienda La Carmelita")


def _html_solicitud_resena(nombre: str, codigo_reserva: str) -> str:
    return _html_base(f"""
<h2 style="color:#2D5016; font-family:Georgia,serif;">¿Cómo fue tu estadía?</h2>
<p style="color:#555;">Hola <strong>{nombre}</strong>, esperamos que hayas disfrutado tu visita a Hacienda La Carmelita.</p>
<p style="color:#555;">Tu opinión nos ayuda a mejorar y a que otras familias descubran la hacienda.</p>
<a href="https://g.page/haciendalacarmelita/review" class="btn">Dejar reseña en Google</a>
<div class="divider"></div>
<p style="color:#888; font-size:13px;">Reserva: {codigo_reserva} · ¡Esperamos verte pronto!</p>
""", titulo="¿Cómo estuvo tu visita? · Hacienda La Carmelita")


# ─────────────────────────────────────────────────────────────
#  FUNCIONES DE ENVÍO
# ─────────────────────────────────────────────────────────────

async def _send_email(to: str, subject: str, html_content: str) -> bool:
    """
    Envía email vía SendGrid.
    Retorna True si se envió, False si hubo error.
    En development sin API key: imprime en consola.
    """
    if not settings.SENDGRID_API_KEY:
        # Modo desarrollo: simular envío
        print(f"\n{'='*60}")
        print(f"[EMAIL SIMULADO — desarrollo]")
        print(f"Para: {to}")
        print(f"Asunto: {subject}")
        print(f"{'='*60}\n")
        return True

    try:
        import sendgrid
        from sendgrid.helpers.mail import Mail, To, From, Subject, HtmlContent

        sg = sendgrid.SendGridAPIClient(api_key=settings.SENDGRID_API_KEY)
        message = Mail(
            from_email=(settings.SENDGRID_FROM_EMAIL, settings.SENDGRID_FROM_NAME),
            to_emails=to,
            subject=subject,
            html_content=html_content,
        )
        response = sg.client.mail.send.post(request_body=message.get())
        return response.status_code in (200, 202)
    except Exception as e:
        print(f"[SendGrid Error] {e}")
        return False


async def send_otp_email(destinatario: str, codigo: str, nombre: str = "") -> bool:
    """Envía email con código OTP de 6 dígitos."""
    return await _send_email(
        to=destinatario,
        subject="Tu código de verificación — Hacienda La Carmelita",
        html_content=_html_otp(codigo, nombre),
    )


async def send_confirmation_email(
    destinatario: str,
    nombre: str,
    codigo_reserva: str,
    checkin: str,
    checkout: str,
    noches: int,
    precio: str,
) -> bool:
    """Envía email de confirmación de reserva."""
    return await _send_email(
        to=destinatario,
        subject=f"Reserva confirmada {codigo_reserva} — Hacienda La Carmelita",
        html_content=_html_confirmacion(codigo_reserva, nombre, checkin, checkout, noches, precio),
    )


async def send_reminder_email(
    destinatario: str,
    nombre: str,
    checkin: str,
    codigo_reserva: str,
) -> bool:
    """Envía recordatorio 48h antes del check-in."""
    return await _send_email(
        to=destinatario,
        subject=f"Te esperamos mañana — Hacienda La Carmelita",
        html_content=_html_recordatorio(nombre, checkin, codigo_reserva),
    )


async def send_review_request_email(
    destinatario: str,
    nombre: str,
    codigo_reserva: str,
) -> bool:
    """Envía solicitud de reseña 24h después del check-out."""
    return await _send_email(
        to=destinatario,
        subject="¿Cómo estuvo tu visita? — Hacienda La Carmelita",
        html_content=_html_solicitud_resena(nombre, codigo_reserva),
    )

"""
Módulo de notificaciones SMS y WhatsApp usando Twilio.

IMPORTANTE: Los mensajes de WhatsApp Business deben usar templates
aprobados por Meta. Los templates de desarrollo usan el sandbox de Twilio.
"""

from app.config import settings


def _get_twilio_client():
    """Obtener cliente de Twilio. Retorna None si no hay credenciales."""
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        return None
    try:
        from twilio.rest import Client
        return Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    except ImportError:
        return None


# ─────────────────────────────────────────────────────────────
#  SMS
# ─────────────────────────────────────────────────────────────

async def send_sms_otp(telefono: str, mensaje: str) -> bool:
    """Envía OTP por SMS usando Twilio."""
    client = _get_twilio_client()
    if not client:
        print(f"\n[SMS SIMULADO — desarrollo]\nPara: {telefono}\n{mensaje}\n")
        return True
    try:
        message = client.messages.create(
            body=mensaje,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=telefono,
        )
        return message.status not in ("failed", "undelivered")
    except Exception as e:
        print(f"[Twilio SMS Error] {e}")
        return False


# ─────────────────────────────────────────────────────────────
#  WHATSAPP
# ─────────────────────────────────────────────────────────────

async def send_whatsapp_otp(telefono: str, codigo: str) -> bool:
    """
    Envía OTP por WhatsApp Business.
    En sandbox de Twilio: usa el número de sandbox y template libre.
    En producción: requiere template aprobado por Meta.
    """
    client = _get_twilio_client()
    mensaje = (
        f"*Hacienda La Carmelita*\n\n"
        f"Tu código de verificación es:\n\n"
        f"*{codigo}*\n\n"
        f"Válido por 10 minutos. No lo compartas.\n\n"
        f"¿Necesitas ayuda? Responde este mensaje."
    )
    if not client:
        print(f"\n[WHATSAPP SIMULADO — desarrollo]\nPara: whatsapp:{telefono}\n{mensaje}\n")
        return True
    try:
        message = client.messages.create(
            body=mensaje,
            from_=settings.TWILIO_WHATSAPP_NUMBER,
            to=f"whatsapp:{telefono}",
        )
        return message.status not in ("failed", "undelivered")
    except Exception as e:
        print(f"[Twilio WhatsApp Error] {e}")
        return False


async def notify_new_booking_admin(
    codigo_reserva: str,
    nombre_huesped: str,
    checkin: str,
    checkout: str,
    huespedes: int,
    precio: str,
) -> bool:
    """Notifica al admin/mayordomo cuando llega una nueva reserva confirmada."""
    client = _get_twilio_client()
    mensaje = (
        f"*Nueva reserva confirmada*\n\n"
        f"Código: *{codigo_reserva}*\n"
        f"Huésped: {nombre_huesped}\n"
        f"Check-in: {checkin}\n"
        f"Check-out: {checkout}\n"
        f"Huéspedes: {huespedes}\n"
        f"Total: {precio}\n\n"
        f"Ver detalle en el panel admin."
    )
    if not client:
        print(f"\n[WHATSAPP ADMIN SIMULADO]\n{mensaje}\n")
        return True
    try:
        client.messages.create(
            body=mensaje,
            from_=settings.TWILIO_WHATSAPP_NUMBER,
            to=f"whatsapp:{settings.ADMIN_WHATSAPP}",
        )
        return True
    except Exception as e:
        print(f"[Twilio Admin Notify Error] {e}")
        return False


async def send_welcome_guest(
    telefono: str,
    nombre: str,
    codigo_reserva: str,
    checkin: str,
) -> bool:
    """Envía bienvenida al huésped con detalles de la reserva."""
    client = _get_twilio_client()
    mensaje = (
        f"¡Hola {nombre}!\n\n"
        f"Tu reserva en *Hacienda La Carmelita* está confirmada.\n\n"
        f"*{codigo_reserva}*\n"
        f"Check-in: {checkin}\n\n"
        f"Te enviaremos las instrucciones de llegada 48 horas antes.\n\n"
        f"¿Preguntas? Escríbenos aquí."
    )
    if not client:
        print(f"\n[WHATSAPP BIENVENIDA SIMULADO]\nPara: {telefono}\n{mensaje}\n")
        return True
    try:
        client.messages.create(
            body=mensaje,
            from_=settings.TWILIO_WHATSAPP_NUMBER,
            to=f"whatsapp:{telefono}",
        )
        return True
    except Exception as e:
        print(f"[Twilio Welcome Error] {e}")
        return False


async def send_checkin_reminder(
    telefono: str,
    nombre: str,
    checkin: str,
    codigo_reserva: str,
) -> bool:
    """Envía recordatorio 48h antes del check-in."""
    client = _get_twilio_client()
    mensaje = (
        f"¡Hola {nombre}! Te esperamos en *Hacienda La Carmelita*\n\n"
        f"Tu check-in es *{checkin}*.\n\n"
        f"Lerida, Tolima, Colombia\n"
        f"GPS: 4.8623, -74.9308\n\n"
        f"¿Necesitas indicaciones? Responde este mensaje."
    )
    if not client:
        print(f"\n[WHATSAPP RECORDATORIO SIMULADO]\nPara: {telefono}\n{mensaje}\n")
        return True
    try:
        client.messages.create(
            body=mensaje,
            from_=settings.TWILIO_WHATSAPP_NUMBER,
            to=f"whatsapp:{telefono}",
        )
        return True
    except Exception as e:
        print(f"[Twilio Reminder Error] {e}")
        return False


async def send_review_request(
    telefono: str,
    nombre: str,
    codigo_reserva: str,
) -> bool:
    """Envía solicitud de reseña 24h después del check-out."""
    client = _get_twilio_client()
    mensaje = (
        f"¡Hola {nombre}! Esperamos que hayas disfrutado Hacienda La Carmelita\n\n"
        f"¿Podrías dejarnos una reseña en Google? Nos ayuda mucho:\n"
        f"https://g.page/haciendalacarmelita/review\n\n"
        f"¡Hasta pronto!"
    )
    if not client:
        print(f"\n[WHATSAPP RESENA SIMULADO]\nPara: {telefono}\n{mensaje}\n")
        return True
    try:
        client.messages.create(
            body=mensaje,
            from_=settings.TWILIO_WHATSAPP_NUMBER,
            to=f"whatsapp:{telefono}",
        )
        return True
    except Exception as e:
        print(f"[Twilio Review Error] {e}")
        return False

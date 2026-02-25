import asyncio
import logging
import uuid

from workers.celery_app import celery_app
from app.database import _get_sync_engine
from sqlmodel import Session, select
from app.models.reserva import Reserva
from app.models.usuario import Usuario
from app.notificaciones.email import (
    send_confirmation_email,
    send_reminder_email,
    send_review_request_email,
)

logger = logging.getLogger(__name__)


@celery_app.task(name="notificaciones.enviar_email_confirmacion")
def enviar_email_confirmacion(reserva_id: str):
    """Envía email de confirmación de reserva al huésped."""
    try:
        engine = _get_sync_engine()
        with Session(engine) as db:
            reserva = db.get(Reserva, uuid.UUID(reserva_id))
            if not reserva:
                logger.error(f"Reserva {reserva_id} no encontrada")
                return False

            usuario = db.get(Usuario, reserva.usuario_id) if reserva.usuario_id else None
            if not usuario:
                logger.warning(f"Usuario no encontrado para reserva {reserva_id}")
                return False

            nombre = f"{usuario.nombre} {usuario.apellido}".strip()
            precio_str = f"COP {int(reserva.precio_total_cop):,}".replace(",", ".")

            resultado = asyncio.run(send_confirmation_email(
                destinatario=usuario.email,
                nombre=nombre,
                codigo_reserva=reserva.codigo,
                checkin=reserva.fecha_checkin.strftime("%d %b %Y"),
                checkout=reserva.fecha_checkout.strftime("%d %b %Y"),
                noches=reserva.noches,
                precio=precio_str,
            ))
            logger.info(f"Email confirmación {'enviado' if resultado else 'falló'}: {usuario.email}")
            return resultado
    except Exception as e:
        logger.error(f"Error enviando email confirmación {reserva_id}: {e}")
        return False


@celery_app.task(name="notificaciones.enviar_recordatorio_48h")
def enviar_recordatorio_48h(reserva_id: str):
    """Envía recordatorio 48h antes del check-in."""
    try:
        engine = _get_sync_engine()
        with Session(engine) as db:
            reserva = db.get(Reserva, uuid.UUID(reserva_id))
            if not reserva:
                logger.error(f"Reserva {reserva_id} no encontrada")
                return False

            usuario = db.get(Usuario, reserva.usuario_id) if reserva.usuario_id else None
            if not usuario:
                logger.warning(f"Usuario no encontrado para reserva {reserva_id}")
                return False

            nombre = f"{usuario.nombre} {usuario.apellido}".strip()

            resultado = asyncio.run(send_reminder_email(
                destinatario=usuario.email,
                nombre=nombre,
                checkin=reserva.fecha_checkin.strftime("%d de %B de %Y"),
                codigo_reserva=reserva.codigo,
            ))
            logger.info(f"Recordatorio 48h {'enviado' if resultado else 'falló'}: {usuario.email}")
            return resultado
    except Exception as e:
        logger.error(f"Error recordatorio {reserva_id}: {e}")
        return False


@celery_app.task(name="notificaciones.enviar_solicitud_resena")
def enviar_solicitud_resena(reserva_id: str):
    """Envía solicitud de reseña 24h después del checkout."""
    try:
        engine = _get_sync_engine()
        with Session(engine) as db:
            reserva = db.get(Reserva, uuid.UUID(reserva_id))
            if not reserva:
                logger.error(f"Reserva {reserva_id} no encontrada")
                return False

            usuario = db.get(Usuario, reserva.usuario_id) if reserva.usuario_id else None
            if not usuario:
                logger.warning(f"Usuario no encontrado para reserva {reserva_id}")
                return False

            nombre = f"{usuario.nombre} {usuario.apellido}".strip()

            resultado = asyncio.run(send_review_request_email(
                destinatario=usuario.email,
                nombre=nombre,
                codigo_reserva=reserva.codigo,
            ))
            logger.info(f"Solicitud reseña {'enviada' if resultado else 'falló'}: {usuario.email}")
            return resultado
    except Exception as e:
        logger.error(f"Error solicitud reseña {reserva_id}: {e}")
        return False

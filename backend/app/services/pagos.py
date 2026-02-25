"""
Servicio de pagos — Wompi (Colombia) + Stripe (Internacional)
Sprint 3 — Hacienda La Carmelita
"""
from __future__ import annotations

import hashlib
import hmac
import json
import uuid
from decimal import Decimal
from typing import Optional

from sqlmodel import Session, select

from app.config import settings
from app.models.pago import Pago
from app.models.reserva import Reserva
import logging

logger = logging.getLogger(__name__)

# ── Wompi ─────────────────────────────────────────────────────────────────────

WOMPI_BASE = (
    "https://sandbox.wompi.co/v1"
    if settings.WOMPI_SANDBOX
    else "https://production.wompi.co/v1"
)


def _wompi_integrity_key() -> str:
    """
    Retorna la clave de integridad de Wompi.
    Usa WOMPI_INTEGRITY_KEY si está definida, con fallback a WOMPI_EVENTS_SECRET.
    """
    return settings.WOMPI_INTEGRITY_KEY or settings.WOMPI_EVENTS_SECRET


def generar_firma_integridad_wompi(
    referencia: str, monto_centavos: int, moneda: str
) -> str:
    """SHA256(referencia + monto_centavos + moneda + integrity_key)"""
    clave = _wompi_integrity_key()
    cadena = f"{referencia}{monto_centavos}{moneda}{clave}"
    return hashlib.sha256(cadena.encode()).hexdigest()


def crear_url_checkout_wompi(
    referencia: str,
    monto_cop: Decimal,
    email_cliente: str,
    nombre_cliente: str,
) -> dict:
    """
    Genera la URL del checkout de Wompi (widget de pago).
    Wompi usa un iframe/redirect a: https://checkout.wompi.co/p/
    Retorna la URL y los datos del checkout.
    """
    monto_centavos = int(monto_cop * 100)  # Wompi trabaja en centavos
    firma = generar_firma_integridad_wompi(referencia, monto_centavos, "COP")
    return_url = f"{settings.FRONTEND_URL}/reservar/confirmacion"

    checkout_url = (
        f"https://checkout.wompi.co/p/"
        f"?public-key={settings.WOMPI_PUBLIC_KEY}"
        f"&currency=COP"
        f"&amount-in-cents={monto_centavos}"
        f"&reference={referencia}"
        f"&signature:integrity={firma}"
        f"&redirect-url={return_url}"
        f"&customer-data:email={email_cliente}"
        f"&customer-data:full-name={nombre_cliente}"
    )
    return {
        "checkout_url": checkout_url,
        "referencia": referencia,
        "monto_centavos": monto_centavos,
        "firma_integridad": firma,
    }


def verificar_firma_webhook_wompi(
    payload_raw: bytes,
    timestamp: str,
    checksum_recibido: str,
) -> bool:
    """
    Verifica la firma HMAC del webhook de Wompi.
    Wompi firma con: SHA256(timestamp + payload_json + integrity_key)
    """
    try:
        clave = _wompi_integrity_key()
        cadena = timestamp + payload_raw.decode("utf-8") + clave
        checksum_calculado = hashlib.sha256(cadena.encode()).hexdigest()
        return hmac.compare_digest(checksum_calculado, checksum_recibido)
    except Exception:
        return False


def procesar_evento_wompi(evento: dict, db: Session) -> dict:
    """
    Procesa un evento de webhook de Wompi.
    Evento más común: 'transaction.updated' con status APPROVED/DECLINED/VOIDED
    """
    tipo = evento.get("event", "")
    if tipo != "transaction.updated":
        logger.info(f"Wompi evento ignorado: {tipo}")
        return {"procesado": False, "razon": f"evento ignorado: {tipo}"}

    data = evento.get("data", {}).get("transaction", {})
    referencia = data.get("reference", "")
    status_wompi = data.get("status", "")
    wompi_id = data.get("id", "")

    # Buscar el pago por referencia (la referencia es el código de reserva)
    # Recorremos los pagos de tipo wompi y buscamos por metadatos
    pagos_wompi = db.exec(
        select(Pago).where(Pago.pasarela == "wompi")
    ).all()

    pago = None
    for p in pagos_wompi:
        meta = p.metadatos or {}
        if meta.get("referencia") == referencia:
            pago = p
            break

    if not pago:
        logger.warning(
            f"Wompi webhook: pago no encontrado para referencia {referencia}"
        )
        return {"procesado": False, "razon": "pago no encontrado"}

    pago.pasarela_pago_id = wompi_id
    if status_wompi == "APPROVED":
        pago.estado = "aprobado"
        pago.metodo = data.get("payment_method_type", "")
        _confirmar_reserva_post_pago(pago.reserva_id, db)
    elif status_wompi in ("DECLINED", "VOIDED", "ERROR"):
        pago.estado = "rechazado"

    db.add(pago)
    db.commit()
    return {"procesado": True, "estado": pago.estado}


# ── Stripe ─────────────────────────────────────────────────────────────────────

def crear_payment_intent_stripe(
    reserva_id: uuid.UUID,
    monto_cop: Decimal,
    email_cliente: str,
    db: Session,
) -> dict:
    """
    Crea un PaymentIntent en Stripe y guarda el Pago en DB.
    Retorna el client_secret para usar con Stripe.js en el frontend.
    """
    import stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY

    monto_centavos = int(monto_cop * 100)
    try:
        intent = stripe.PaymentIntent.create(
            amount=monto_centavos,
            currency="cop",
            metadata={"reserva_id": str(reserva_id)},
            receipt_email=email_cliente,
            automatic_payment_methods={"enabled": True},
        )
        pago = Pago(
            reserva_id=reserva_id,
            pasarela="stripe",
            pasarela_pago_id=intent["id"],
            monto=monto_cop,
            moneda="COP",
            estado="pendiente",
            metadatos={"client_secret": intent["client_secret"]},
        )
        db.add(pago)
        db.commit()
        db.refresh(pago)
        return {
            "pago_id": str(pago.id),
            "client_secret": intent["client_secret"],
            "publishable_key": settings.STRIPE_PUBLISHABLE_KEY,
        }
    except Exception as e:
        logger.error(f"Stripe error: {e}")
        raise


def verificar_firma_webhook_stripe(payload_raw: bytes, sig_header: str) -> dict:
    """
    Verifica la firma del webhook de Stripe y retorna el evento.
    Lanza ValueError si la firma no es válida.
    """
    import stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        evento = stripe.Webhook.construct_event(
            payload_raw, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
        return evento
    except stripe.error.SignatureVerificationError as e:
        raise ValueError(f"Firma Stripe inválida: {e}")


def procesar_evento_stripe(evento: dict, db: Session) -> dict:
    """Procesa un evento de Stripe webhook."""
    tipo = evento.get("type", "")
    if tipo == "payment_intent.succeeded":
        intent = evento["data"]["object"]
        stripe_id = intent.get("id", "")

        pago = db.exec(
            select(Pago).where(
                Pago.pasarela == "stripe",
                Pago.pasarela_pago_id == stripe_id,
            )
        ).first()
        if pago:
            pago.estado = "aprobado"
            db.add(pago)
            _confirmar_reserva_post_pago(pago.reserva_id, db)
            db.commit()
            return {"procesado": True, "estado": "aprobado"}

    elif tipo == "payment_intent.payment_failed":
        intent = evento["data"]["object"]
        stripe_id = intent.get("id", "")
        pago = db.exec(
            select(Pago).where(
                Pago.pasarela == "stripe",
                Pago.pasarela_pago_id == stripe_id,
            )
        ).first()
        if pago:
            pago.estado = "rechazado"
            db.add(pago)
            db.commit()
            return {"procesado": True, "estado": "rechazado"}

    return {"procesado": False, "razon": f"evento ignorado: {tipo}"}


# ── Utilidades internas ────────────────────────────────────────────────────────

def _confirmar_reserva_post_pago(reserva_id: uuid.UUID, db: Session) -> None:
    """
    Transiciona la reserva de pago_pendiente → confirmada.
    Dispara la tarea Celery de email de confirmación.
    """
    from app.services.reservas import transicionar_estado_por_id
    try:
        transicionar_estado_por_id(reserva_id, "confirmada", db)
        logger.info(f"Reserva {reserva_id} confirmada tras pago exitoso")
        # Disparar email de confirmación (Celery)
        try:
            from workers.tasks.notificaciones import enviar_email_confirmacion
            enviar_email_confirmacion.delay(str(reserva_id))
        except Exception as e:
            logger.warning(f"No se pudo encolar email de confirmación: {e}")
    except Exception as e:
        logger.error(f"Error confirmando reserva {reserva_id}: {e}")
        raise


def obtener_estado_pago(pago_id: uuid.UUID, db: Session) -> Pago:
    """Retorna el pago por ID o lanza 404."""
    from fastapi import HTTPException
    pago = db.get(Pago, pago_id)
    if not pago:
        raise HTTPException(status_code=404, detail="Pago no encontrado")
    return pago

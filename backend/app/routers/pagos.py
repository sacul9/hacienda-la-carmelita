"""
Router de pagos — Wompi (Colombia) + Stripe (Internacional)
Sprint 3 — Hacienda La Carmelita
"""
from __future__ import annotations

import json
import uuid
from decimal import Decimal
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Request, Header
from pydantic import BaseModel
from sqlmodel import Session, select

from app.database import get_sync_db
from app.auth.dependencies import get_otp_token_payload, require_admin
from app.models.pago import Pago
from app.models.reserva import Reserva
from app.models.usuario import Usuario
from app.services import pagos as svc_pagos

router = APIRouter()


class IniciarPagoWompiRequest(BaseModel):
    reserva_id: str


class IniciarPagoStripeRequest(BaseModel):
    reserva_id: str


def _obtener_datos_huesped(reserva: Reserva, db: Session) -> tuple[str, str]:
    """
    Retorna (nombre_completo, email) del huésped asociado a la reserva.
    Busca en la tabla usuarios via reserva.usuario_id.
    """
    if reserva.usuario_id:
        usuario = db.get(Usuario, reserva.usuario_id)
        if usuario:
            nombre = f"{usuario.nombre} {usuario.apellido}".strip()
            return nombre, usuario.email
    # Fallback a metadatos si el usuario no está disponible
    meta = reserva.metadatos or {}
    nombre = meta.get("huesped_nombre", "Huésped")
    email = meta.get("huesped_email", "")
    return nombre, email


@router.post("/wompi/iniciar", status_code=201)
def wompi_iniciar(
    data: IniciarPagoWompiRequest,
    otp_payload: dict = Depends(get_otp_token_payload),
    db: Session = Depends(get_sync_db),
):
    """
    Inicia una transacción Wompi para la reserva.
    Requiere token OTP válido. Retorna la URL de checkout de Wompi.
    """
    try:
        reserva_id = uuid.UUID(data.reserva_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="reserva_id inválido")

    reserva = db.get(Reserva, reserva_id)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    if reserva.estado != "pago_pendiente":
        raise HTTPException(
            status_code=409,
            detail=(
                f"La reserva no está en estado pago_pendiente "
                f"(estado actual: {reserva.estado})"
            ),
        )

    if not reserva.precio_total_cop:
        raise HTTPException(
            status_code=422, detail="La reserva no tiene precio calculado"
        )

    # Crear registro de pago en DB
    pago = Pago(
        reserva_id=reserva_id,
        pasarela="wompi",
        monto=reserva.precio_total_cop,
        moneda="COP",
        estado="pendiente",
        metadatos={"referencia": reserva.codigo},
    )
    db.add(pago)
    db.commit()
    db.refresh(pago)

    # Obtener datos del huésped
    nombre_huesped, email_huesped = _obtener_datos_huesped(reserva, db)

    # Generar URL de checkout Wompi
    checkout = svc_pagos.crear_url_checkout_wompi(
        referencia=reserva.codigo,
        monto_cop=reserva.precio_total_cop,
        email_cliente=email_huesped,
        nombre_cliente=nombre_huesped,
    )

    return {
        "pago_id": str(pago.id),
        "pasarela": "wompi",
        "checkout_url": checkout["checkout_url"],
        "referencia": checkout["referencia"],
        "monto_cop": float(reserva.precio_total_cop),
    }


@router.post("/wompi/webhook")
async def wompi_webhook(
    request: Request,
    x_event_signature_timestamp: Optional[str] = Header(None),
    x_event_signature_checksum: Optional[str] = Header(None),
    db: Session = Depends(get_sync_db),
):
    """
    Webhook Wompi. Verifica firma HMAC antes de procesar.
    """
    payload_raw = await request.body()

    if not x_event_signature_timestamp or not x_event_signature_checksum:
        raise HTTPException(
            status_code=400, detail="Faltan headers de firma Wompi"
        )

    if not svc_pagos.verificar_firma_webhook_wompi(
        payload_raw, x_event_signature_timestamp, x_event_signature_checksum
    ):
        raise HTTPException(status_code=400, detail="Firma Wompi inválida")

    evento = json.loads(payload_raw)
    resultado = svc_pagos.procesar_evento_wompi(evento, db)
    return {"ok": True, **resultado}


@router.post("/stripe/intent", status_code=201)
def stripe_intent(
    data: IniciarPagoStripeRequest,
    otp_payload: dict = Depends(get_otp_token_payload),
    db: Session = Depends(get_sync_db),
):
    """
    Crea un PaymentIntent de Stripe para la reserva.
    Requiere token OTP válido.
    """
    try:
        reserva_id = uuid.UUID(data.reserva_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="reserva_id inválido")

    reserva = db.get(Reserva, reserva_id)
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")

    if reserva.estado != "pago_pendiente":
        raise HTTPException(
            status_code=409,
            detail="La reserva no está en estado pago_pendiente",
        )

    if not reserva.precio_total_cop:
        raise HTTPException(
            status_code=422, detail="La reserva no tiene precio calculado"
        )

    nombre_huesped, email_huesped = _obtener_datos_huesped(reserva, db)

    try:
        result = svc_pagos.crear_payment_intent_stripe(
            reserva_id=reserva_id,
            monto_cop=reserva.precio_total_cop,
            email_cliente=email_huesped,
            db=db,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error Stripe: {str(e)}")


@router.post("/stripe/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: Optional[str] = Header(None),
    db: Session = Depends(get_sync_db),
):
    """Webhook Stripe. Verifica firma antes de procesar."""
    payload_raw = await request.body()

    if not stripe_signature:
        raise HTTPException(
            status_code=400, detail="Falta header Stripe-Signature"
        )

    try:
        evento = svc_pagos.verificar_firma_webhook_stripe(
            payload_raw, stripe_signature
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    resultado = svc_pagos.procesar_evento_stripe(evento, db)
    return {"ok": True, **resultado}


@router.get("/{pago_id}/estado")
def estado_pago(
    pago_id: str,
    db: Session = Depends(get_sync_db),
):
    """Estado público del pago (para polling desde el frontend)."""
    try:
        pid = uuid.UUID(pago_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="pago_id inválido")

    pago = svc_pagos.obtener_estado_pago(pid, db)
    return {
        "pago_id": str(pago.id),
        "estado": pago.estado,
        "pasarela": pago.pasarela,
        "monto": float(pago.monto),
        "moneda": pago.moneda,
        "created_at": pago.created_at.isoformat(),
    }

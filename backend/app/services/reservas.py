"""
Servicio de gestión de reservas — Sprint 2.

Máquina de estados:
  pendiente → otp_pendiente → otp_verificado → pago_pendiente
           → confirmada → checkin → checkout
           → cancelada | noshow (cualquier estado activo)
"""
from __future__ import annotations

import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from fastapi import HTTPException, status
from sqlmodel import Session, select, func

from app.models.reserva import Reserva
from app.services.disponibilidad import verificar_disponibilidad
from app.services.precio import calcular_precio, NOCHES_MINIMAS

# Transiciones permitidas de la máquina de estados
TRANSICIONES: dict[str, list[str]] = {
    "pendiente":      ["otp_pendiente", "cancelada"],
    "otp_pendiente":  ["otp_verificado", "cancelada"],
    "otp_verificado": ["pago_pendiente", "cancelada"],
    "pago_pendiente": ["confirmada", "cancelada"],
    "confirmada":     ["checkin", "cancelada"],
    "checkin":        ["checkout"],
    "checkout":       [],
    "cancelada":      [],
    "noshow":         [],
}

ESTADOS_CANCELABLES = {"pendiente", "otp_pendiente", "otp_verificado", "pago_pendiente", "confirmada"}


def generar_codigo(db: Session) -> str:
    """Genera código único HLC-YYYY-NNNN."""
    year = datetime.utcnow().year
    count = db.exec(select(func.count(Reserva.id))).one()
    return f"HLC-{year}-{(count + 1):04d}"


def crear_reserva(
    fecha_checkin: date,
    fecha_checkout: date,
    huespedes: int,
    addon_ids: list[str],
    notas_huesped: Optional[str],
    usuario_id: str,
    db: Session,
) -> Reserva:
    """
    Crea una nueva reserva después de validar disponibilidad y calcular precio.
    Requiere que el usuario ya haya verificado su OTP (token tipo otp_verified).
    """
    noches = (fecha_checkout - fecha_checkin).days

    if noches < NOCHES_MINIMAS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mínimo {NOCHES_MINIMAS} noches de estancia.",
        )
    if not 1 <= huespedes <= 18:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El número de huéspedes debe estar entre 1 y 18.",
        )

    disponible, fechas_bloqueadas = verificar_disponibilidad(
        fecha_checkin, fecha_checkout, db
    )
    if not disponible:
        primeras = [str(f) for f in fechas_bloqueadas[:3]]
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Las fechas seleccionadas no están disponibles. "
                   f"Fechas bloqueadas: {primeras}",
        )

    precio = calcular_precio(fecha_checkin, fecha_checkout, addon_ids)
    codigo = generar_codigo(db)

    reserva = Reserva(
        codigo=codigo,
        usuario_id=uuid.UUID(usuario_id),
        canal="directo",
        estado="otp_verificado",
        fecha_checkin=fecha_checkin,
        fecha_checkout=fecha_checkout,
        noches=noches,
        huespedes=huespedes,
        precio_total_cop=precio["total_cop"],
        precio_total_usd=precio["total_usd"],
        moneda="COP",
        notas_huesped=notas_huesped,
    )
    db.add(reserva)
    db.commit()
    db.refresh(reserva)
    return reserva


def transicionar_estado(
    reserva: Reserva, nuevo_estado: str, db: Session
) -> Reserva:
    """
    Aplica una transición de estado a la reserva validando que sea permitida.
    """
    permitidos = TRANSICIONES.get(reserva.estado, [])
    if nuevo_estado not in permitidos:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"No se puede cambiar de '{reserva.estado}' a '{nuevo_estado}'. "
                f"Transiciones permitidas: {permitidos or 'ninguna'}"
            ),
        )
    reserva.estado = nuevo_estado
    reserva.updated_at = datetime.utcnow()
    db.add(reserva)
    db.commit()
    db.refresh(reserva)
    return reserva


def transicionar_estado_por_id(
    reserva_id: uuid.UUID, nuevo_estado: str, db: Session
) -> Reserva:
    """
    Busca la reserva por ID y aplica una transición de estado.
    Variante de transicionar_estado que acepta UUID en lugar de objeto Reserva.
    Usada internamente por el servicio de pagos tras confirmación de pago.
    Lanza HTTPException 404 si la reserva no existe, 400 si la transición no está permitida.
    """
    reserva = db.get(Reserva, reserva_id)
    if not reserva:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva no encontrada",
        )
    return transicionar_estado(reserva, nuevo_estado, db)

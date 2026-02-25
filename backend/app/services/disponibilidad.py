"""
Servicio de disponibilidad del calendario — Sprint 2.

Una fecha está BLOQUEADA si:
1. Existe un BloqueoCalendario que la cubre, O
2. Existe una Reserva activa (estado ∈ ESTADOS_OCUPADOS) que la cubre.
"""
from __future__ import annotations

from datetime import date, timedelta
from typing import Optional

from sqlmodel import Session, select

from app.models.bloqueo_calendario import BloqueoCalendario
from app.models.reserva import Reserva

ESTADOS_OCUPADOS = (
    "otp_pendiente",
    "otp_verificado",
    "pago_pendiente",
    "confirmada",
    "checkin",
)


def obtener_fechas_bloqueadas(
    desde: date, hasta: date, db: Session
) -> list[date]:
    """
    Retorna lista ordenada de fechas bloqueadas en el rango [desde, hasta] inclusive.
    """
    bloqueadas: set[date] = set()

    # 1. BloqueoCalendario manual / canal manager
    bloqueos = db.exec(
        select(BloqueoCalendario).where(
            BloqueoCalendario.fecha_inicio <= hasta,
            BloqueoCalendario.fecha_fin >= desde,
        )
    ).all()
    for b in bloqueos:
        d = max(b.fecha_inicio, desde)
        fin = min(b.fecha_fin, hasta)
        while d <= fin:
            bloqueadas.add(d)
            d += timedelta(days=1)

    # 2. Reservas activas (excluye canceladas / noshow / checkout)
    reservas = db.exec(
        select(Reserva).where(
            Reserva.estado.in_(list(ESTADOS_OCUPADOS)),
            Reserva.fecha_checkin < hasta + timedelta(days=1),
            Reserva.fecha_checkout > desde,
            Reserva.deleted_at == None,   # noqa: E711
        )
    ).all()
    for r in reservas:
        # El día de checkout NO cuenta como bloqueado
        d = max(r.fecha_checkin, desde)
        fin = min(r.fecha_checkout - timedelta(days=1), hasta)
        while d <= fin:
            bloqueadas.add(d)
            d += timedelta(days=1)

    return sorted(bloqueadas)


def verificar_disponibilidad(
    fecha_checkin: date,
    fecha_checkout: date,
    db: Session,
) -> tuple[bool, list[date]]:
    """
    Verifica si el rango [checkin, checkout) está completamente libre.

    Retorna (disponible: bool, fechas_bloqueadas: list[date]).
    """
    # Las fechas bloqueadas dentro del rango [checkin, checkout - 1]
    bloqueadas = obtener_fechas_bloqueadas(
        desde=fecha_checkin,
        hasta=fecha_checkout - timedelta(days=1),
        db=db,
    )
    return len(bloqueadas) == 0, bloqueadas

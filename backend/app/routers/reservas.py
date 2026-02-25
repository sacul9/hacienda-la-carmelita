"""
Router de reservas — Sprint 2.

POST /reservas              → crear reserva (requiere OTP verificado)
GET  /reservas              → listar (solo admin)
GET  /reservas/{codigo}     → detalle por código HLC-XXXX
PUT  /reservas/{id}/cancelar → cancelar (usuario o admin)
PUT  /reservas/{id}/checkin  → marcar check-in (staff/admin)
PUT  /reservas/{id}/checkout → marcar check-out (staff/admin)
"""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session, select

from app.auth.dependencies import (
    get_current_user,
    get_otp_token_payload,
    require_admin,
    require_staff,
)
from app.database import get_sync_db
from app.models.reserva import Reserva
from app.models.usuario import Usuario
from app.schemas.reserva import CrearReservaRequest, ReservaResponse
from app.services.reservas import (
    crear_reserva,
    transicionar_estado,
    ESTADOS_CANCELABLES,
)

router = APIRouter()


def _reserva_a_response(r: Reserva) -> ReservaResponse:
    return ReservaResponse(
        id=str(r.id),
        codigo=r.codigo,
        estado=r.estado,
        fecha_checkin=r.fecha_checkin,
        fecha_checkout=r.fecha_checkout,
        noches=r.noches or 0,
        huespedes=r.huespedes,
        precio_total_cop=r.precio_total_cop,
        precio_total_usd=r.precio_total_usd,
        moneda=r.moneda,
    )


# ─── POST /reservas ───────────────────────────────────────────────────────────

@router.post(
    "",
    response_model=ReservaResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Crear reserva (requiere OTP verificado)",
)
def post_crear_reserva(
    body: CrearReservaRequest,
    otp_payload: dict = Depends(get_otp_token_payload),
    db: Session = Depends(get_sync_db),
) -> ReservaResponse:
    """
    Crea una nueva reserva. El header Authorization debe contener un JWT
    de tipo otp_verified obtenido al completar la verificación OTP.
    """
    usuario_id: str = otp_payload.get("sub", "")
    if not usuario_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token OTP inválido: falta 'sub'.",
        )

    reserva = crear_reserva(
        fecha_checkin=body.fecha_checkin,
        fecha_checkout=body.fecha_checkout,
        huespedes=body.huespedes,
        addon_ids=body.addon_ids,
        notas_huesped=body.notas_huesped,
        usuario_id=usuario_id,
        db=db,
    )
    return _reserva_a_response(reserva)


# ─── GET /reservas ────────────────────────────────────────────────────────────

@router.get(
    "",
    response_model=list[ReservaResponse],
    summary="Listar reservas (solo admin)",
)
def get_listar_reservas(
    estado: Optional[str] = Query(default=None, description="Filtrar por estado"),
    page: int = Query(default=1, ge=1),
    per_page: int = Query(default=20, ge=1, le=100),
    current_user: Usuario = Depends(require_admin),
    db: Session = Depends(get_sync_db),
) -> list[ReservaResponse]:
    q = select(Reserva).where(Reserva.deleted_at == None)   # noqa: E711
    if estado:
        q = q.where(Reserva.estado == estado)
    q = q.offset((page - 1) * per_page).limit(per_page)
    reservas = db.exec(q).all()
    return [_reserva_a_response(r) for r in reservas]


# ─── GET /reservas/{codigo} ───────────────────────────────────────────────────

@router.get(
    "/{codigo}",
    response_model=ReservaResponse,
    summary="Detalle de reserva por código",
)
def get_reserva(
    codigo: str,
    db: Session = Depends(get_sync_db),
) -> ReservaResponse:
    """Pública: cualquier persona con el código puede consultar su reserva."""
    reserva = db.exec(
        select(Reserva).where(
            Reserva.codigo == codigo.upper(),
            Reserva.deleted_at == None,   # noqa: E711
        )
    ).first()
    if not reserva:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Reserva '{codigo}' no encontrada.",
        )
    return _reserva_a_response(reserva)


# ─── PUT /reservas/{id}/cancelar ─────────────────────────────────────────────

@router.put(
    "/{id}/cancelar",
    response_model=ReservaResponse,
    summary="Cancelar reserva",
)
def put_cancelar(
    id: str,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_sync_db),
) -> ReservaResponse:
    reserva = db.exec(
        select(Reserva).where(
            Reserva.id == uuid.UUID(id),
            Reserva.deleted_at == None,   # noqa: E711
        )
    ).first()
    if not reserva:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada.")

    es_admin = current_user.rol == "admin"
    es_dueno = reserva.usuario_id == current_user.id
    if not (es_admin or es_dueno):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No autorizado.")

    if reserva.estado not in ESTADOS_CANCELABLES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede cancelar una reserva en estado '{reserva.estado}'.",
        )

    reserva = transicionar_estado(reserva, "cancelada", db)
    return _reserva_a_response(reserva)


# ─── PUT /reservas/{id}/checkin ───────────────────────────────────────────────

@router.put(
    "/{id}/checkin",
    response_model=ReservaResponse,
    summary="Registrar check-in (staff/admin)",
)
def put_checkin(
    id: str,
    current_user: Usuario = Depends(require_staff),
    db: Session = Depends(get_sync_db),
) -> ReservaResponse:
    reserva = db.exec(
        select(Reserva).where(
            Reserva.id == uuid.UUID(id),
            Reserva.deleted_at == None,   # noqa: E711
        )
    ).first()
    if not reserva:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada.")
    reserva = transicionar_estado(reserva, "checkin", db)
    return _reserva_a_response(reserva)


# ─── PUT /reservas/{id}/checkout ─────────────────────────────────────────────

@router.put(
    "/{id}/checkout",
    response_model=ReservaResponse,
    summary="Registrar check-out (staff/admin)",
)
def put_checkout(
    id: str,
    current_user: Usuario = Depends(require_staff),
    db: Session = Depends(get_sync_db),
) -> ReservaResponse:
    reserva = db.exec(
        select(Reserva).where(
            Reserva.id == uuid.UUID(id),
            Reserva.deleted_at == None,   # noqa: E711
        )
    ).first()
    if not reserva:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Reserva no encontrada.")
    reserva = transicionar_estado(reserva, "checkout", db)
    return _reserva_a_response(reserva)

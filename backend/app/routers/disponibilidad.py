"""
Router de disponibilidad — Sprint 2.

GET /disponibilidad          → fechas bloqueadas + si el rango está libre
GET /disponibilidad/precio   → desglose de precio por noches
"""
from __future__ import annotations

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlmodel import Session

from app.database import get_sync_db
from app.schemas.reserva import DisponibilidadResponse, PrecioResponse
from app.services.disponibilidad import verificar_disponibilidad
from app.services.precio import calcular_precio, NOCHES_MINIMAS

router = APIRouter()


def _parse_fecha(valor: str, nombre: str) -> date:
    """Parsea YYYY-MM-DD o retorna HTTP 422."""
    try:
        return date.fromisoformat(valor)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=422,
            detail=f"'{nombre}' debe estar en formato YYYY-MM-DD. Valor recibido: '{valor}'",
        )


@router.get("", response_model=DisponibilidadResponse, summary="Verificar disponibilidad")
def get_disponibilidad(
    desde: str = Query(..., description="Fecha inicio YYYY-MM-DD"),
    hasta: str = Query(..., description="Fecha fin YYYY-MM-DD"),
    db: Session = Depends(get_sync_db),
) -> DisponibilidadResponse:
    """
    Retorna las fechas bloqueadas en el rango y si toda la estancia está disponible.
    """
    fecha_desde = _parse_fecha(desde, "desde")
    fecha_hasta = _parse_fecha(hasta, "hasta")

    if fecha_desde >= fecha_hasta:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="'hasta' debe ser posterior a 'desde'.",
        )

    disponible, bloqueadas = verificar_disponibilidad(fecha_desde, fecha_hasta, db)

    return DisponibilidadResponse(
        fechas_bloqueadas=[str(f) for f in bloqueadas],
        disponible=disponible,
        mensaje=None if disponible else f"{len(bloqueadas)} fecha(s) no disponible(s).",
    )


@router.get("/precio", response_model=PrecioResponse, summary="Calcular precio de estancia")
def get_precio(
    desde: str = Query(..., description="Fecha checkin YYYY-MM-DD"),
    hasta: str = Query(..., description="Fecha checkout YYYY-MM-DD"),
    huespedes: int = Query(default=1, ge=1, le=18, description="Número de huéspedes"),
    skus: Optional[str] = Query(default=None, description="SKUs adicionales (ignorado en MVP)"),
    db: Session = Depends(get_sync_db),
) -> PrecioResponse:
    """
    Calcula el precio total de la estancia con desglose por noche.
    """
    fecha_desde = _parse_fecha(desde, "desde")
    fecha_hasta = _parse_fecha(hasta, "hasta")

    if fecha_desde >= fecha_hasta:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="'hasta' debe ser posterior a 'desde'.",
        )

    noches = (fecha_hasta - fecha_desde).days
    if noches < NOCHES_MINIMAS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Mínimo {NOCHES_MINIMAS} noches. Se solicitó {noches}.",
        )

    addon_ids = skus.split(",") if skus else []
    precio = calcular_precio(fecha_desde, fecha_hasta, addon_ids)

    return PrecioResponse(**precio)

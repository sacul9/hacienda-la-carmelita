from pydantic import BaseModel, field_validator
from datetime import date
from decimal import Decimal
from typing import Optional
import re


class CrearReservaRequest(BaseModel):
    fecha_checkin: date
    fecha_checkout: date
    huespedes: int
    sku_id: str
    addon_ids: list[str] = []
    notas_huesped: Optional[str] = None
    # El usuario_id viene del token OTP, no del body

    @field_validator("fecha_checkout")
    @classmethod
    def checkout_despues_checkin(cls, v: date, info) -> date:
        if "fecha_checkin" in info.data and v <= info.data["fecha_checkin"]:
            raise ValueError("La fecha de checkout debe ser posterior al checkin")
        return v

    @field_validator("huespedes")
    @classmethod
    def huespedes_valido(cls, v: int) -> int:
        if v < 1 or v > 18:
            raise ValueError("Número de huéspedes debe ser entre 1 y 18")
        return v


class ReservaResponse(BaseModel):
    id: str
    codigo: str
    estado: str
    fecha_checkin: date
    fecha_checkout: date
    noches: int
    huespedes: int
    precio_total_cop: Optional[Decimal]
    precio_total_usd: Optional[Decimal]
    moneda: str


class DisponibilidadResponse(BaseModel):
    fechas_bloqueadas: list[str]   # ISO format YYYY-MM-DD
    disponible: bool
    mensaje: Optional[str] = None


class PrecioResponse(BaseModel):
    noches: int
    precio_base_cop: Decimal
    addons_cop: Decimal
    total_cop: Decimal
    total_usd: Optional[Decimal]
    desglose: list[dict]

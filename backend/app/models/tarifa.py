"""
Modelo de tarifas — Sprint 6
Permite gestionar precios desde el panel admin.
"""
import uuid
from datetime import datetime
from decimal import Decimal
from sqlmodel import SQLModel, Field


class Tarifa(SQLModel, table=True):
    __tablename__ = "tarifas"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
    )
    temporada: str = Field(max_length=20, unique=True)
    # 'baja' | 'alta' | 'especial'
    descripcion: str = Field(max_length=100)
    # ej. "Lunes a Jueves" | "Viernes a Domingo"
    tarifa_cop: Decimal = Field(decimal_places=0, max_digits=12)
    activo: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

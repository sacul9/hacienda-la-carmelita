import uuid
from decimal import Decimal
from typing import Optional
from sqlmodel import SQLModel, Field


class ReservaExperiencia(SQLModel, table=True):
    __tablename__ = "reservas_experiencias"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
    )
    reserva_id: uuid.UUID = Field(foreign_key="reservas.id", index=True)
    experiencia_id: uuid.UUID = Field(foreign_key="experiencias.id")
    cantidad: int = Field(default=1)
    precio_cop: Optional[Decimal] = Field(default=None, decimal_places=0, max_digits=12)
    precio_usd: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=8)

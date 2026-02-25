import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON, ForeignKey


class Pago(SQLModel, table=True):
    __tablename__ = "pagos"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
    )
    reserva_id: uuid.UUID = Field(
        sa_column=Column(
            "reserva_id",
            ForeignKey("reservas.id", use_alter=True, name="fk_pagos_reserva_id"),
            index=True,
            nullable=False,
        )
    )
    pasarela: str = Field(max_length=20)          # 'wompi' | 'stripe'
    pasarela_pago_id: Optional[str] = Field(default=None, max_length=200)
    monto: Decimal = Field(decimal_places=0, max_digits=14)
    moneda: str = Field(max_length=3)
    estado: str = Field(max_length=30)             # pendiente | aprobado | rechazado | reembolsado
    metodo: Optional[str] = Field(default=None, max_length=50)  # pse | tarjeta | nequi | etc.
    metadatos: Optional[dict] = Field(default={}, sa_column=Column(JSON))
    # CRÍTICO: Nunca almacenar número de tarjeta, CVV ni datos sensibles
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

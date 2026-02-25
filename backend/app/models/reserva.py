import uuid
from datetime import datetime, date
from decimal import Decimal
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON


class Reserva(SQLModel, table=True):
    __tablename__ = "reservas"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
    )
    codigo: str = Field(unique=True, index=True, max_length=12)  # HLC-2025-0042
    usuario_id: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id", index=True)
    canal: str = Field(max_length=30)          # 'directo' | 'airbnb' | 'booking'
    canal_reserva_id: Optional[str] = Field(default=None, max_length=100)
    estado: str = Field(default="pendiente", max_length=30)
    # Estados: pendiente | otp_pendiente | otp_verificado | pago_pendiente
    #          confirmada | checkin | checkout | cancelada | noshow
    fecha_checkin: date
    fecha_checkout: date
    noches: Optional[int] = Field(default=None)  # calculado: checkout - checkin
    huespedes: int
    precio_total_cop: Optional[Decimal] = Field(default=None, decimal_places=0, max_digits=14)
    precio_total_usd: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=10)
    moneda: str = Field(default="COP", max_length=3)
    notas_huesped: Optional[str] = Field(default=None)
    notas_internas: Optional[str] = Field(default=None)
    otp_id: Optional[uuid.UUID] = Field(default=None, foreign_key="otps.id")
    pago_id: Optional[uuid.UUID] = Field(default=None, foreign_key="pagos.id")
    metadatos: Optional[dict] = Field(default={}, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = Field(default=None)

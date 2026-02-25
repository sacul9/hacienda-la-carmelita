import uuid
from datetime import datetime, date
from typing import Optional
from sqlmodel import SQLModel, Field


class BloqueoCalendario(SQLModel, table=True):
    __tablename__ = "bloqueos_calendario"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
    )
    fecha_inicio: date = Field(index=True)
    fecha_fin: date = Field(index=True)
    motivo: Optional[str] = Field(default=None, max_length=100)
    # 'mantenimiento' | 'uso_personal' | 'reservado' | 'temporada'
    origen: str = Field(default="manual", max_length=30)
    # manual | airbnb | booking | sistema
    tipo: Optional[str] = Field(default="manual", max_length=30)
    # 'manual' | 'reserva_ota' | 'reserva_directa' | 'mantenimiento'
    created_by: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)

import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON


class Habitacion(SQLModel, table=True):
    __tablename__ = "habitaciones"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
    )
    numero: int = Field(unique=True)
    nombre: str = Field(max_length=100)
    capacidad: int
    descripcion: Optional[str] = Field(default=None)
    amenidades: Optional[list] = Field(default=[], sa_column=Column(JSON))
    fotos: Optional[list] = Field(default=[], sa_column=Column(JSON))
    activa: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

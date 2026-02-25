import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON


class Experiencia(SQLModel, table=True):
    __tablename__ = "experiencias"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
    )
    slug: str = Field(unique=True, index=True, max_length=100)
    nombre_es: str = Field(max_length=200)
    nombre_en: str = Field(max_length=200)
    descripcion_es: Optional[str] = Field(default=None)
    descripcion_en: Optional[str] = Field(default=None)
    duracion_horas: Optional[Decimal] = Field(default=None, decimal_places=1, max_digits=4)
    capacidad_min: int = Field(default=1)
    capacidad_max: int = Field(default=16)
    precio_cop: Decimal = Field(decimal_places=0, max_digits=12)
    precio_usd: Optional[Decimal] = Field(default=None, decimal_places=2, max_digits=8)
    incluye_es: Optional[list] = Field(default=[], sa_column=Column(JSON))
    incluye_en: Optional[list] = Field(default=[], sa_column=Column(JSON))
    fotos: Optional[list] = Field(default=[], sa_column=Column(JSON))
    activa: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

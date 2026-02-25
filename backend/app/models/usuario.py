import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON


class Usuario(SQLModel, table=True):
    __tablename__ = "usuarios"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
    )
    email: str = Field(unique=True, index=True, max_length=255)
    telefono: Optional[str] = Field(default=None, max_length=20)
    whatsapp: Optional[str] = Field(default=None, max_length=20)
    nombre: str = Field(max_length=200)
    apellido: str = Field(max_length=200)
    pais: str = Field(default="CO", max_length=2)
    idioma: str = Field(default="es", max_length=2)
    rol: str = Field(default="guest", max_length=20)  # guest | staff | admin
    # SEC-001 fix: bcrypt hash para autenticación staff/admin
    password_hash: Optional[str] = Field(default=None)
    email_verificado: bool = Field(default=False)
    telefono_verificado: bool = Field(default=False)
    fecha_nacimiento: Optional[datetime] = Field(default=None)
    preferencias: Optional[dict] = Field(default={}, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    deleted_at: Optional[datetime] = Field(default=None)


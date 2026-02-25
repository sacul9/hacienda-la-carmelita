import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class OTP(SQLModel, table=True):
    __tablename__ = "otps"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
    )
    usuario_id: Optional[uuid.UUID] = Field(default=None, foreign_key="usuarios.id")
    canal: str = Field(max_length=20)       # 'email' | 'sms' | 'whatsapp'
    destino: str = Field(max_length=255)    # email o teléfono
    codigo: str = Field(max_length=64)      # hash SHA-256 del código (nunca el código plain)
    proposito: str = Field(max_length=50)   # 'registro' | 'reserva' | 'login' | 'pago'
    intentos: int = Field(default=0)        # máx 3 intentos
    verificado: bool = Field(default=False)
    expires_at: datetime
    created_at: datetime = Field(default_factory=datetime.utcnow)

import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field


class SyncLog(SQLModel, table=True):
    __tablename__ = "sync_logs"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    canal: str = Field(max_length=30)          # 'lodgify' | 'airbnb' | 'booking' | 'manual'
    estado: str = Field(max_length=20)         # 'ok' | 'error' | 'en_progreso'
    reservas_importadas: int = Field(default=0)
    reservas_ya_existian: int = Field(default=0)
    conflictos_detectados: int = Field(default=0)
    mensaje_error: Optional[str] = Field(default=None, max_length=500)
    duracion_ms: Optional[int] = Field(default=None)
    iniciado_por: str = Field(default="celery_beat", max_length=50)  # 'celery_beat' | 'manual_admin'
    created_at: datetime = Field(default_factory=datetime.utcnow)

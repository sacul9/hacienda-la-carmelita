import uuid
from datetime import datetime

from sqlmodel import SQLModel, Field


class GeoContenido(SQLModel, table=True):
    __tablename__ = "geo_contenido"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
    )
    # Tipo de contenido: 'llms_txt' | 'faq_jsonld' | 'about_snippet'
    tipo: str = Field(index=True, max_length=50)
    # Contenido en texto plano o JSON serializado como string
    contenido: str
    version: int = Field(default=1)
    activo: bool = Field(default=True)
    # Agente que generó el contenido
    generado_por: str = Field(default="geo_agent", max_length=50)
    created_at: datetime = Field(default_factory=datetime.utcnow)

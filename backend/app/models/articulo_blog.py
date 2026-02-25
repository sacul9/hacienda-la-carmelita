import uuid
from datetime import datetime
from typing import Optional
from sqlmodel import SQLModel, Field
from sqlalchemy import Column, JSON


class ArticuloBlog(SQLModel, table=True):
    __tablename__ = "articulos_blog"

    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
    )
    slug: str = Field(unique=True, index=True, max_length=200)
    titulo_es: str = Field(max_length=300)
    titulo_en: Optional[str] = Field(default=None, max_length=300)
    contenido_es: str
    contenido_en: Optional[str] = Field(default=None)
    resumen_es: Optional[str] = Field(default=None)
    resumen_en: Optional[str] = Field(default=None)
    palabras_clave: Optional[list] = Field(default=[], sa_column=Column(JSON))
    meta_descripcion_es: Optional[str] = Field(default=None, max_length=160)
    meta_descripcion_en: Optional[str] = Field(default=None, max_length=160)
    schema_markup: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    autor_agente: Optional[str] = Field(default=None, max_length=50)
    publicado: bool = Field(default=False)
    fecha_publicacion: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

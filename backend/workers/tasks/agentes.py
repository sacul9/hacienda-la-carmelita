"""
Tareas de Celery para los Agentes de IA — Sprint 8
SEO Agent: genera artículos de blog SEO (lunes 7am)
GEO Agent: genera contenido estructurado para LLMs (quincenal)
"""
from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime

from workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="agentes.generar_articulo_seo", bind=True, max_retries=2)
def generar_articulo_seo(self):
    """
    Genera un artículo de blog SEO y lo publica en la BD.
    Programado: lunes 7am (America/Bogota).
    """
    # Importaciones locales para evitar circular imports con Celery
    from sqlmodel import Session
    from app.database import _get_sync_engine  # noqa: PLC0415
    from app.services import seo_agent  # noqa: PLC0415

    try:
        engine = _get_sync_engine()
        with Session(engine) as db:
            logger.info("[SEO Agent] Seleccionando tema disponible...")
            tema = seo_agent.seleccionar_tema_disponible(db)

            logger.info("[SEO Agent] Generando artículo para tema: %s", tema)
            articulo_data = seo_agent.generar_articulo_seo(tema)

            logger.info("[SEO Agent] Guardando artículo en BD. Slug: %s", articulo_data.get("slug"))
            articulo = seo_agent.guardar_articulo(articulo_data, db, publicado=True)

            resultado = {
                "articulo_id": str(articulo.id),
                "slug": articulo.slug,
                "titulo_es": articulo.titulo_es,
                "publicado": articulo.publicado,
            }
            logger.info("[SEO Agent] Artículo generado y publicado: %s", resultado)
            return resultado

    except Exception as exc:
        logger.error("[SEO Agent] Error al generar artículo: %s", exc, exc_info=True)
        return {"error": str(exc)}


@celery_app.task(name="agentes.generar_contenido_geo", bind=True, max_retries=2)
def generar_contenido_geo(self):
    """
    Genera contenido GEO (llms.txt + FAQ JSON-LD) y lo guarda en la BD.
    Programado: cada 14 días.
    """
    # Importaciones locales para evitar circular imports con Celery
    from sqlmodel import Session, select
    from app.database import _get_sync_engine  # noqa: PLC0415
    from app.services import geo_agent  # noqa: PLC0415
    from app.models.geo_contenido import GeoContenido  # noqa: PLC0415

    try:
        engine = _get_sync_engine()

        # 1. Generar contenido con Claude
        logger.info("[GEO Agent] Generando llms.txt...")
        llms_txt_contenido = geo_agent.generar_llms_txt()

        logger.info("[GEO Agent] Generando FAQ JSON-LD...")
        faq_jsonld_data = geo_agent.generar_faq_jsonld()
        faq_jsonld_str = json.dumps(faq_jsonld_data, ensure_ascii=False, indent=2)

        ahora = datetime.utcnow()

        with Session(engine) as db:
            # 2. Desactivar versiones anteriores del mismo tipo y calcular siguiente versión

            def _desactivar_y_siguiente_version(tipo: str) -> int:
                """Desactiva registros activos del tipo y retorna el siguiente número de versión."""
                stmt = select(GeoContenido).where(
                    GeoContenido.tipo == tipo,
                    GeoContenido.activo == True,  # noqa: E712
                )
                registros_activos = db.exec(stmt).all()
                version_max = 0
                for reg in registros_activos:
                    reg.activo = False
                    db.add(reg)
                    if reg.version > version_max:
                        version_max = reg.version
                return version_max + 1

            # --- llms.txt ---
            siguiente_version_llms = _desactivar_y_siguiente_version("llms_txt")
            nuevo_llms = GeoContenido(
                id=uuid.uuid4(),
                tipo="llms_txt",
                contenido=llms_txt_contenido,
                version=siguiente_version_llms,
                activo=True,
                generado_por="geo_agent",
                created_at=ahora,
            )
            db.add(nuevo_llms)

            # --- faq_jsonld ---
            siguiente_version_faq = _desactivar_y_siguiente_version("faq_jsonld")
            nuevo_faq = GeoContenido(
                id=uuid.uuid4(),
                tipo="faq_jsonld",
                contenido=faq_jsonld_str,
                version=siguiente_version_faq,
                activo=True,
                generado_por="geo_agent",
                created_at=ahora,
            )
            db.add(nuevo_faq)

            db.commit()
            db.refresh(nuevo_llms)
            db.refresh(nuevo_faq)

            resultado = {
                "llms_txt_id": str(nuevo_llms.id),
                "llms_txt_version": nuevo_llms.version,
                "faq_id": str(nuevo_faq.id),
                "faq_version": nuevo_faq.version,
            }
            logger.info("[GEO Agent] Contenido GEO generado y guardado: %s", resultado)
            return resultado

    except Exception as exc:
        logger.error("[GEO Agent] Error al generar contenido GEO: %s", exc, exc_info=True)
        return {"error": str(exc)}


@celery_app.task
def sincronizar_otas():
    """Sincroniza reservas con Airbnb y Booking (cada 15 min)."""
    logger.warning("TODO Sprint 7: not yet implemented")
    return None

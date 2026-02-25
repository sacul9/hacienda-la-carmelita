"""
Router de Agentes de IA — Sprint 8
Endpoints para disparar y consultar los agentes SEO y GEO.
"""
from __future__ import annotations

import json
import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import PlainTextResponse
from sqlmodel import Session, select

from app.auth.dependencies import require_admin
from app.models.usuario import Usuario
from app.database import get_sync_db

logger = logging.getLogger(__name__)

router = APIRouter()


# ---------------------------------------------------------------------------
# SEC-006: Todos los triggers de agentes requieren rol 'admin'
# ---------------------------------------------------------------------------

@router.post("/seo/generar", status_code=202)
async def generar_articulo_seo(
    current_user: Usuario = Depends(require_admin),
):
    """
    Dispara la generación de un artículo SEO de forma asíncrona.
    Si Celery no está disponible, llama al servicio directamente (modo síncrono).
    Solo Admin.
    """
    try:
        from workers.tasks.agentes import generar_articulo_seo as task_seo  # noqa: PLC0415
        result = task_seo.delay()
        return {
            "status": "encolado",
            "task_id": result.id,
            "message": "Generación de artículo SEO encolada. Consulta el task_id para ver el resultado.",
        }
    except Exception as celery_exc:
        logger.warning(
            "Celery no disponible, ejecutando SEO agent de forma síncrona: %s", celery_exc
        )
        try:
            from app.services import seo_agent  # noqa: PLC0415
            from app.database import _get_sync_engine  # noqa: PLC0415
            from sqlmodel import Session  # noqa: PLC0415

            engine = _get_sync_engine()
            with Session(engine) as db:
                tema = seo_agent.seleccionar_tema_disponible(db)
                articulo_data = seo_agent.generar_articulo_seo(tema)
                articulo = seo_agent.guardar_articulo(articulo_data, db, publicado=True)

            return {
                "status": "completado",
                "task_id": None,
                "articulo_id": str(articulo.id),
                "slug": articulo.slug,
                "titulo_es": articulo.titulo_es,
                "message": "Artículo SEO generado y publicado (modo síncrono).",
            }
        except Exception as svc_exc:
            logger.error("Error en SEO agent síncrono: %s", svc_exc, exc_info=True)
            raise HTTPException(status_code=500, detail=str(svc_exc)) from svc_exc


@router.post("/geo/generar", status_code=202)
async def generar_contenido_geo(
    current_user: Usuario = Depends(require_admin),
):
    """
    Dispara la generación de contenido GEO (llms.txt + FAQ JSON-LD) de forma asíncrona.
    Si Celery no está disponible, ejecuta el servicio directamente.
    Solo Admin.
    """
    try:
        from workers.tasks.agentes import generar_contenido_geo as task_geo  # noqa: PLC0415
        result = task_geo.delay()
        return {
            "status": "encolado",
            "task_id": result.id,
            "message": "Generación de contenido GEO encolada. Consulta el task_id para ver el resultado.",
        }
    except Exception as celery_exc:
        logger.warning(
            "Celery no disponible, ejecutando GEO agent de forma síncrona: %s", celery_exc
        )
        try:
            import uuid  # noqa: PLC0415
            from datetime import datetime  # noqa: PLC0415
            from app.services import geo_agent  # noqa: PLC0415
            from app.database import _get_sync_engine  # noqa: PLC0415
            from app.models.geo_contenido import GeoContenido  # noqa: PLC0415
            from sqlmodel import Session, select  # noqa: PLC0415

            llms_txt_contenido = geo_agent.generar_llms_txt()
            faq_jsonld_data = geo_agent.generar_faq_jsonld()
            faq_jsonld_str = json.dumps(faq_jsonld_data, ensure_ascii=False, indent=2)

            ahora = datetime.utcnow()
            engine = _get_sync_engine()

            with Session(engine) as db:
                def _desactivar(tipo: str) -> int:
                    stmt = select(GeoContenido).where(
                        GeoContenido.tipo == tipo,
                        GeoContenido.activo == True,  # noqa: E712
                    )
                    registros = db.exec(stmt).all()
                    version_max = 0
                    for reg in registros:
                        reg.activo = False
                        db.add(reg)
                        if reg.version > version_max:
                            version_max = reg.version
                    return version_max + 1

                v_llms = _desactivar("llms_txt")
                nuevo_llms = GeoContenido(
                    id=uuid.uuid4(), tipo="llms_txt", contenido=llms_txt_contenido,
                    version=v_llms, activo=True, generado_por="geo_agent", created_at=ahora,
                )
                db.add(nuevo_llms)

                v_faq = _desactivar("faq_jsonld")
                nuevo_faq = GeoContenido(
                    id=uuid.uuid4(), tipo="faq_jsonld", contenido=faq_jsonld_str,
                    version=v_faq, activo=True, generado_por="geo_agent", created_at=ahora,
                )
                db.add(nuevo_faq)
                db.commit()
                db.refresh(nuevo_llms)
                db.refresh(nuevo_faq)

            return {
                "status": "completado",
                "task_id": None,
                "llms_txt_id": str(nuevo_llms.id),
                "faq_id": str(nuevo_faq.id),
                "message": "Contenido GEO generado y guardado (modo síncrono).",
            }
        except Exception as svc_exc:
            logger.error("Error en GEO agent síncrono: %s", svc_exc, exc_info=True)
            raise HTTPException(status_code=500, detail=str(svc_exc)) from svc_exc


@router.get("/seo/articulos", status_code=200)
async def listar_articulos_seo(
    page: int = Query(default=1, ge=1, description="Número de página"),
    limit: int = Query(default=10, ge=1, le=50, description="Artículos por página"),
    todos: bool = Query(default=False, description="Admin: incluir no publicados"),
    current_user: Optional[Usuario] = None,
    db: Session = Depends(get_sync_db),
):
    """
    Lista artículos del blog SEO de forma paginada.
    Por defecto retorna solo los publicados.
    Admins pueden ver todos con ?todos=true.
    """
    from app.models.articulo_blog import ArticuloBlog  # noqa: PLC0415

    stmt = select(ArticuloBlog)

    # Solo admins pueden ver no publicados
    mostrar_todos = todos and current_user and getattr(current_user, "rol", None) == "admin"
    if not mostrar_todos:
        stmt = stmt.where(ArticuloBlog.publicado == True)  # noqa: E712

    stmt = stmt.order_by(ArticuloBlog.created_at.desc())

    # Contar total
    from sqlmodel import func  # noqa: PLC0415
    from sqlalchemy import func as sa_func  # noqa: PLC0415

    total_stmt = select(sa_func.count()).select_from(ArticuloBlog)
    if not mostrar_todos:
        total_stmt = total_stmt.where(ArticuloBlog.publicado == True)  # noqa: E712
    total = db.exec(total_stmt).one()

    # Paginación
    offset = (page - 1) * limit
    stmt = stmt.offset(offset).limit(limit)
    articulos = db.exec(stmt).all()

    return {
        "total": total,
        "page": page,
        "limit": limit,
        "paginas": (total + limit - 1) // limit,
        "articulos": [
            {
                "id": str(a.id),
                "slug": a.slug,
                "titulo_es": a.titulo_es,
                "titulo_en": a.titulo_en,
                "resumen_es": a.resumen_es,
                "resumen_en": a.resumen_en,
                "palabras_clave": a.palabras_clave,
                "meta_descripcion_es": a.meta_descripcion_es,
                "meta_descripcion_en": a.meta_descripcion_en,
                "autor_agente": a.autor_agente,
                "publicado": a.publicado,
                "fecha_publicacion": a.fecha_publicacion.isoformat() if a.fecha_publicacion else None,
                "created_at": a.created_at.isoformat(),
                "updated_at": a.updated_at.isoformat(),
            }
            for a in articulos
        ],
    }


@router.get("/seo/articulos/{slug}", status_code=200)
async def obtener_articulo_por_slug(
    slug: str,
    db: Session = Depends(get_sync_db),
):
    """
    Retorna un artículo de blog por slug. Endpoint público, sin autenticación.
    """
    from app.models.articulo_blog import ArticuloBlog  # noqa: PLC0415

    stmt = select(ArticuloBlog).where(ArticuloBlog.slug == slug)
    articulo = db.exec(stmt).first()

    if not articulo:
        raise HTTPException(status_code=404, detail=f"Artículo con slug '{slug}' no encontrado.")

    return {
        "id": str(articulo.id),
        "slug": articulo.slug,
        "titulo_es": articulo.titulo_es,
        "titulo_en": articulo.titulo_en,
        "contenido_es": articulo.contenido_es,
        "contenido_en": articulo.contenido_en,
        "resumen_es": articulo.resumen_es,
        "resumen_en": articulo.resumen_en,
        "palabras_clave": articulo.palabras_clave,
        "meta_descripcion_es": articulo.meta_descripcion_es,
        "meta_descripcion_en": articulo.meta_descripcion_en,
        "schema_markup": articulo.schema_markup,
        "autor_agente": articulo.autor_agente,
        "publicado": articulo.publicado,
        "fecha_publicacion": articulo.fecha_publicacion.isoformat() if articulo.fecha_publicacion else None,
        "created_at": articulo.created_at.isoformat(),
        "updated_at": articulo.updated_at.isoformat(),
    }


@router.get("/geo/llms.txt", response_class=PlainTextResponse, status_code=200)
async def obtener_llms_txt(
    db: Session = Depends(get_sync_db),
):
    """
    Retorna el contenido llms.txt activo para indexación por LLMs.
    Endpoint público, sin autenticación.
    Media type: text/plain.
    """
    from app.models.geo_contenido import GeoContenido  # noqa: PLC0415

    stmt = (
        select(GeoContenido)
        .where(GeoContenido.tipo == "llms_txt", GeoContenido.activo == True)  # noqa: E712
        .order_by(GeoContenido.version.desc())
    )
    registro = db.exec(stmt).first()

    if not registro:
        # Placeholder si todavía no se ha generado
        placeholder = """\
# Hacienda La Carmelita

Hacienda La Carmelita es una finca de turismo rural premium ubicada en Lérida, Tolima, Colombia.
Ofrece experiencias únicas en contacto con la naturaleza para hasta 18 huéspedes.

Para información actualizada, visita https://haciendalacarmelita.com
o escríbenos al WhatsApp +573001234567.
"""
        return PlainTextResponse(content=placeholder, media_type="text/plain; charset=utf-8")

    return PlainTextResponse(content=registro.contenido, media_type="text/plain; charset=utf-8")


@router.post("/social/generar", status_code=501)
async def generar_posts_social(
    current_user: Usuario = Depends(require_admin),
):
    """Generar posts para redes sociales. Solo Admin. [No implementado aún]"""
    raise HTTPException(
        status_code=501,
        detail="Social Media Agent no implementado todavía. Disponible en un sprint futuro.",
    )

"""
Tests Sprint 8 — Agentes SEO y GEO
Cubre servicios seo_agent, geo_agent y los endpoints HTTP del router /agentes.
Todos los tests corren en sandbox mode (sin API key real, sin Celery).
"""
from __future__ import annotations

import uuid
from datetime import datetime
from unittest.mock import patch

import pytest

# Forzar registro del modelo GeoContenido en SQLModel.metadata
# para que engine_fixture lo incluya en create_all.
from app.models.geo_contenido import GeoContenido  # noqa: F401
from app.models.articulo_blog import ArticuloBlog


# ===========================================================================
# TestSEOAgentService — 4 tests unitarios del servicio seo_agent
# ===========================================================================

class TestSEOAgentService:
    """Pruebas unitarias del servicio seo_agent — modo sandbox (sin API key)."""

    def test_seleccionar_tema_retorna_string(self, db_session):
        """seleccionar_tema_disponible retorna una cadena de al menos 10 caracteres."""
        from app.services import seo_agent

        tema = seo_agent.seleccionar_tema_disponible(db_session)

        assert isinstance(tema, str)
        assert len(tema) > 10

    def test_seleccionar_tema_evita_slugs_ya_publicados(self, db_session):
        """El primer tema con artículo publicado no debe ser reseleccionado."""
        from app.services import seo_agent

        # Tomar el primer tema disponible y guardar un artículo publicado para él
        primer_tema = seo_agent.TEMAS_SEO[0]
        slug_primer_tema = seo_agent._generar_slug(primer_tema)

        articulo = ArticuloBlog(
            id=uuid.uuid4(),
            slug=slug_primer_tema,
            titulo_es=f"[Test] {primer_tema[:80]}",
            contenido_es="Contenido de prueba para evitar reselección.",
            publicado=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db_session.add(articulo)
        db_session.commit()

        # El tema seleccionado debe ser diferente al primer tema publicado
        tema_seleccionado = seo_agent.seleccionar_tema_disponible(db_session)
        slug_seleccionado = seo_agent._generar_slug(tema_seleccionado)

        assert slug_seleccionado != slug_primer_tema

    def test_generar_articulo_sandbox_retorna_campos_requeridos(self, db_session):
        """generar_articulo_seo en modo sandbox retorna todos los campos SEO requeridos."""
        from app.services import seo_agent

        resultado = seo_agent.generar_articulo_seo("turismo rural")

        campos_requeridos = [
            "slug",
            "titulo_es",
            "contenido_es",
            "palabras_clave",
            "meta_descripcion_es",
            "schema_markup",
        ]
        for campo in campos_requeridos:
            assert campo in resultado, f"Campo '{campo}' ausente en el resultado"

        assert isinstance(resultado["palabras_clave"], list)
        assert len(resultado["meta_descripcion_es"]) <= 155

    def test_guardar_articulo_crea_en_bd(self, db_session):
        """guardar_articulo crea un ArticuloBlog en la BD con autor_agente='seo_agent'."""
        from app.services import seo_agent
        from sqlmodel import select

        articulo_data = seo_agent.generar_articulo_seo("tema test")
        articulo = seo_agent.guardar_articulo(articulo_data, db_session, publicado=True)

        # Verificar que el artículo existe en la BD
        stmt = select(ArticuloBlog).where(ArticuloBlog.slug == articulo_data["slug"])
        articulo_en_bd = db_session.exec(stmt).first()

        assert articulo_en_bd is not None
        assert articulo_en_bd.publicado is True
        assert articulo_en_bd.autor_agente == "seo_agent"


# ===========================================================================
# TestGEOAgentService — 3 tests unitarios del servicio geo_agent
# ===========================================================================

class TestGEOAgentService:
    """Pruebas unitarias del servicio geo_agent — modo sandbox (sin API key)."""

    def test_generar_llms_txt_sandbox_retorna_markdown(self, db_session):
        """generar_llms_txt en sandbox retorna markdown que comienza con '# Hacienda La Carmelita'."""
        from app.services import geo_agent

        resultado = geo_agent.generar_llms_txt()

        assert isinstance(resultado, str)
        assert resultado.startswith("# Hacienda La Carmelita")
        # Verificar sección de servicios (con o sin tilde)
        assert ("## Qué ofrecemos" in resultado or "## Que ofrecemos" in resultado)

    def test_generar_faq_jsonld_sandbox_retorna_schema(self, db_session):
        """generar_faq_jsonld en sandbox retorna un dict con estructura FAQPage válida."""
        from app.services import geo_agent

        data = geo_agent.generar_faq_jsonld()

        assert isinstance(data, dict)
        assert data["@type"] == "FAQPage"
        assert "@context" in data
        assert "mainEntity" in data
        assert isinstance(data["mainEntity"], list)

    def test_generar_faq_jsonld_sandbox_tiene_preguntas(self, db_session):
        """generar_faq_jsonld en sandbox retorna al menos 1 pregunta de tipo Question."""
        from app.services import geo_agent

        data = geo_agent.generar_faq_jsonld()

        assert len(data["mainEntity"]) >= 1
        assert data["mainEntity"][0]["@type"] == "Question"


# ===========================================================================
# TestAgentesEndpoints — 6 tests de los endpoints HTTP
# ===========================================================================

class TestAgentesEndpoints:
    """Pruebas de integración de los endpoints HTTP del router /agentes."""

    def test_get_articulos_sin_auth_retorna_200(self, client):
        """GET /agentes/seo/articulos es público y retorna 200 con clave 'articulos'."""
        response = client.get("/agentes/seo/articulos")

        assert response.status_code == 200
        data = response.json()
        assert "articulos" in data
        assert isinstance(data["articulos"], list)

    def test_get_articulos_retorna_solo_publicados(self, client, db_session):
        """GET /agentes/seo/articulos solo incluye artículos con publicado=True."""
        ahora = datetime.utcnow()

        # Artículo publicado
        publicado = ArticuloBlog(
            id=uuid.uuid4(),
            slug="test-articulo-publicado-sprint8",
            titulo_es="Artículo Publicado Sprint 8",
            contenido_es="Contenido publicado.",
            publicado=True,
            fecha_publicacion=ahora,
            created_at=ahora,
            updated_at=ahora,
        )
        # Artículo NO publicado
        no_publicado = ArticuloBlog(
            id=uuid.uuid4(),
            slug="test-articulo-no-publicado-sprint8",
            titulo_es="Artículo No Publicado Sprint 8",
            contenido_es="Contenido no publicado.",
            publicado=False,
            created_at=ahora,
            updated_at=ahora,
        )
        db_session.add(publicado)
        db_session.add(no_publicado)
        db_session.commit()

        response = client.get("/agentes/seo/articulos")
        assert response.status_code == 200
        data = response.json()

        slugs_retornados = [a["slug"] for a in data["articulos"]]
        assert "test-articulo-publicado-sprint8" in slugs_retornados
        assert "test-articulo-no-publicado-sprint8" not in slugs_retornados

    def test_get_articulo_por_slug_no_encontrado_404(self, client):
        """GET /agentes/seo/articulos/{slug} retorna 404 si el slug no existe."""
        response = client.get("/agentes/seo/articulos/slug-que-no-existe-jamás-12345")

        assert response.status_code == 404

    def test_get_articulo_por_slug_encontrado_200(self, client, db_session):
        """GET /agentes/seo/articulos/test-articulo-sprint8 retorna 200 con el slug correcto."""
        ahora = datetime.utcnow()
        articulo = ArticuloBlog(
            id=uuid.uuid4(),
            slug="test-articulo-sprint8",
            titulo_es="Artículo de Prueba Sprint 8",
            contenido_es="Contenido completo del artículo de prueba.",
            publicado=True,
            fecha_publicacion=ahora,
            created_at=ahora,
            updated_at=ahora,
        )
        db_session.add(articulo)
        db_session.commit()

        response = client.get("/agentes/seo/articulos/test-articulo-sprint8")
        assert response.status_code == 200
        data = response.json()
        assert data["slug"] == "test-articulo-sprint8"

    def test_post_seo_generar_sin_auth_retorna_401(self, client):
        """POST /agentes/seo/generar sin token de autenticación retorna 401."""
        response = client.post("/agentes/seo/generar")

        assert response.status_code == 401

    def test_get_llms_txt_retorna_texto_plano(self, client):
        """GET /agentes/geo/llms.txt retorna 200 y contiene 'Carmelita' en el cuerpo."""
        response = client.get("/agentes/geo/llms.txt")

        assert response.status_code == 200
        assert "Carmelita" in response.text


# ===========================================================================
# TestGeneracionAdmin — 1 test de generación con token admin
# ===========================================================================

class TestGeneracionAdmin:
    """Prueba que los endpoints de generación admin retornan 202 en sandbox mode."""

    def test_post_geo_generar_con_admin_retorna_202(self, client, admin_token, engine):
        """POST /agentes/geo/generar con admin token retorna 202 en sandbox mode.

        El endpoint tiene try/except — cuando Celery no está disponible, ejecuta el
        servicio directamente usando _get_sync_engine(). En tests, sustituimos esa
        llamada por el engine SQLite in-memory para evitar la dependencia de psycopg2.
        """
        headers = {"Authorization": f"Bearer {admin_token}"}

        # El fallback del endpoint crea su propia sesión via _get_sync_engine().
        # Parcheamos esa función para que devuelva el engine de test (SQLite in-memory).
        with patch("app.database._get_sync_engine", return_value=engine):
            response = client.post("/agentes/geo/generar", headers=headers)

        assert response.status_code == 202
        data = response.json()
        assert "message" in data

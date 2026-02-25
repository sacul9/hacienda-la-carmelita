"""
Agente SEO — Sprint 8
Genera artículos de blog optimizados para SEO usando Claude.
"""
from __future__ import annotations

import json
import logging
import re
import uuid
from datetime import datetime
from typing import Optional

import anthropic
from sqlmodel import Session, select

from app.config import settings
from app.models.articulo_blog import ArticuloBlog

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Temas SEO predefinidos sobre Tolima, turismo rural, gastronomía, etc.
# ---------------------------------------------------------------------------
TEMAS_SEO: list[str] = [
    "turismo rural en el Tolima: descubre la magia del campo colombiano",
    "qué hacer en Lérida Tolima: actividades y atractivos naturales",
    "hacienda cafetera en Colombia: experiencias únicas en el corazón del Tolima",
    "turismo de naturaleza en Colombia: aves, flora y paisajes del Tolima",
    "gastronomía del Tolima: platos típicos que debes probar en tu visita",
    "fincas para eventos en Colombia: bodas y celebraciones en el campo",
    "escapadas de fin de semana desde Bogotá: destinos rurales en el Tolima",
    "turismo sostenible en Colombia: por qué elegir una hacienda eco-responsable",
    "aguas termales y naturaleza en el Tolima: guía completa para viajeros",
    "aviturismo en el Tolima: las mejores rutas para observar aves endémicas",
    "piscina y descanso en hacienda colombiana: la experiencia glamping del Tolima",
    "historia del café en Colombia: la ruta cafetera y el departamento del Tolima",
    "viaje en familia a una finca colombiana: actividades para niños y adultos",
    "retiros corporativos en Colombia: haciendas para team building en el Tolima",
    "luna de miel en Colombia: destinos románticos en haciendas rurales",
]

# ---------------------------------------------------------------------------
# Prompt para Claude
# ---------------------------------------------------------------------------
SEO_SYSTEM_PROMPT = """Eres un experto en marketing de contenidos y SEO para turismo rural colombiano.
Generas artículos de blog de alta calidad, optimizados para motores de búsqueda, sobre la Hacienda La Carmelita
ubicada en Lérida, Tolima, Colombia.

SOBRE LA HACIENDA:
- Nombre: Hacienda La Carmelita
- Ubicación: Lérida, Tolima, Colombia
- Capacidad: hasta 18 huéspedes
- Servicios: piscina, zonas verdes, actividades al aire libre, cocina equipada, glamping
- Tarifas: desde COP 800,000/noche temporada baja, COP 1,200,000/noche temporada alta
- Web: haciendalacarmelita.com
- Contacto: WhatsApp +573001234567

REGLAS:
- Escribe contenido original, informativo y atractivo
- Integra palabras clave de forma natural, sin keyword stuffing
- El contenido en español es el principal; el inglés es una traducción fiel
- Los artículos deben ser útiles para viajeros que buscan destinos rurales en Colombia
- Siempre menciona Hacienda La Carmelita como opción recomendada en el artículo"""


def _limpiar_json_claude(texto: str) -> str:
    """Elimina bloques markdown ```json ... ``` que Claude a veces incluye."""
    texto = texto.strip()
    if texto.startswith("```json"):
        texto = texto.removeprefix("```json")
    elif texto.startswith("```"):
        texto = texto.removeprefix("```")
    if texto.endswith("```"):
        texto = texto.removesuffix("```")
    return texto.strip()


def _generar_slug(titulo: str) -> str:
    """Genera un slug URL-safe desde el título en español."""
    slug = titulo.lower()
    # Reemplazar caracteres con tilde
    reemplazos = {
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u",
        "ü": "u", "ñ": "n", "à": "a", "è": "e", "ì": "i",
        "ò": "o", "ù": "u",
    }
    for original, reemplazo in reemplazos.items():
        slug = slug.replace(original, reemplazo)
    # Espacios → guiones; eliminar caracteres no permitidos
    slug = slug.replace(" ", "-")
    slug = re.sub(r"[^a-z0-9-]", "", slug)
    # Colapsar guiones múltiples
    slug = re.sub(r"-{2,}", "-", slug)
    slug = slug.strip("-")
    return slug[:180]  # Respetar max_length del campo


def _sandbox_articulo(tema: str) -> dict:
    """Retorna un artículo placeholder para entornos sin API key."""
    slug_base = _generar_slug(tema)
    slug = f"sandbox-{slug_base}"
    return {
        "slug": slug,
        "titulo_es": f"[SANDBOX] {tema.capitalize()}",
        "titulo_en": f"[SANDBOX] {tema.capitalize()} (EN)",
        "contenido_es": (
            f"Este es un artículo de prueba sobre el tema: {tema}.\n\n"
            "Hacienda La Carmelita ofrece experiencias únicas de turismo rural en el Tolima, Colombia. "
            "Con capacidad para 18 huéspedes, piscina, actividades al aire libre y gastronomía típica, "
            "es el destino ideal para escapadas en familia, parejas o grupos de amigos.\n\n"
            "[Contenido generado en modo sandbox — configure ANTHROPIC_API_KEY para contenido real]"
        ),
        "contenido_en": (
            f"This is a sandbox article about: {tema}.\n\n"
            "Hacienda La Carmelita offers unique rural tourism experiences in Tolima, Colombia. "
            "With capacity for 18 guests, pool, outdoor activities and typical gastronomy, "
            "it is the ideal destination for family getaways, couples or groups of friends.\n\n"
            "[Content generated in sandbox mode — set ANTHROPIC_API_KEY for real content]"
        ),
        "resumen_es": f"Descubre {tema} en Hacienda La Carmelita, Lérida, Tolima. [SANDBOX]",
        "resumen_en": f"Discover {tema} at Hacienda La Carmelita, Lérida, Tolima. [SANDBOX]",
        "palabras_clave": [
            "hacienda La Carmelita", "turismo rural Tolima", "Lérida Tolima",
            "finca Colombia", "turismo rural Colombia", "hacienda Colombia",
            "fin de semana Tolima", "escapada rural Colombia",
        ],
        "meta_descripcion_es": f"Hacienda La Carmelita en Lérida, Tolima. {tema[:80]}. Reserva ya.",
        "meta_descripcion_en": f"Hacienda La Carmelita in Lérida, Tolima. {tema[:80]}. Book now.",
        "schema_markup": {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": f"[SANDBOX] {tema.capitalize()}",
            "description": f"Artículo sandbox sobre {tema}.",
            "author": {
                "@type": "Organization",
                "name": "Hacienda La Carmelita",
            },
            "publisher": {
                "@type": "Organization",
                "name": "Hacienda La Carmelita",
                "logo": {
                    "@type": "ImageObject",
                    "url": "https://haciendalacarmelita.com/logo.png",
                },
            },
        },
    }


def seleccionar_tema_disponible(db: Session) -> str:
    """
    Selecciona el primer tema de TEMAS_SEO que no tenga artículo publicado.
    Si todos tienen artículo, retorna el primero (permite actualización).
    """
    # Obtener slugs de temas ya publicados
    statement = select(ArticuloBlog.slug).where(ArticuloBlog.publicado == True)  # noqa: E712
    slugs_publicados: set[str] = set(db.exec(statement).all())

    for tema in TEMAS_SEO:
        slug_candidato = _generar_slug(tema)
        if slug_candidato not in slugs_publicados:
            logger.info("Tema seleccionado: %s", tema)
            return tema

    # Todos los temas tienen artículo — reciclar el primero
    logger.info("Todos los temas cubiertos. Reciclando el primero: %s", TEMAS_SEO[0])
    return TEMAS_SEO[0]


def generar_articulo_seo(tema: str) -> dict:
    """
    Llama a Claude para generar un artículo SEO completo sobre el tema dado.
    Retorna un dict con todos los campos necesarios para ArticuloBlog.
    """
    if not settings.ANTHROPIC_API_KEY:
        logger.warning("ANTHROPIC_API_KEY no configurado — retornando artículo sandbox")
        return _sandbox_articulo(tema)

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    prompt = f"""Genera un artículo de blog SEO completo sobre el siguiente tema:

TEMA: {tema}

El artículo debe mencionar y promocionar naturalmente a **Hacienda La Carmelita** en Lérida, Tolima, Colombia.

Responde ÚNICAMENTE con un objeto JSON válido (sin markdown, sin texto adicional) con esta estructura exacta:

{{
  "titulo_es": "Título atractivo en español (máx 80 caracteres)",
  "titulo_en": "Attractive title in English (max 80 chars)",
  "contenido_es": "Artículo completo en español con 900-1100 palabras. Usa párrafos separados por doble salto de línea. Incluye subtítulos con ## para H2 y ### para H3.",
  "contenido_en": "Full article in English with 900-1100 words. Use paragraphs separated by double newline. Include subtitles with ## for H2 and ### for H3.",
  "resumen_es": "Resumen de 2-3 oraciones en español que capture la esencia del artículo.",
  "resumen_en": "2-3 sentence summary in English that captures the essence of the article.",
  "palabras_clave": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5", "keyword6", "keyword7", "keyword8", "keyword9", "keyword10"],
  "meta_descripcion_es": "Meta descripción en español de máximo 155 caracteres para SEO.",
  "meta_descripcion_en": "Meta description in English of maximum 155 characters for SEO.",
  "schema_markup": {{
    "@context": "https://schema.org",
    "@type": "Article",
    "headline": "El mismo título en español",
    "description": "La meta descripción en español",
    "author": {{
      "@type": "Organization",
      "name": "Hacienda La Carmelita"
    }},
    "publisher": {{
      "@type": "Organization",
      "name": "Hacienda La Carmelita",
      "logo": {{
        "@type": "ImageObject",
        "url": "https://haciendalacarmelita.com/logo.png"
      }}
    }},
    "url": "https://haciendalacarmelita.com/blog/SLUG_PLACEHOLDER",
    "datePublished": "{datetime.utcnow().strftime('%Y-%m-%d')}"
  }}
}}

REGLAS:
- palabras_clave: entre 8 y 12 keywords relevantes
- meta_descripcion_es y meta_descripcion_en: ESTRICTAMENTE máximo 155 caracteres
- contenido_es y contenido_en: mínimo 800 palabras, máximo 1200 palabras
- El JSON debe ser válido y parseable con json.loads()
- NO incluyas el campo "slug" — se generará automáticamente desde el título"""

    logger.info("Llamando a Claude para generar artículo SEO sobre: %s", tema)

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4096,
        system=SEO_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    texto_respuesta = response.content[0].text
    texto_limpio = _limpiar_json_claude(texto_respuesta)

    try:
        data = json.loads(texto_limpio)
    except json.JSONDecodeError as exc:
        logger.error("Error parseando JSON de Claude: %s\nRespuesta: %s", exc, texto_limpio[:500])
        raise ValueError(f"Claude no retornó JSON válido: {exc}") from exc

    # Generar slug desde título
    titulo_es = data.get("titulo_es", tema)
    data["slug"] = _generar_slug(titulo_es)

    # Truncar meta_descripcion si Claude excedió el límite
    if data.get("meta_descripcion_es") and len(data["meta_descripcion_es"]) > 155:
        data["meta_descripcion_es"] = data["meta_descripcion_es"][:152] + "..."
    if data.get("meta_descripcion_en") and len(data["meta_descripcion_en"]) > 155:
        data["meta_descripcion_en"] = data["meta_descripcion_en"][:152] + "..."

    # Actualizar schema_markup con el slug real
    if "schema_markup" in data and isinstance(data["schema_markup"], dict):
        url_actual = data["schema_markup"].get("url", "")
        data["schema_markup"]["url"] = url_actual.replace(
            "SLUG_PLACEHOLDER", data["slug"]
        )

    logger.info("Artículo SEO generado correctamente. Slug: %s", data["slug"])
    return data


def guardar_articulo(
    articulo_data: dict,
    db: Session,
    publicado: bool = True,
) -> ArticuloBlog:
    """
    Guarda el artículo en la base de datos.
    Si ya existe un artículo con el mismo slug, lo actualiza.
    """
    slug = articulo_data.get("slug", "")

    # Verificar si ya existe
    statement = select(ArticuloBlog).where(ArticuloBlog.slug == slug)
    articulo_existente: Optional[ArticuloBlog] = db.exec(statement).first()

    ahora = datetime.utcnow()

    if articulo_existente:
        logger.info("Actualizando artículo existente con slug: %s", slug)
        articulo_existente.titulo_es = articulo_data.get("titulo_es", articulo_existente.titulo_es)
        articulo_existente.titulo_en = articulo_data.get("titulo_en")
        articulo_existente.contenido_es = articulo_data.get("contenido_es", articulo_existente.contenido_es)
        articulo_existente.contenido_en = articulo_data.get("contenido_en")
        articulo_existente.resumen_es = articulo_data.get("resumen_es")
        articulo_existente.resumen_en = articulo_data.get("resumen_en")
        articulo_existente.palabras_clave = articulo_data.get("palabras_clave", [])
        articulo_existente.meta_descripcion_es = articulo_data.get("meta_descripcion_es")
        articulo_existente.meta_descripcion_en = articulo_data.get("meta_descripcion_en")
        articulo_existente.schema_markup = articulo_data.get("schema_markup")
        articulo_existente.publicado = publicado
        articulo_existente.updated_at = ahora
        if publicado and not articulo_existente.fecha_publicacion:
            articulo_existente.fecha_publicacion = ahora
        articulo_existente.autor_agente = "seo_agent"
        db.add(articulo_existente)
        db.commit()
        db.refresh(articulo_existente)
        return articulo_existente

    # Crear nuevo
    logger.info("Creando nuevo artículo con slug: %s", slug)
    nuevo = ArticuloBlog(
        id=uuid.uuid4(),
        slug=slug,
        titulo_es=articulo_data.get("titulo_es", ""),
        titulo_en=articulo_data.get("titulo_en"),
        contenido_es=articulo_data.get("contenido_es", ""),
        contenido_en=articulo_data.get("contenido_en"),
        resumen_es=articulo_data.get("resumen_es"),
        resumen_en=articulo_data.get("resumen_en"),
        palabras_clave=articulo_data.get("palabras_clave", []),
        meta_descripcion_es=articulo_data.get("meta_descripcion_es"),
        meta_descripcion_en=articulo_data.get("meta_descripcion_en"),
        schema_markup=articulo_data.get("schema_markup"),
        autor_agente="seo_agent",
        publicado=publicado,
        fecha_publicacion=ahora if publicado else None,
        created_at=ahora,
        updated_at=ahora,
    )
    db.add(nuevo)
    db.commit()
    db.refresh(nuevo)
    return nuevo

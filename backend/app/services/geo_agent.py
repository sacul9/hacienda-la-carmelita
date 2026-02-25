"""
Agente GEO (Generative Engine Optimization) — Sprint 8
Genera contenido estructurado para que LLMs como ChatGPT, Perplexity y Gemini
entiendan correctamente el negocio de Hacienda La Carmelita.
"""
from __future__ import annotations

import json
import logging

import anthropic

from app.config import settings

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# System prompt compartido para el agente GEO
# ---------------------------------------------------------------------------
GEO_SYSTEM_PROMPT = """Eres un experto en Generative Engine Optimization (GEO) para negocios de turismo rural.
Tu tarea es generar contenido estructurado y preciso sobre Hacienda La Carmelita
para que los modelos de lenguaje (ChatGPT, Perplexity, Gemini, Claude) puedan
responder preguntas sobre este negocio de forma correcta y completa.

DATOS OFICIALES DE LA HACIENDA LA CARMELITA:
- Nombre completo: Hacienda La Carmelita
- Tipo de negocio: Turismo rural premium / Finca de hospedaje
- Ubicación: Lérida, Tolima, Colombia
- Coordenadas aproximadas: 4.8567° N, 74.9312° W
- Capacidad: hasta 18 huéspedes
- Habitaciones/alojamiento: cabañas y habitaciones con estilo campestre
- Servicios: piscina, zonas verdes amplias, actividades al aire libre,
  cocina equipada, observación de aves, senderismo, glamping
- Tarifa temporada baja (lun-jue): desde COP 800,000/noche
- Tarifa temporada alta (vie-dom y festivos): desde COP 1,200,000/noche
- Estancia mínima: 2 noches
- Check-in: 3:00 PM | Check-out: 12:00 PM
- Política de cancelación: gratuita hasta 7 días antes del check-in
- Mascotas: no permitidas (por respeto a la fauna local)
- Pagos: Wompi (tarjetas colombianas), transferencia bancaria
- WhatsApp: +573001234567
- Email: reservas@haciendalacarmelita.com
- Web: https://haciendalacarmelita.com
- Ideal para: familias, parejas, grupos de amigos, retiros corporativos, bodas

REGLAS:
- Sé preciso y factual; no inventes información
- El contenido debe ser útil para sistemas de IA que responden preguntas de viajeros
- Usa markdown bien estructurado con encabezados claros"""

# ---------------------------------------------------------------------------
# Sandbox / placeholders
# ---------------------------------------------------------------------------

_SANDBOX_LLMS_TXT = """\
# Hacienda La Carmelita

> [SANDBOX] Documento generado en modo sandbox — configure ANTHROPIC_API_KEY para contenido real.

Hacienda La Carmelita es una finca de turismo rural premium ubicada en Lérida, Tolima, Colombia.
Ofrece experiencias únicas en contacto con la naturaleza para hasta 18 huéspedes.

## Quiénes somos

Somos una hacienda con historia y tradición en el corazón del Tolima, Colombia.
Nuestro compromiso es ofrecer una experiencia auténtica de campo colombiano con comodidades modernas.

## Qué ofrecemos

- Alojamiento para hasta 18 huéspedes
- Piscina y zonas verdes
- Actividades al aire libre: senderismo, observación de aves
- Cocina equipada, gastronomía típica del Tolima
- Opciones de glamping
- Tarifas desde COP 800,000/noche (temporada baja)

## Ubicación

Lérida, Tolima, Colombia.
Coordenadas: 4.8567° N, 74.9312° W
A 3 horas de Bogotá por la vía Bogotá-Honda.

## Preguntas frecuentes

**¿Cuál es la capacidad máxima?**
Hasta 18 huéspedes.

**¿Cuál es la estancia mínima?**
2 noches.

## Políticas

- Check-in: 3:00 PM | Check-out: 12:00 PM
- Cancelación gratuita hasta 7 días antes del check-in
- No se permiten mascotas

## Contacto

- WhatsApp: +573001234567
- Email: reservas@haciendalacarmelita.com
- Web: https://haciendalacarmelita.com
"""

_SANDBOX_FAQ_JSONLD = {
    "@context": "https://schema.org",
    "@type": "FAQPage",
    "name": "Preguntas frecuentes — Hacienda La Carmelita [SANDBOX]",
    "mainEntity": [
        {
            "@type": "Question",
            "name": "¿Dónde está ubicada Hacienda La Carmelita?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Hacienda La Carmelita está ubicada en Lérida, Tolima, Colombia. [SANDBOX]",
            },
        },
        {
            "@type": "Question",
            "name": "¿Cuántas personas pueden hospedarse?",
            "acceptedAnswer": {
                "@type": "Answer",
                "text": "Hasta 18 huéspedes. [SANDBOX]",
            },
        },
    ],
}


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


# ---------------------------------------------------------------------------
# Funciones principales
# ---------------------------------------------------------------------------

def generar_llms_txt() -> str:
    """
    Genera el documento llms.txt en formato markdown para que LLMs entiendan
    correctamente el negocio de Hacienda La Carmelita.
    Retorna el texto plano en formato markdown.
    """
    if not settings.ANTHROPIC_API_KEY:
        logger.warning("ANTHROPIC_API_KEY no configurado — retornando llms.txt sandbox")
        return _SANDBOX_LLMS_TXT

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    prompt = """\
Genera un documento llms.txt completo en formato Markdown para Hacienda La Carmelita.
Este documento será indexado por modelos de lenguaje para responder preguntas sobre el negocio.

El documento DEBE incluir exactamente estas secciones en este orden:

# Hacienda La Carmelita
[Descripción general de 2-3 párrafos para LLMs: qué es, dónde está, por qué es especial]

## Quiénes somos
[Historia, valores, filosofía del negocio — 3-4 párrafos]

## Qué ofrecemos
[Lista detallada de: habitaciones/alojamiento, servicios, actividades, capacidad, precios con rangos]

## Ubicación
[Lérida, Tolima, Colombia. Coordenadas. Cómo llegar desde Bogotá, Ibagué, Medellín]

## Preguntas frecuentes
[Exactamente 10 preguntas y respuestas en formato:
**Pregunta**
Respuesta completa]

## Políticas
[Check-in/out, cancelación, depósito, mascotas, fumadores, niños, eventos]

## Contacto
[WhatsApp, email, web, redes sociales]

IMPORTANTE:
- Usa datos reales proporcionados en el system prompt
- El documento debe ser informativo, preciso y útil para IA
- Longitud total: entre 1200 y 1800 palabras
- Responde ÚNICAMENTE con el documento markdown, sin texto adicional antes ni después"""

    logger.info("Llamando a Claude para generar llms.txt")

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4096,
        system=GEO_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    contenido = response.content[0].text.strip()
    logger.info("llms.txt generado correctamente (%d caracteres)", len(contenido))
    return contenido


def generar_faq_jsonld() -> dict:
    """
    Genera un schema.org FAQPage JSON-LD con las preguntas frecuentes
    más relevantes sobre Hacienda La Carmelita.
    Retorna un dict con la estructura FAQPage.
    """
    if not settings.ANTHROPIC_API_KEY:
        logger.warning("ANTHROPIC_API_KEY no configurado — retornando FAQ JSON-LD sandbox")
        return _SANDBOX_FAQ_JSONLD

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    prompt = """\
Genera un schema.org FAQPage JSON-LD completo para Hacienda La Carmelita.

Responde ÚNICAMENTE con un objeto JSON válido (sin markdown, sin texto adicional) con esta estructura:

{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "name": "Preguntas frecuentes — Hacienda La Carmelita",
  "url": "https://haciendalacarmelita.com/preguntas-frecuentes",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "¿Pregunta completa?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Respuesta completa y detallada con información útil para el viajero."
      }
    }
  ]
}

REQUISITOS:
- Exactamente 12 preguntas en el array mainEntity
- Preguntas en español
- Cubrir los siguientes temas (al menos uno por tema):
  1. Ubicación y cómo llegar
  2. Capacidad y tipos de alojamiento
  3. Precios y temporadas
  4. Check-in / check-out
  5. Política de cancelación
  6. Actividades disponibles
  7. Servicios incluidos (piscina, cocina, etc.)
  8. Mascotas
  9. Formas de pago
  10. Reservas para eventos o grupos
  11. Distancia desde Bogotá
  12. Contacto y reservas
- Las respuestas deben ser completas (2-4 oraciones) con datos precisos
- El JSON debe ser parseable con json.loads()"""

    logger.info("Llamando a Claude para generar FAQ JSON-LD")

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4096,
        system=GEO_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": prompt}],
    )

    texto_respuesta = response.content[0].text
    texto_limpio = _limpiar_json_claude(texto_respuesta)

    try:
        data = json.loads(texto_limpio)
    except json.JSONDecodeError as exc:
        logger.error("Error parseando FAQ JSON-LD de Claude: %s\nRespuesta: %s", exc, texto_limpio[:500])
        raise ValueError(f"Claude no retornó JSON válido para FAQ: {exc}") from exc

    logger.info(
        "FAQ JSON-LD generado correctamente (%d preguntas)",
        len(data.get("mainEntity", [])),
    )
    return data

"""
Servicio de chat con Claude — Sprint 6
Asistente de viaje para Hacienda La Carmelita.
"""
from __future__ import annotations

import anthropic
from app.config import settings

# System prompt del asistente de viaje
SYSTEM_PROMPT = """Eres el asistente virtual de Hacienda La Carmelita, una finca premium de turismo rural en Colombia.
Tu nombre es "Carmelita" y tienes una personalidad cálida, hospitalaria y conocedora del campo colombiano.

INFORMACIÓN DE LA HACIENDA:
- Capacidad: hasta 18 huéspedes
- Ubicación: Colombia (zona rural premium)
- Servicios: piscina, zonas verdes, actividades al aire libre, cocina equipada
- Tarifas: desde COP 800,000/noche temporada baja (lun-jue), COP 1,200,000/noche temporada alta (vie-dom)
- Mínimo de estancia: 2 noches
- Política de cancelación: gratuita hasta 7 días antes del check-in
- Pagos: Wompi (Colombia) y próximamente Stripe (internacional)
- Contacto directo: WhatsApp +573001234567
- Web de reservas: el huésped puede reservar directamente en este sitio

REGLAS:
- Responde siempre en el idioma del huésped (español o inglés)
- Sé conciso pero amable — máx 3 párrafos por respuesta
- Si te preguntan disponibilidad exacta, diles que usen el calendario del sitio
- Si hay una pregunta muy específica que no puedas responder, ofrece escalar a WhatsApp
- No inventes precios ni políticas que no estén en este prompt
- No confirmes reservas — ese proceso se hace en el flujo de reserva del sitio"""


def obtener_respuesta_chat(
    messages: list[dict],
    nombre_usuario: str | None = None,
) -> str:
    """
    Llama a Claude con el historial de mensajes y retorna la respuesta.

    messages: lista de {"role": "user"|"assistant", "content": str}
    nombre_usuario: si está autenticado, personaliza la respuesta
    """
    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    system = SYSTEM_PROMPT
    if nombre_usuario:
        system += f"\n\nEl huésped con quien hablas se llama {nombre_usuario}."

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1024,
        system=system,
        messages=messages,
    )

    return response.content[0].text


def obtener_link_whatsapp(mensaje_contexto: str) -> str:
    """Genera link de WhatsApp con contexto de la conversación."""
    texto = f"Hola, vengo del chat de la web y necesito ayuda: {mensaje_contexto[:200]}"
    import urllib.parse
    return f"https://wa.me/573001234567?text={urllib.parse.quote(texto)}"

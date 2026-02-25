"""
Router de chat IA — Sprint 6
Asistente virtual "Carmelita" para huéspedes.
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from app.auth.dependencies import get_current_user_optional
from app.models.usuario import Usuario
from app.services.claude_chat import obtener_respuesta_chat, obtener_link_whatsapp

router = APIRouter()


class MensajeRequest(BaseModel):
    mensaje: str
    historial: List[dict] = []  # Lista de {"role": "user"|"assistant", "content": str}


class MensajeResponse(BaseModel):
    respuesta: str
    whatsapp_url: Optional[str] = None


@router.post("/mensaje", response_model=MensajeResponse)
async def enviar_mensaje(
    data: MensajeRequest,
    current_user: Optional[Usuario] = Depends(get_current_user_optional),
):
    """Enviar mensaje al asistente IA. Retorna respuesta de Claude."""
    if not data.mensaje.strip():
        raise HTTPException(status_code=422, detail="El mensaje no puede estar vacío")

    if len(data.mensaje) > 2000:
        raise HTTPException(status_code=422, detail="Mensaje demasiado largo (máx 2000 caracteres)")

    # Construir historial + nuevo mensaje
    messages = list(data.historial[-10:])  # máx últimos 10 intercambios
    messages.append({"role": "user", "content": data.mensaje})

    nombre = None
    if current_user:
        nombre = f"{current_user.nombre} {current_user.apellido}".strip()

    try:
        respuesta = obtener_respuesta_chat(messages, nombre_usuario=nombre)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Error del servicio de IA: {str(e)}")

    return MensajeResponse(respuesta=respuesta)


@router.get("/{session_id}/historial")
async def historial_chat(
    session_id: str,
    current_user: Optional[Usuario] = Depends(get_current_user_optional),
):
    """
    El historial se gestiona en el frontend (localStorage).
    Este endpoint está disponible para futuras integraciones.
    """
    return {"session_id": session_id, "historial": [], "nota": "Historial gestionado en cliente"}


@router.post("/escalar-whatsapp")
async def escalar_whatsapp(
    data: MensajeRequest,
    current_user: Optional[Usuario] = Depends(get_current_user_optional),
):
    """Genera link de WhatsApp para escalar a humano."""
    url = obtener_link_whatsapp(data.mensaje)
    return {"whatsapp_url": url}

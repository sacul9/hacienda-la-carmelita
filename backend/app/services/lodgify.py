"""
Servicio de integración con Lodgify API.
Documentación: https://docs.lodgify.com/

Si LODGIFY_API_KEY está vacío, todas las funciones retornan datos de prueba
(igual que Wompi/Stripe en modo sandbox).
"""
import httpx
import logging
from datetime import date, datetime
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)
LODGIFY_BASE = "https://api.lodgify.com/v2"

# ── helpers ──────────────────────────────────────────────────────────────────

def _headers() -> dict:
    return {"X-ApiKey": settings.LODGIFY_API_KEY, "accept": "application/json"}

def _sandbox_mode() -> bool:
    return not settings.LODGIFY_API_KEY

# ── funciones principales ─────────────────────────────────────────────────────

def pull_reservas_lodgify(desde: Optional[date] = None, hasta: Optional[date] = None) -> list[dict]:
    """
    Obtiene reservas de Lodgify (que vienen de Airbnb/Booking.com).
    Retorna lista de dicts con estructura normalizada.
    En sandbox retorna 2 reservas de prueba.
    """
    if _sandbox_mode():
        logger.info("[Lodgify SANDBOX] pull_reservas_lodgify: retornando datos de prueba")
        return _sandbox_reservas()

    params = {}
    if desde:
        params["dateFrom"] = desde.isoformat()
    if hasta:
        params["dateTo"] = hasta.isoformat()

    try:
        resp = httpx.get(f"{LODGIFY_BASE}/reservations", headers=_headers(), params=params, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        return [_normalizar_reserva_lodgify(r) for r in data.get("items", [])]
    except Exception as e:
        logger.error(f"[Lodgify] Error al obtener reservas: {e}")
        return []


def push_bloqueo_lodgify(fecha_inicio: date, fecha_fin: date, motivo: str = "Reserva directa") -> bool:
    """
    Bloquea fechas en Lodgify (se propaga a Airbnb y Booking.com).
    En sandbox simula éxito.
    """
    if _sandbox_mode():
        logger.info(f"[Lodgify SANDBOX] push_bloqueo: {fecha_inicio} → {fecha_fin}")
        return True

    try:
        payload = {
            "dateFrom": fecha_inicio.isoformat(),
            "dateTo": fecha_fin.isoformat(),
            "name": motivo,
        }
        resp = httpx.post(f"{LODGIFY_BASE}/availability/block", headers=_headers(), json=payload, timeout=15)
        resp.raise_for_status()
        logger.info(f"[Lodgify] Bloqueo creado: {fecha_inicio} → {fecha_fin}")
        return True
    except Exception as e:
        logger.error(f"[Lodgify] Error al crear bloqueo: {e}")
        return False


def push_precio_lodgify(fecha: date, precio_cop: float) -> bool:
    """
    Actualiza precio en Lodgify para una fecha específica.
    En sandbox simula éxito.
    """
    if _sandbox_mode():
        logger.info(f"[Lodgify SANDBOX] push_precio: {fecha} = COP {precio_cop}")
        return True

    try:
        payload = {"date": fecha.isoformat(), "price": precio_cop}
        resp = httpx.post(f"{LODGIFY_BASE}/rates/prices", headers=_headers(), json=payload, timeout=15)
        resp.raise_for_status()
        return True
    except Exception as e:
        logger.error(f"[Lodgify] Error al actualizar precio: {e}")
        return False


def parsear_reserva_lodgify(raw: dict) -> dict:
    """Alias público para normalizar una reserva cruda de Lodgify."""
    return _normalizar_reserva_lodgify(raw)


# ── helpers internos ──────────────────────────────────────────────────────────

def _normalizar_reserva_lodgify(raw: dict) -> dict:
    """
    Convierte la estructura de Lodgify a la estructura interna:
    {canal, canal_reserva_id, fecha_checkin, fecha_checkout, huespedes,
     nombre_huesped, email_huesped, telefono_huesped, precio_total, moneda, estado}
    """
    source = raw.get("source", "").lower()
    canal = "airbnb" if "airbnb" in source else ("booking" if "booking" in source else "ota")

    return {
        "canal": canal,
        "canal_reserva_id": str(raw.get("id", "")),
        "fecha_checkin": raw.get("arrival", ""),
        "fecha_checkout": raw.get("departure", ""),
        "huespedes": raw.get("people", 1),
        "nombre_huesped": raw.get("guestName", "Huésped OTA"),
        "email_huesped": raw.get("guestEmail", ""),
        "telefono_huesped": raw.get("guestPhone", ""),
        "precio_total": float(raw.get("totalPrice", 0)),
        "moneda": raw.get("currency", "COP"),
        "estado": "confirmada",
        "notas_internas": f"Importada desde Lodgify ({canal}). ID externo: {raw.get('id', 'N/A')}",
    }


def _sandbox_reservas() -> list[dict]:
    """2 reservas de prueba para desarrollo sin API key real."""
    return [
        {
            "canal": "airbnb",
            "canal_reserva_id": "SANDBOX-AIR-001",
            "fecha_checkin": "2026-03-14",
            "fecha_checkout": "2026-03-16",
            "huespedes": 4,
            "nombre_huesped": "Carlos Sandbox Airbnb",
            "email_huesped": "sandbox.airbnb@example.com",
            "telefono_huesped": "+573001111111",
            "precio_total": 1600000.0,
            "moneda": "COP",
            "estado": "confirmada",
            "notas_internas": "Reserva de prueba SANDBOX — Airbnb",
        },
        {
            "canal": "booking",
            "canal_reserva_id": "SANDBOX-BKG-001",
            "fecha_checkin": "2026-03-21",
            "fecha_checkout": "2026-03-23",
            "huespedes": 2,
            "nombre_huesped": "María Sandbox Booking",
            "email_huesped": "sandbox.booking@example.com",
            "telefono_huesped": "+573002222222",
            "precio_total": 2400000.0,
            "moneda": "COP",
            "estado": "confirmada",
            "notas_internas": "Reserva de prueba SANDBOX — Booking.com",
        },
    ]

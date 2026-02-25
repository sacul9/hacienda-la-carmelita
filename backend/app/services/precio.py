"""
Servicio de cálculo de precios — Sprint 6.
Lee tarifas desde la DB si están disponibles, fallback a hardcoded.
"""
from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal
from typing import Optional

from sqlmodel import Session, select

# ─── Tarifas fallback (si la DB no tiene datos) ──────────────────────────────
TARIFA_BAJA_DEFAULT = Decimal("800000")    # Lun–Jue
TARIFA_ALTA_DEFAULT = Decimal("1200000")   # Vie–Sáb–Dom
TASA_USD = Decimal("4200")
NOCHES_MINIMAS = 2

# Mantener las variables originales como alias para compatibilidad
TARIFA_BAJA = TARIFA_BAJA_DEFAULT
TARIFA_ALTA = TARIFA_ALTA_DEFAULT


def es_temporada_alta(d: date) -> bool:
    """Viernes(4), Sábado(5), Domingo(6) → temporada alta."""
    return d.weekday() >= 4


def obtener_tarifas(db: Optional[Session] = None) -> tuple[Decimal, Decimal]:
    """
    Retorna (tarifa_baja, tarifa_alta) desde la DB o los defaults.
    """
    if db is None:
        return TARIFA_BAJA_DEFAULT, TARIFA_ALTA_DEFAULT

    try:
        from app.models.tarifa import Tarifa
        baja_row = db.exec(select(Tarifa).where(Tarifa.temporada == "baja", Tarifa.activo == True)).first()
        alta_row = db.exec(select(Tarifa).where(Tarifa.temporada == "alta", Tarifa.activo == True)).first()

        tarifa_baja = baja_row.tarifa_cop if baja_row else TARIFA_BAJA_DEFAULT
        tarifa_alta = alta_row.tarifa_cop if alta_row else TARIFA_ALTA_DEFAULT
        return tarifa_baja, tarifa_alta
    except Exception:
        return TARIFA_BAJA_DEFAULT, TARIFA_ALTA_DEFAULT


def calcular_precio(
    fecha_checkin: date,
    fecha_checkout: date,
    addon_ids: Optional[list] = None,
    db: Optional[Session] = None,
) -> dict:
    """
    Calcula el precio total de la estancia noche a noche.
    Lee tarifas desde la DB si se proporciona una sesión.
    """
    if addon_ids is None:
        addon_ids = []

    noches = (fecha_checkout - fecha_checkin).days
    if noches < NOCHES_MINIMAS:
        raise ValueError(f"Mínimo {NOCHES_MINIMAS} noches de estancia.")

    tarifa_baja, tarifa_alta = obtener_tarifas(db)

    desglose = []
    precio_base = Decimal("0")

    for i in range(noches):
        noche = fecha_checkin + timedelta(days=i)
        es_alta = es_temporada_alta(noche)
        tarifa = tarifa_alta if es_alta else tarifa_baja
        precio_base += tarifa
        desglose.append({
            "concepto": (
                f"Noche {noche.isoformat()} "
                f"({'Temporada Alta' if es_alta else 'Temporada Baja'})"
            ),
            "monto": float(tarifa),
        })

    addons_cop = Decimal("0")
    total_cop = precio_base + addons_cop
    total_usd = (total_cop / TASA_USD).quantize(Decimal("0.01"))

    return {
        "noches": noches,
        "precio_base_cop": precio_base,
        "addons_cop": addons_cop,
        "total_cop": total_cop,
        "total_usd": total_usd,
        "desglose": desglose,
    }

# Sprint 7: Agente de sincronización con OTAs (Airbnb + Booking via Lodgify)
# TODO: Implementar en Sprint 7


async def pull_reservas_otas():
    """Obtiene nuevas reservas de OTAs cada 15 minutos."""
    raise NotImplementedError("TODO: Sprint 7")


async def push_disponibilidad(fecha_inicio, fecha_fin, disponible: bool):
    """Propaga cambios de disponibilidad a Airbnb y Booking."""
    raise NotImplementedError("TODO: Sprint 7")


async def push_precios(precios: dict):
    """Propaga cambios de precios a todos los canales."""
    raise NotImplementedError("TODO: Sprint 7")

"""
Tareas Celery para sincronización con OTAs vía Lodgify.

Celery beat schedule (ya configurado en celery_app.py):
  - sincronizar_ota: cada 15 minutos
"""
import logging
import time
import uuid
from datetime import date, datetime, timedelta
from sqlmodel import Session, select

from app.database import _get_sync_engine
from app.models.reserva import Reserva
from app.models.bloqueo_calendario import BloqueoCalendario
from app.models.sync_log import SyncLog
from app.services import lodgify as lodgify_svc
from workers.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="sincronizacion.sincronizar_ota", bind=True, max_retries=3)
def sincronizar_ota(self, iniciado_por: str = "celery_beat"):
    """
    Tarea principal: pull de Lodgify → importar reservas nuevas → detectar conflictos.
    Se ejecuta cada 15 minutos según el beat schedule.
    """
    inicio = time.monotonic()
    engine = _get_sync_engine()

    with Session(engine) as db:
        # Crear log inicial
        sync_log = SyncLog(
            canal="lodgify",
            estado="en_progreso",
            iniciado_por=iniciado_por,
        )
        db.add(sync_log)
        db.commit()
        db.refresh(sync_log)

        importadas = 0
        ya_existian = 0
        conflictos = 0

        try:
            # Pull desde Lodgify (últimos 90 días hacia adelante)
            desde = date.today() - timedelta(days=7)
            hasta = date.today() + timedelta(days=90)
            reservas_ota = lodgify_svc.pull_reservas_lodgify(desde=desde, hasta=hasta)

            for r_data in reservas_ota:
                resultado = importar_reserva_ota(r_data, db)
                if resultado == "importada":
                    importadas += 1
                elif resultado == "ya_existia":
                    ya_existian += 1
                elif resultado == "conflicto":
                    conflictos += 1
                    notificar_conflicto_doble_reserva.delay(r_data)

            # Actualizar log con éxito
            sync_log.estado = "ok"
            sync_log.reservas_importadas = importadas
            sync_log.reservas_ya_existian = ya_existian
            sync_log.conflictos_detectados = conflictos
            sync_log.duracion_ms = int((time.monotonic() - inicio) * 1000)
            db.add(sync_log)
            db.commit()

            logger.info(
                f"[Sync OTA] OK — importadas={importadas}, ya_existian={ya_existian}, "
                f"conflictos={conflictos}, duración={sync_log.duracion_ms}ms"
            )
            return {"status": "ok", "importadas": importadas, "conflictos": conflictos}

        except Exception as e:
            logger.error(f"[Sync OTA] Error: {e}", exc_info=True)
            sync_log.estado = "error"
            sync_log.mensaje_error = str(e)[:500]
            sync_log.duracion_ms = int((time.monotonic() - inicio) * 1000)
            db.add(sync_log)
            db.commit()
            raise self.retry(exc=e, countdown=60)


def importar_reserva_ota(r_data: dict, db: Session) -> str:
    """
    Importa una reserva desde datos normalizados de Lodgify.
    Retorna: 'importada' | 'ya_existia' | 'conflicto'
    """
    canal_reserva_id = r_data.get("canal_reserva_id", "")

    # 1. Verificar si ya existe (idempotente)
    existente = db.exec(
        select(Reserva).where(Reserva.canal_reserva_id == canal_reserva_id)
    ).first()
    if existente:
        return "ya_existia"

    # 2. Parsear fechas
    try:
        fecha_checkin = date.fromisoformat(r_data["fecha_checkin"])
        fecha_checkout = date.fromisoformat(r_data["fecha_checkout"])
    except (KeyError, ValueError) as e:
        logger.warning(f"[Sync] Fechas inválidas en reserva OTA {canal_reserva_id}: {e}")
        return "conflicto"

    # 3. Detectar conflicto con reservas directas existentes
    conflicto = db.exec(
        select(Reserva).where(
            Reserva.estado.in_(["otp_verificado", "pago_pendiente", "confirmada", "checkin"]),
            Reserva.fecha_checkin < fecha_checkout,
            Reserva.fecha_checkout > fecha_checkin,
            Reserva.canal == "directo",
        )
    ).first()

    if conflicto:
        logger.warning(
            f"[Sync] CONFLICTO: reserva OTA {canal_reserva_id} choca con reserva directa {conflicto.codigo}"
        )
        return "conflicto"

    # 4. Generar código de reserva para OTA
    count = db.exec(select(Reserva)).all()
    codigo = f"OTA-{date.today().year}-{len(count) + 1:04d}"

    # 5. Crear Reserva
    nueva = Reserva(
        codigo=codigo,
        canal=r_data.get("canal", "ota"),
        canal_reserva_id=canal_reserva_id,
        estado="confirmada",
        fecha_checkin=fecha_checkin,
        fecha_checkout=fecha_checkout,
        noches=(fecha_checkout - fecha_checkin).days,
        huespedes=r_data.get("huespedes", 1),
        precio_total_cop=r_data.get("precio_total"),
        moneda=r_data.get("moneda", "COP"),
        notas_internas=r_data.get("notas_internas", ""),
        metadatos={
            "nombre_huesped": r_data.get("nombre_huesped"),
            "email_huesped": r_data.get("email_huesped"),
            "telefono_huesped": r_data.get("telefono_huesped"),
            "fuente": "lodgify_sync",
        },
    )
    db.add(nueva)

    # 6. Crear BloqueoCalendario para que el motor de disponibilidad la vea
    bloqueo = BloqueoCalendario(
        fecha_inicio=fecha_checkin,
        fecha_fin=fecha_checkout,
        motivo=f"[{r_data.get('canal', 'OTA').upper()}] {r_data.get('nombre_huesped', 'Huésped')}",
        tipo="reserva_ota",
    )
    db.add(bloqueo)
    db.commit()

    logger.info(f"[Sync] Reserva OTA importada: {codigo} ({r_data.get('canal')} {fecha_checkin}→{fecha_checkout})")
    return "importada"


@celery_app.task(name="sincronizacion.notificar_conflicto_doble_reserva")
def notificar_conflicto_doble_reserva(r_data: dict):
    """
    Envía WhatsApp a Luis cuando se detecta un conflicto de calendario
    entre una reserva OTA nueva y una reserva directa existente.
    """
    from app.notificaciones.whatsapp import notify_new_booking_admin

    mensaje = (
        f"⚠️ CONFLICTO DE CALENDARIO DETECTADO\n\n"
        f"Canal: {r_data.get('canal', 'OTA').upper()}\n"
        f"ID externo: {r_data.get('canal_reserva_id', 'N/A')}\n"
        f"Huésped: {r_data.get('nombre_huesped', 'Desconocido')}\n"
        f"Fechas: {r_data.get('fecha_checkin')} → {r_data.get('fecha_checkout')}\n\n"
        f"Acción requerida: revisar el panel de admin y resolver manualmente."
    )
    logger.warning(f"[Sync] Notificando conflicto: {mensaje}")

    try:
        notify_new_booking_admin(
            codigo_reserva=r_data.get("canal_reserva_id", "CONFLICTO"),
            nombre_huesped=r_data.get("nombre_huesped", "Huésped OTA"),
            fecha_checkin=r_data.get("fecha_checkin", ""),
            fecha_checkout=r_data.get("fecha_checkout", ""),
            canal=r_data.get("canal", "ota"),
        )
    except Exception as e:
        logger.error(f"[Sync] Error al enviar notificación de conflicto: {e}")

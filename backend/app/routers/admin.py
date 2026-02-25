"""
Router de administración — Dashboard, Reservas, Calendario
Sprint 4 — Hacienda La Carmelita
"""
from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from calendar import monthrange

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select, func, col
from pydantic import BaseModel

from app.database import get_sync_db
from app.auth.dependencies import require_admin
from app.models.reserva import Reserva
from app.models.usuario import Usuario
from app.models.pago import Pago
from app.models.bloqueo_calendario import BloqueoCalendario
from app.models.tarifa import Tarifa
from app.services.precio import TARIFA_BAJA_DEFAULT, TARIFA_ALTA_DEFAULT
from app.models.sync_log import SyncLog

router = APIRouter()


# ── Schemas de respuesta ─────────────────────────────────────────────────────

class BloqueoCreateRequest(BaseModel):
    fecha_inicio: date
    fecha_fin: date
    motivo: Optional[str] = None
    origen: str = "manual"


class ReservaAdminItem(BaseModel):
    id: str
    codigo: str
    estado: str
    fecha_checkin: str
    fecha_checkout: str
    noches: int
    huespedes: int
    precio_total_cop: float
    huesped_nombre: str
    huesped_email: str
    created_at: str


class DashboardResponse(BaseModel):
    reservas_mes: int
    ingresos_mes: float
    reservas_pendientes: int
    proximas_llegadas: int
    ocupacion_pct: float
    ultimas_reservas: List[ReservaAdminItem]


class ReservasListResponse(BaseModel):
    items: List[ReservaAdminItem]
    total: int
    page: int
    limit: int
    pages: int


class ReporteResponse(BaseModel):
    periodo_inicio: str
    periodo_fin: str
    total_reservas: int
    reservas_confirmadas: int
    reservas_canceladas: int
    ingresos_totales: float
    noches_totales: int
    tasa_cancelacion: float
    ingreso_promedio_noche: float
    reservas_por_estado: dict
    reservas_detalle: List[ReservaAdminItem]


class TarifaItem(BaseModel):
    id: Optional[str] = None
    temporada: str
    descripcion: str
    tarifa_cop: float
    activo: bool = True


class TarifasUpdateRequest(BaseModel):
    tarifas: List[TarifaItem]


class SyncLogItem(BaseModel):
    id: str
    canal: str
    estado: str  # 'ok' | 'error' | 'en_progreso'
    reservas_importadas: int
    reservas_ya_existian: int
    conflictos_detectados: int
    mensaje_error: Optional[str]
    duracion_ms: Optional[int]
    iniciado_por: str
    created_at: str

class SyncEstadoResponse(BaseModel):
    logs: List[SyncLogItem]
    ultima_sync: Optional[str]
    minutos_desde_ultima_sync: Optional[int]
    estado_actual: str  # 'ok' | 'error' | 'sin_datos' | 'alerta' (>30min sin sync)
    total_importadas_hoy: int
    conflictos_pendientes: int


# ── Helpers ──────────────────────────────────────────────────────────────────

def _reserva_a_item(reserva: Reserva, db: Session) -> ReservaAdminItem:
    """Convierte un modelo Reserva a ReservaAdminItem con datos del huésped."""
    huesped_nombre = "—"
    huesped_email = "—"
    if reserva.usuario_id:
        usuario = db.get(Usuario, reserva.usuario_id)
        if usuario:
            huesped_nombre = f"{usuario.nombre} {usuario.apellido}".strip()
            huesped_email = usuario.email

    return ReservaAdminItem(
        id=str(reserva.id),
        codigo=reserva.codigo,
        estado=reserva.estado,
        fecha_checkin=reserva.fecha_checkin.isoformat(),
        fecha_checkout=reserva.fecha_checkout.isoformat(),
        noches=reserva.noches if reserva.noches is not None else 0,
        huespedes=reserva.huespedes,
        precio_total_cop=float(reserva.precio_total_cop or 0),
        huesped_nombre=huesped_nombre,
        huesped_email=huesped_email,
        created_at=reserva.created_at.isoformat(),
    )


# ── Endpoints ────────────────────────────────────────────────────────────────

@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(
    current_user: Usuario = Depends(require_admin),
    db: Session = Depends(get_sync_db),
):
    """KPIs y métricas del mes actual para el dashboard admin."""
    hoy = date.today()
    inicio_mes = date(hoy.year, hoy.month, 1)
    _, dias_mes = monthrange(hoy.year, hoy.month)
    fin_mes = date(hoy.year, hoy.month, dias_mes)

    # 1. Reservas creadas este mes
    reservas_mes_rows = db.exec(
        select(Reserva).where(
            Reserva.deleted_at == None,
            func.date(Reserva.created_at) >= inicio_mes,
            func.date(Reserva.created_at) <= fin_mes,
        )
    ).all()
    reservas_mes = len(reservas_mes_rows)

    # 2. Ingresos del mes (reservas confirmadas/checkin/checkout)
    estados_con_pago = ("confirmada", "checkin", "checkout")
    reservas_pagadas = db.exec(
        select(Reserva).where(
            Reserva.estado.in_(estados_con_pago),
            Reserva.deleted_at == None,
            func.date(Reserva.created_at) >= inicio_mes,
            func.date(Reserva.created_at) <= fin_mes,
        )
    ).all()
    ingresos_mes = sum(float(r.precio_total_cop or 0) for r in reservas_pagadas)

    # 3. Reservas pendientes de acción
    estados_pendientes = ("pendiente", "otp_pendiente", "otp_verificado", "pago_pendiente")
    reservas_pendientes_rows = db.exec(
        select(Reserva).where(
            Reserva.estado.in_(estados_pendientes),
            Reserva.deleted_at == None,
        )
    ).all()
    reservas_pendientes = len(reservas_pendientes_rows)

    # 4. Próximas llegadas (check-in en los próximos 7 días, estado confirmada)
    from datetime import timedelta
    proximos_7_dias = hoy + timedelta(days=7)
    proximas_llegadas_rows = db.exec(
        select(Reserva).where(
            Reserva.estado == "confirmada",
            Reserva.deleted_at == None,
            Reserva.fecha_checkin >= hoy,
            Reserva.fecha_checkin <= proximos_7_dias,
        )
    ).all()
    proximas_llegadas = len(proximas_llegadas_rows)

    # 5. Ocupación del mes: noches ocupadas / total noches del mes
    reservas_activas_mes = db.exec(
        select(Reserva).where(
            Reserva.estado.in_(("confirmada", "checkin", "checkout")),
            Reserva.deleted_at == None,
            Reserva.fecha_checkin <= fin_mes,
            Reserva.fecha_checkout >= inicio_mes,
        )
    ).all()
    noches_ocupadas = sum(r.noches for r in reservas_activas_mes if r.noches is not None)
    ocupacion_pct = round((noches_ocupadas / dias_mes) * 100, 1) if dias_mes > 0 else 0.0

    # 6. Últimas 5 reservas
    ultimas = db.exec(
        select(Reserva)
        .where(Reserva.deleted_at == None)
        .order_by(Reserva.created_at.desc())
        .limit(5)
    ).all()

    return DashboardResponse(
        reservas_mes=reservas_mes,
        ingresos_mes=ingresos_mes,
        reservas_pendientes=reservas_pendientes,
        proximas_llegadas=proximas_llegadas,
        ocupacion_pct=ocupacion_pct,
        ultimas_reservas=[_reserva_a_item(r, db) for r in ultimas],
    )


@router.get("/reservas", response_model=ReservasListResponse)
def listar_reservas(
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    current_user: Usuario = Depends(require_admin),
    db: Session = Depends(get_sync_db),
):
    """Lista paginada de reservas con filtro opcional por estado."""
    base_query = select(Reserva).where(Reserva.deleted_at == None)

    if estado:
        base_query = base_query.where(Reserva.estado == estado)

    # Total usando len on all rows (SQLModel-safe fallback)
    all_rows = db.exec(base_query).all()
    total = len(all_rows)

    # Paginación
    offset = (page - 1) * limit
    reservas = db.exec(
        base_query.order_by(Reserva.created_at.desc()).offset(offset).limit(limit)
    ).all()

    pages = max(1, -(-total // limit))  # ceil division

    return ReservasListResponse(
        items=[_reserva_a_item(r, db) for r in reservas],
        total=total,
        page=page,
        limit=limit,
        pages=pages,
    )


@router.get("/calendario")
def calendario(
    mes: Optional[str] = Query(None, description="Mes en formato YYYY-MM. Default: mes actual"),
    current_user: Usuario = Depends(require_admin),
    db: Session = Depends(get_sync_db),
):
    """Reservas del mes para vista de calendario."""
    hoy = date.today()
    if mes:
        try:
            año, m = mes.split("-")
            año, m = int(año), int(m)
        except (ValueError, TypeError):
            raise HTTPException(status_code=422, detail="Formato de mes inválido. Use YYYY-MM")
    else:
        año, m = hoy.year, hoy.month

    _, dias_mes = monthrange(año, m)
    inicio = date(año, m, 1)
    fin = date(año, m, dias_mes)

    reservas = db.exec(
        select(Reserva).where(
            Reserva.estado.not_in(("cancelada", "noshow")),
            Reserva.deleted_at == None,
            Reserva.fecha_checkin <= fin,
            Reserva.fecha_checkout >= inicio,
        ).order_by(Reserva.fecha_checkin)
    ).all()

    bloqueos = db.exec(
        select(BloqueoCalendario).where(
            BloqueoCalendario.fecha_inicio <= fin,
            BloqueoCalendario.fecha_fin >= inicio,
        )
    ).all()

    eventos = []
    for r in reservas:
        eventos.append({
            "tipo": "reserva",
            "id": str(r.id),
            "codigo": r.codigo,
            "estado": r.estado,
            "fecha_inicio": r.fecha_checkin.isoformat(),
            "fecha_fin": r.fecha_checkout.isoformat(),
            "noches": r.noches,
        })
    for b in bloqueos:
        eventos.append({
            "tipo": "bloqueo",
            "id": str(b.id),
            "motivo": b.motivo or "Bloqueo",
            "fecha_inicio": b.fecha_inicio.isoformat(),
            "fecha_fin": b.fecha_fin.isoformat(),
        })

    return {
        "mes": f"{año:04d}-{m:02d}",
        "dias": dias_mes,
        "eventos": eventos,
    }


@router.post("/bloqueos", status_code=201)
def crear_bloqueo(
    data: BloqueoCreateRequest,
    current_user: Usuario = Depends(require_admin),
    db: Session = Depends(get_sync_db),
):
    """Crea un bloqueo de fechas en el calendario."""
    if data.fecha_fin <= data.fecha_inicio:
        raise HTTPException(status_code=422, detail="fecha_fin debe ser posterior a fecha_inicio")

    bloqueo = BloqueoCalendario(
        fecha_inicio=data.fecha_inicio,
        fecha_fin=data.fecha_fin,
        motivo=data.motivo,
        origen=data.origen,
        created_by=current_user.id,
    )
    db.add(bloqueo)
    db.commit()
    db.refresh(bloqueo)
    return {
        "id": str(bloqueo.id),
        "fecha_inicio": bloqueo.fecha_inicio.isoformat(),
        "fecha_fin": bloqueo.fecha_fin.isoformat(),
        "motivo": bloqueo.motivo,
        "origen": bloqueo.origen,
        "created_at": bloqueo.created_at.isoformat(),
    }


@router.delete("/bloqueos/{bloqueo_id}", status_code=204)
def eliminar_bloqueo(
    bloqueo_id: str,
    current_user: Usuario = Depends(require_admin),
    db: Session = Depends(get_sync_db),
):
    """Elimina un bloqueo de calendario."""
    try:
        bid = uuid.UUID(bloqueo_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="bloqueo_id inválido")

    bloqueo = db.get(BloqueoCalendario, bid)
    if not bloqueo:
        raise HTTPException(status_code=404, detail="Bloqueo no encontrado")

    db.delete(bloqueo)
    db.commit()
    return None


@router.get("/precios")
def listar_precios(
    current_user: Usuario = Depends(require_admin),
    db: Session = Depends(get_sync_db),
):
    """Lista las tarifas actuales."""
    tarifas = db.exec(select(Tarifa).order_by(Tarifa.temporada)).all()

    if not tarifas:
        # Devolver defaults si no hay tarifas en DB
        return {
            "tarifas": [
                {
                    "id": None,
                    "temporada": "baja",
                    "descripcion": "Lunes a Jueves",
                    "tarifa_cop": float(TARIFA_BAJA_DEFAULT),
                    "activo": True,
                },
                {
                    "id": None,
                    "temporada": "alta",
                    "descripcion": "Viernes a Domingo",
                    "tarifa_cop": float(TARIFA_ALTA_DEFAULT),
                    "activo": True,
                },
            ]
        }

    return {
        "tarifas": [
            {
                "id": str(t.id),
                "temporada": t.temporada,
                "descripcion": t.descripcion,
                "tarifa_cop": float(t.tarifa_cop),
                "activo": t.activo,
            }
            for t in tarifas
        ]
    }


@router.put("/precios")
def actualizar_precios(
    data: TarifasUpdateRequest,
    current_user: Usuario = Depends(require_admin),
    db: Session = Depends(get_sync_db),
):
    """Actualiza las tarifas de temporada (crea o actualiza en DB)."""
    for item in data.tarifas:
        if item.tarifa_cop <= 0:
            raise HTTPException(
                status_code=422,
                detail=f"La tarifa de '{item.temporada}' debe ser mayor a 0"
            )

        existing = db.exec(
            select(Tarifa).where(Tarifa.temporada == item.temporada)
        ).first()

        if existing:
            existing.tarifa_cop = Decimal(str(item.tarifa_cop))
            existing.descripcion = item.descripcion
            existing.activo = item.activo
            existing.updated_at = datetime.utcnow()
            db.add(existing)
        else:
            nueva = Tarifa(
                temporada=item.temporada,
                descripcion=item.descripcion,
                tarifa_cop=Decimal(str(item.tarifa_cop)),
                activo=item.activo,
            )
            db.add(nueva)

    db.commit()
    return {"ok": True, "mensaje": f"{len(data.tarifas)} tarifa(s) actualizadas"}


@router.get("/reportes", response_model=ReporteResponse)
def reportes(
    desde: Optional[str] = Query(None, description="Fecha inicio YYYY-MM-DD"),
    hasta: Optional[str] = Query(None, description="Fecha fin YYYY-MM-DD"),
    current_user: Usuario = Depends(require_admin),
    db: Session = Depends(get_sync_db),
):
    """Reporte de reservas por período (últimos 30 días por defecto)."""
    from datetime import timedelta
    hoy = date.today()

    if desde:
        try:
            fecha_desde = date.fromisoformat(desde)
        except ValueError:
            raise HTTPException(status_code=422, detail="Formato inválido para 'desde'. Use YYYY-MM-DD")
    else:
        fecha_desde = hoy - timedelta(days=30)

    if hasta:
        try:
            fecha_hasta = date.fromisoformat(hasta)
        except ValueError:
            raise HTTPException(status_code=422, detail="Formato inválido para 'hasta'. Use YYYY-MM-DD")
    else:
        fecha_hasta = hoy

    if fecha_hasta < fecha_desde:
        raise HTTPException(status_code=422, detail="'hasta' debe ser posterior o igual a 'desde'")

    reservas_periodo = db.exec(
        select(Reserva).where(
            Reserva.deleted_at == None,
            func.date(Reserva.created_at) >= fecha_desde,
            func.date(Reserva.created_at) <= fecha_hasta,
        ).order_by(Reserva.created_at.desc())
    ).all()

    total = len(reservas_periodo)
    estados_pagados = ("confirmada", "checkin", "checkout")
    estados_cancelados = ("cancelada", "noshow")

    confirmadas = [r for r in reservas_periodo if r.estado in estados_pagados]
    canceladas = [r for r in reservas_periodo if r.estado in estados_cancelados]

    ingresos = sum(float(r.precio_total_cop or 0) for r in confirmadas)
    noches = sum(r.noches for r in confirmadas if r.noches is not None)

    por_estado: dict = {}
    for r in reservas_periodo:
        por_estado[r.estado] = por_estado.get(r.estado, 0) + 1

    tasa_cancel = round(len(canceladas) / total * 100, 1) if total > 0 else 0.0
    ingreso_prom = round(ingresos / noches, 0) if noches > 0 else 0.0

    return ReporteResponse(
        periodo_inicio=fecha_desde.isoformat(),
        periodo_fin=fecha_hasta.isoformat(),
        total_reservas=total,
        reservas_confirmadas=len(confirmadas),
        reservas_canceladas=len(canceladas),
        ingresos_totales=ingresos,
        noches_totales=noches,
        tasa_cancelacion=tasa_cancel,
        ingreso_promedio_noche=ingreso_prom,
        reservas_por_estado=por_estado,
        reservas_detalle=[_reserva_a_item(r, db) for r in reservas_periodo],
    )


@router.get("/sync/estado", response_model=SyncEstadoResponse)
def get_sync_estado(
    current_user: Usuario = Depends(require_admin),
    db: Session = Depends(get_sync_db),
):
    """Estado del channel manager — últimos 20 sync logs."""
    logs = db.exec(
        select(SyncLog).order_by(SyncLog.created_at.desc()).limit(20)
    ).all()

    ultima_sync = None
    minutos_desde = None
    estado_actual = "sin_datos"

    if logs:
        ultima = logs[0]
        ultima_sync = ultima.created_at.isoformat()
        delta = datetime.utcnow() - ultima.created_at
        minutos_desde = int(delta.total_seconds() / 60)

        if ultima.estado == "error":
            estado_actual = "error"
        elif minutos_desde > 30:
            estado_actual = "alerta"
        else:
            estado_actual = "ok"

    # Total importadas hoy
    hoy = date.today()
    total_hoy = sum(
        l.reservas_importadas for l in logs
        if l.created_at.date() == hoy
    )

    conflictos = sum(l.conflictos_detectados for l in logs if l.created_at.date() == hoy)

    return SyncEstadoResponse(
        logs=[
            SyncLogItem(
                id=str(l.id),
                canal=l.canal,
                estado=l.estado,
                reservas_importadas=l.reservas_importadas,
                reservas_ya_existian=l.reservas_ya_existian,
                conflictos_detectados=l.conflictos_detectados,
                mensaje_error=l.mensaje_error,
                duracion_ms=l.duracion_ms,
                iniciado_por=l.iniciado_por,
                created_at=l.created_at.isoformat(),
            )
            for l in logs
        ],
        ultima_sync=ultima_sync,
        minutos_desde_ultima_sync=minutos_desde,
        estado_actual=estado_actual,
        total_importadas_hoy=total_hoy,
        conflictos_pendientes=conflictos,
    )


@router.post("/sync/forzar", status_code=202)
def forzar_sincronizacion(
    current_user: Usuario = Depends(require_admin),
):
    """Trigger manual de sincronización OTA. Encola la tarea Celery."""
    try:
        from workers.tasks.sincronizacion import sincronizar_ota
        task = sincronizar_ota.delay(iniciado_por=f"admin:{current_user.email}")
        return {"message": "Sincronización encolada", "task_id": str(task.id)}
    except Exception as e:
        # Si Celery no está disponible (dev sin broker), ejecutar sync directo
        import logging
        logging.getLogger(__name__).warning(f"Celery no disponible, simulando sync: {e}")
        return {"message": "Sincronización simulada (Celery no disponible en dev)", "task_id": "dev-sync"}

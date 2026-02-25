"""Tests de integración del router de administración — Sprint 4.

Cubre los endpoints:
  GET /admin/dashboard
  GET /admin/reservas
  GET /admin/calendario

Fixtures propias db/client con SQLite en memoria, siguiendo el patrón
de test_pagos.py.

La autenticación admin requiere un JWT de tipo 'access' con usuario rol='admin'.
"""
from __future__ import annotations

import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from app.auth.jwt import crear_access_token
from app.database import get_sync_db
from app.main import app
from app.models.bloqueo_calendario import BloqueoCalendario
from app.models.reserva import Reserva
from app.models.usuario import Usuario


# Fixtures

@pytest.fixture(name="db")
def db_fixture():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="client")
def client_fixture(db):
    def override_get_db():
        yield db

    app.dependency_overrides[get_sync_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# Helpers

def _crear_usuario(
    db: Session,
    email: str = "admin@test.com",
    rol: str = "admin",
    nombre: str = "Admin",
    apellido: str = "Test",
) -> Usuario:
    usuario = Usuario(email=email, nombre=nombre, apellido=apellido, rol=rol)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def _admin_headers(db: Session, email: str = "admin@test.com") -> dict:
    usuario = _crear_usuario(db, email=email, rol="admin")
    token = crear_access_token({"sub": str(usuario.id)})
    return {"Authorization": f"Bearer {token}"}


def _guest_headers(db: Session, email: str = "guest@test.com") -> dict:
    usuario = _crear_usuario(db, email=email, rol="guest")
    token = crear_access_token({"sub": str(usuario.id)})
    return {"Authorization": f"Bearer {token}"}


def _crear_reserva(
    db: Session,
    codigo: str,
    email: str,
    estado: str = "confirmada",
    fecha_checkin: date = None,
    fecha_checkout: date = None,
    precio_total_cop: Decimal = Decimal("1200000"),
) -> Reserva:
    usuario = _crear_usuario(db, email=email, rol="guest", nombre="Huesped", apellido="Prueba")
    checkin = fecha_checkin or date.today() + timedelta(days=10)
    checkout = fecha_checkout or checkin + timedelta(days=2)
    noches = (checkout - checkin).days
    reserva = Reserva(
        codigo=codigo,
        usuario_id=usuario.id,
        canal="directo",
        estado=estado,
        fecha_checkin=checkin,
        fecha_checkout=checkout,
        noches=noches,
        huespedes=2,
        precio_total_cop=precio_total_cop,
        moneda="COP",
    )
    db.add(reserva)
    db.commit()
    db.refresh(reserva)
    return reserva


def _crear_bloqueo(
    db: Session,
    fecha_inicio: date = None,
    fecha_fin: date = None,
    motivo: str = "mantenimiento",
) -> BloqueoCalendario:
    inicio = fecha_inicio or date.today()
    fin = fecha_fin or inicio + timedelta(days=3)
    bloqueo = BloqueoCalendario(
        fecha_inicio=inicio,
        fecha_fin=fin,
        motivo=motivo,
        origen="manual",
    )
    db.add(bloqueo)
    db.commit()
    db.refresh(bloqueo)
    return bloqueo


# TestDashboard

class TestDashboard:
    def test_dashboard_sin_auth(self, client, db):
        """Sin header Authorization → 401 o 403."""
        response = client.get("/admin/dashboard")
        assert response.status_code in (401, 403)

    def test_dashboard_usuario_guest_rechazado(self, client, db):
        """Usuario con rol guest → 403 (no es admin)."""
        headers = _guest_headers(db, email="guest_dash@test.com")
        response = client.get("/admin/dashboard", headers=headers)
        assert response.status_code == 403

    def test_dashboard_con_admin_ok(self, client, db):
        """Admin autenticado → 200 con todos los campos KPI."""
        headers = _admin_headers(db, email="admin_dash@test.com")
        response = client.get("/admin/dashboard", headers=headers)
        assert response.status_code == 200
        data = response.json()
        campos_requeridos = (
            "reservas_mes", "ingresos_mes", "reservas_pendientes",
            "proximas_llegadas", "ocupacion_pct", "ultimas_reservas",
        )
        for campo in campos_requeridos:
            assert campo in data, f"Falta el campo '{campo}' en la respuesta"

    def test_dashboard_campos_numericos(self, client, db):
        """Todos los campos KPI numéricos son numeros >= 0."""
        _crear_reserva(db, "HLC-ADM-0001", "res1_dash@test.com", estado="confirmada")
        headers = _admin_headers(db, email="admin_num@test.com")
        response = client.get("/admin/dashboard", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["reservas_mes"], int)
        assert isinstance(data["ingresos_mes"], (int, float))
        assert isinstance(data["reservas_pendientes"], int)
        assert isinstance(data["proximas_llegadas"], int)
        assert isinstance(data["ocupacion_pct"], (int, float))
        assert data["reservas_mes"] >= 0
        assert data["ingresos_mes"] >= 0
        assert data["reservas_pendientes"] >= 0
        assert data["proximas_llegadas"] >= 0
        assert data["ocupacion_pct"] >= 0

    def test_dashboard_ultimas_reservas_es_lista(self, client, db):
        """El campo ultimas_reservas es una lista."""
        headers = _admin_headers(db, email="admin_lista@test.com")
        response = client.get("/admin/dashboard", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["ultimas_reservas"], list)

    def test_dashboard_ultimas_reservas_estructura(self, client, db):
        """Cada item de ultimas_reservas tiene los campos esperados."""
        _crear_reserva(db, "HLC-ADM-0002", "res2_dash@test.com", estado="confirmada")
        headers = _admin_headers(db, email="admin_struct@test.com")
        response = client.get("/admin/dashboard", headers=headers)
        assert response.status_code == 200
        data = response.json()
        if data["ultimas_reservas"]:
            item = data["ultimas_reservas"][0]
            campos_item = (
                "id", "codigo", "estado", "fecha_checkin", "fecha_checkout",
                "noches", "huespedes", "precio_total_cop",
                "huesped_nombre", "huesped_email", "created_at",
            )
            for campo in campos_item:
                assert campo in item, f"Falta '{campo}' en ultimas_reservas[0]"

    def test_dashboard_reservas_pendientes_cuenta_estados(self, client, db):
        """Reservas en estados pendientes aparecen en reservas_pendientes."""
        _crear_reserva(db, "HLC-ADM-0003", "pend1_dash@test.com", estado="pendiente")
        headers = _admin_headers(db, email="admin_pend@test.com")
        response = client.get("/admin/dashboard", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["reservas_pendientes"] >= 1

    def test_dashboard_maximo_5_ultimas_reservas(self, client, db):
        """El dashboard devuelve como maximo 5 reservas en ultimas_reservas."""
        for i in range(7):
            _crear_reserva(
                db,
                f"HLC-ADM-{10 + i:04d}",
                f"res_max{i}@test.com",
                estado="confirmada",
            )
        headers = _admin_headers(db, email="admin_max5@test.com")
        response = client.get("/admin/dashboard", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert len(data["ultimas_reservas"]) <= 5


# TestListarReservas

class TestListarReservas:
    def test_reservas_sin_auth(self, client, db):
        """Sin header Authorization → 401 o 403."""
        response = client.get("/admin/reservas")
        assert response.status_code in (401, 403)

    def test_reservas_usuario_guest_rechazado(self, client, db):
        """Usuario con rol guest → 403."""
        headers = _guest_headers(db, email="guest_res@test.com")
        response = client.get("/admin/reservas", headers=headers)
        assert response.status_code == 403

    def test_reservas_con_admin_ok(self, client, db):
        """Admin autenticado → 200 con campos items/total/page/limit/pages."""
        headers = _admin_headers(db, email="admin_res@test.com")
        response = client.get("/admin/reservas", headers=headers)
        assert response.status_code == 200
        data = response.json()
        for campo in ("items", "total", "page", "limit", "pages"):
            assert campo in data, f"Falta el campo '{campo}' en la respuesta"

    def test_reservas_items_es_lista(self, client, db):
        """El campo items es una lista."""
        headers = _admin_headers(db, email="admin_items@test.com")
        response = client.get("/admin/reservas", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["items"], list)

    def test_reservas_paginacion(self, client, db):
        """Con limit=1 y reservas existentes, pages >= 1."""
        _crear_reserva(db, "HLC-PAG-0001", "pag1@test.com", estado="confirmada")
        _crear_reserva(db, "HLC-PAG-0002", "pag2@test.com", estado="confirmada")
        headers = _admin_headers(db, email="admin_pag@test.com")
        response = client.get("/admin/reservas?limit=1&page=1", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 1
        assert data["page"] == 1
        assert data["pages"] >= 1
        assert len(data["items"]) <= 1

    def test_reservas_paginacion_segunda_pagina(self, client, db):
        """La segunda pagina con limit=1 devuelve datos coherentes."""
        _crear_reserva(db, "HLC-PAG-0003", "pag3@test.com", estado="confirmada")
        _crear_reserva(db, "HLC-PAG-0004", "pag4@test.com", estado="confirmada")
        headers = _admin_headers(db, email="admin_pag2@test.com")
        response = client.get("/admin/reservas?limit=1&page=2", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 2
        assert data["limit"] == 1

    def test_reservas_filtro_estado(self, client, db):
        """?estado=confirmada solo devuelve reservas con estado confirmada."""
        _crear_reserva(db, "HLC-EST-0001", "est1@test.com", estado="confirmada")
        _crear_reserva(db, "HLC-EST-0002", "est2@test.com", estado="pendiente")
        headers = _admin_headers(db, email="admin_est@test.com")
        response = client.get("/admin/reservas?estado=confirmada", headers=headers)
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert item["estado"] == "confirmada"

    def test_reservas_filtro_estado_pendiente(self, client, db):
        """?estado=pendiente solo devuelve reservas en estado pendiente."""
        _crear_reserva(db, "HLC-EST-0003", "est3@test.com", estado="confirmada")
        _crear_reserva(db, "HLC-EST-0004", "est4@test.com", estado="pendiente")
        headers = _admin_headers(db, email="admin_est2@test.com")
        response = client.get("/admin/reservas?estado=pendiente", headers=headers)
        assert response.status_code == 200
        data = response.json()
        for item in data["items"]:
            assert item["estado"] == "pendiente"

    def test_reservas_total_correcto(self, client, db):
        """El campo total refleja el numero real de reservas creadas."""
        _crear_reserva(db, "HLC-TOT-0001", "tot1@test.com", estado="confirmada")
        _crear_reserva(db, "HLC-TOT-0002", "tot2@test.com", estado="confirmada")
        _crear_reserva(db, "HLC-TOT-0003", "tot3@test.com", estado="pendiente")
        headers = _admin_headers(db, email="admin_tot@test.com")
        response = client.get("/admin/reservas", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 3

    def test_reservas_sin_filtro_devuelve_todas(self, client, db):
        """Sin filtro de estado, devuelve reservas en todos los estados."""
        _crear_reserva(db, "HLC-ALL-0001", "all1@test.com", estado="confirmada")
        _crear_reserva(db, "HLC-ALL-0002", "all2@test.com", estado="pendiente")
        _crear_reserva(db, "HLC-ALL-0003", "all3@test.com", estado="cancelada")
        headers = _admin_headers(db, email="admin_all@test.com")
        response = client.get("/admin/reservas", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["total"] >= 3


# TestCalendario

class TestCalendario:
    def test_calendario_sin_auth(self, client, db):
        """Sin header Authorization → 401 o 403."""
        response = client.get("/admin/calendario")
        assert response.status_code in (401, 403)

    def test_calendario_usuario_guest_rechazado(self, client, db):
        """Usuario con rol guest → 403."""
        headers = _guest_headers(db, email="guest_cal@test.com")
        response = client.get("/admin/calendario", headers=headers)
        assert response.status_code == 403

    def test_calendario_con_admin_ok(self, client, db):
        """Admin autenticado → 200 con campos mes/dias/eventos."""
        headers = _admin_headers(db, email="admin_cal@test.com")
        response = client.get("/admin/calendario", headers=headers)
        assert response.status_code == 200
        data = response.json()
        for campo in ("mes", "dias", "eventos"):
            assert campo in data, f"Falta el campo '{campo}' en la respuesta"

    def test_calendario_mes_parametro_enero(self, client, db):
        """?mes=2025-01 devuelve mes='2025-01' y dias=31."""
        headers = _admin_headers(db, email="admin_ene@test.com")
        response = client.get("/admin/calendario?mes=2025-01", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["mes"] == "2025-01"
        assert data["dias"] == 31

    def test_calendario_mes_febrero_2025(self, client, db):
        """?mes=2025-02 devuelve dias=28 (2025 no es bisiesto)."""
        headers = _admin_headers(db, email="admin_feb@test.com")
        response = client.get("/admin/calendario?mes=2025-02", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["mes"] == "2025-02"
        assert data["dias"] == 28

    def test_calendario_mes_invalido(self, client, db):
        """?mes=foo → 422 (formato invalido)."""
        headers = _admin_headers(db, email="admin_inv@test.com")
        response = client.get("/admin/calendario?mes=foo", headers=headers)
        assert response.status_code == 422

    def test_calendario_mes_invalido_formato_parcial(self, client, db):
        """?mes=2025 (sin el numero de mes) → 422."""
        headers = _admin_headers(db, email="admin_inv2@test.com")
        response = client.get("/admin/calendario?mes=2025", headers=headers)
        assert response.status_code == 422

    def test_calendario_eventos_es_lista(self, client, db):
        """El campo eventos es una lista."""
        headers = _admin_headers(db, email="admin_ev@test.com")
        response = client.get("/admin/calendario", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["eventos"], list)

    def test_calendario_incluye_reservas(self, client, db):
        """Las reservas del mes aparecen en eventos con tipo='reserva'."""
        hoy = date.today()
        mes_str = f"{hoy.year:04d}-{hoy.month:02d}"
        checkin = date(hoy.year, hoy.month, 5)
        checkout = date(hoy.year, hoy.month, 8)
        _crear_reserva(
            db, "HLC-CAL-0001", "cal1@test.com",
            estado="confirmada", fecha_checkin=checkin, fecha_checkout=checkout,
        )
        headers = _admin_headers(db, email="admin_inc@test.com")
        response = client.get(f"/admin/calendario?mes={mes_str}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        tipos_reserva = [e for e in data["eventos"] if e["tipo"] == "reserva"]
        assert len(tipos_reserva) >= 1

    def test_calendario_incluye_bloqueos(self, client, db):
        """Los bloqueos del mes aparecen en eventos con tipo='bloqueo'."""
        hoy = date.today()
        mes_str = f"{hoy.year:04d}-{hoy.month:02d}"
        inicio = date(hoy.year, hoy.month, 12)
        fin = date(hoy.year, hoy.month, 14)
        _crear_bloqueo(db, fecha_inicio=inicio, fecha_fin=fin, motivo="mantenimiento")
        headers = _admin_headers(db, email="admin_bloq@test.com")
        response = client.get(f"/admin/calendario?mes={mes_str}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        tipos_bloqueo = [e for e in data["eventos"] if e["tipo"] == "bloqueo"]
        assert len(tipos_bloqueo) >= 1

    def test_calendario_evento_reserva_estructura(self, client, db):
        """Cada evento de tipo reserva tiene los campos obligatorios."""
        hoy = date.today()
        mes_str = f"{hoy.year:04d}-{hoy.month:02d}"
        checkin = date(hoy.year, hoy.month, 15)
        checkout = date(hoy.year, hoy.month, 17)
        _crear_reserva(
            db, "HLC-CAL-0002", "cal2@test.com",
            estado="confirmada", fecha_checkin=checkin, fecha_checkout=checkout,
        )
        headers = _admin_headers(db, email="admin_evstruct@test.com")
        response = client.get(f"/admin/calendario?mes={mes_str}", headers=headers)
        assert response.status_code == 200
        data = response.json()
        eventos_reserva = [e for e in data["eventos"] if e["tipo"] == "reserva"]
        assert len(eventos_reserva) >= 1
        ev = eventos_reserva[0]
        for campo in ("tipo", "id", "codigo", "estado", "fecha_inicio", "fecha_fin", "noches"):
            assert campo in ev, f"Falta el campo '{campo}' en evento de tipo reserva"

    def test_calendario_sin_mes_usa_mes_actual(self, client, db):
        """Sin parametro ?mes, el campo mes del response corresponde al mes actual."""
        hoy = date.today()
        mes_esperado = f"{hoy.year:04d}-{hoy.month:02d}"
        headers = _admin_headers(db, email="admin_curr@test.com")
        response = client.get("/admin/calendario", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["mes"] == mes_esperado

    def test_calendario_dias_diciembre(self, client, db):
        """?mes=2025-12 devuelve dias=31."""
        headers = _admin_headers(db, email="admin_dic@test.com")
        response = client.get("/admin/calendario?mes=2025-12", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["mes"] == "2025-12"
        assert data["dias"] == 31

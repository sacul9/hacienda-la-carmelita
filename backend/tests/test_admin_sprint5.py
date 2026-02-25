"""Tests de integración del router de administración — Sprint 5.

Cubre los endpoints:
  POST   /admin/bloqueos
  DELETE /admin/bloqueos/{bloqueo_id}
  GET    /admin/reportes

Fixtures propias db/client con SQLite en memoria, siguiendo el patrón
de test_admin.py.

La autenticación admin requiere un JWT de tipo 'access' con usuario rol='admin'.
"""
from __future__ import annotations

import uuid
from datetime import date, timedelta
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


# ── Fixtures ──────────────────────────────────────────────────────────────────

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


# ── Helpers ───────────────────────────────────────────────────────────────────

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


def _crear_bloqueo_directo(
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


# ── TestCrearBloqueo ───────────────────────────────────────────────────────────

class TestCrearBloqueo:
    def test_crear_bloqueo_sin_auth(self, client, db):
        """Sin header Authorization → 401 o 403."""
        payload = {
            "fecha_inicio": "2025-06-01",
            "fecha_fin": "2025-06-05",
            "motivo": "Mantenimiento",
        }
        response = client.post("/admin/bloqueos", json=payload)
        assert response.status_code in (401, 403)

    def test_crear_bloqueo_con_admin_ok(self, client, db):
        """Admin autenticado → 201 con campos id, fecha_inicio, fecha_fin, motivo."""
        headers = _admin_headers(db, email="admin_blq_ok@test.com")
        payload = {
            "fecha_inicio": "2025-06-01",
            "fecha_fin": "2025-06-05",
            "motivo": "Mantenimiento",
        }
        response = client.post("/admin/bloqueos", json=payload, headers=headers)
        assert response.status_code == 201
        data = response.json()
        for campo in ("id", "fecha_inicio", "fecha_fin", "motivo", "origen", "created_at"):
            assert campo in data, f"Falta el campo '{campo}' en la respuesta"
        assert data["fecha_inicio"] == "2025-06-01"
        assert data["fecha_fin"] == "2025-06-05"
        assert data["motivo"] == "Mantenimiento"

    def test_crear_bloqueo_fecha_invalida(self, client, db):
        """fecha_fin == fecha_inicio → 422."""
        headers = _admin_headers(db, email="admin_blq_eq@test.com")
        payload = {
            "fecha_inicio": "2025-07-10",
            "fecha_fin": "2025-07-10",
        }
        response = client.post("/admin/bloqueos", json=payload, headers=headers)
        assert response.status_code == 422

    def test_crear_bloqueo_fecha_fin_anterior(self, client, db):
        """fecha_fin < fecha_inicio → 422."""
        headers = _admin_headers(db, email="admin_blq_ant@test.com")
        payload = {
            "fecha_inicio": "2025-08-10",
            "fecha_fin": "2025-08-05",
        }
        response = client.post("/admin/bloqueos", json=payload, headers=headers)
        assert response.status_code == 422

    def test_crear_bloqueo_sin_motivo(self, client, db):
        """motivo es opcional → 201 sin necesidad de proveer motivo."""
        headers = _admin_headers(db, email="admin_blq_nomot@test.com")
        payload = {
            "fecha_inicio": "2025-09-01",
            "fecha_fin": "2025-09-03",
        }
        response = client.post("/admin/bloqueos", json=payload, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert data["fecha_inicio"] == "2025-09-01"
        assert data["fecha_fin"] == "2025-09-03"

    def test_crear_bloqueo_guest_rechazado(self, client, db):
        """Usuario con rol guest → 403 (no es admin)."""
        headers = _guest_headers(db, email="guest_blq@test.com")
        payload = {
            "fecha_inicio": "2025-10-01",
            "fecha_fin": "2025-10-05",
            "motivo": "Test",
        }
        response = client.post("/admin/bloqueos", json=payload, headers=headers)
        assert response.status_code == 403

    def test_crear_bloqueo_origen_por_defecto(self, client, db):
        """El origen por defecto es 'manual'."""
        headers = _admin_headers(db, email="admin_blq_orig@test.com")
        payload = {
            "fecha_inicio": "2025-11-01",
            "fecha_fin": "2025-11-05",
            "motivo": "Prueba origen",
        }
        response = client.post("/admin/bloqueos", json=payload, headers=headers)
        assert response.status_code == 201
        data = response.json()
        assert data["origen"] == "manual"


# ── TestEliminarBloqueo ────────────────────────────────────────────────────────

class TestEliminarBloqueo:
    def test_eliminar_bloqueo_sin_auth(self, client, db):
        """Sin header Authorization → 401 o 403."""
        bloqueo = _crear_bloqueo_directo(db)
        response = client.delete(f"/admin/bloqueos/{bloqueo.id}")
        assert response.status_code in (401, 403)

    def test_eliminar_bloqueo_ok(self, client, db):
        """Admin autenticado crea y elimina un bloqueo → 204 sin contenido."""
        headers = _admin_headers(db, email="admin_del_ok@test.com")
        # Primero crear el bloqueo via POST
        payload = {
            "fecha_inicio": "2025-06-10",
            "fecha_fin": "2025-06-15",
            "motivo": "Para eliminar",
        }
        create_response = client.post("/admin/bloqueos", json=payload, headers=headers)
        assert create_response.status_code == 201
        bloqueo_id = create_response.json()["id"]

        # Ahora eliminar
        delete_response = client.delete(f"/admin/bloqueos/{bloqueo_id}", headers=headers)
        assert delete_response.status_code == 204
        assert delete_response.content == b""

    def test_eliminar_bloqueo_no_existe(self, client, db):
        """UUID valido pero no encontrado → 404."""
        headers = _admin_headers(db, email="admin_del_404@test.com")
        uuid_inexistente = str(uuid.uuid4())
        response = client.delete(f"/admin/bloqueos/{uuid_inexistente}", headers=headers)
        assert response.status_code == 404

    def test_eliminar_bloqueo_uuid_invalido(self, client, db):
        """UUID invalido → 422."""
        headers = _admin_headers(db, email="admin_del_inv@test.com")
        response = client.delete("/admin/bloqueos/no-es-un-uuid", headers=headers)
        assert response.status_code == 422

    def test_eliminar_bloqueo_idempotente(self, client, db):
        """Despues de eliminar, el bloqueo no aparece en el calendario."""
        headers = _admin_headers(db, email="admin_del_idem@test.com")
        hoy = date.today()
        mes_str = f"{hoy.year:04d}-{hoy.month:02d}"
        inicio = date(hoy.year, hoy.month, 20)
        fin = date(hoy.year, hoy.month, 22) if hoy.month < 12 else date(hoy.year, hoy.month, 28)

        # Crear bloqueo via POST
        payload = {
            "fecha_inicio": inicio.isoformat(),
            "fecha_fin": fin.isoformat(),
            "motivo": "Bloqueo temporal",
        }
        create_response = client.post("/admin/bloqueos", json=payload, headers=headers)
        assert create_response.status_code == 201
        bloqueo_id = create_response.json()["id"]

        # Verificar que aparece en el calendario
        cal_antes = client.get(f"/admin/calendario?mes={mes_str}", headers=headers)
        assert cal_antes.status_code == 200
        bloqueos_antes = [e for e in cal_antes.json()["eventos"] if e["tipo"] == "bloqueo" and e["id"] == bloqueo_id]
        assert len(bloqueos_antes) == 1

        # Eliminar el bloqueo
        delete_response = client.delete(f"/admin/bloqueos/{bloqueo_id}", headers=headers)
        assert delete_response.status_code == 204

        # Verificar que ya no aparece en el calendario
        cal_despues = client.get(f"/admin/calendario?mes={mes_str}", headers=headers)
        assert cal_despues.status_code == 200
        bloqueos_despues = [e for e in cal_despues.json()["eventos"] if e["tipo"] == "bloqueo" and e["id"] == bloqueo_id]
        assert len(bloqueos_despues) == 0

    def test_eliminar_bloqueo_guest_rechazado(self, client, db):
        """Usuario con rol guest → 403."""
        bloqueo = _crear_bloqueo_directo(db)
        headers = _guest_headers(db, email="guest_del@test.com")
        response = client.delete(f"/admin/bloqueos/{bloqueo.id}", headers=headers)
        assert response.status_code == 403


# ── TestReportes ───────────────────────────────────────────────────────────────

class TestReportes:
    def test_reportes_sin_auth(self, client, db):
        """Sin header Authorization → 401 o 403."""
        response = client.get("/admin/reportes")
        assert response.status_code in (401, 403)

    def test_reportes_con_admin_ok(self, client, db):
        """Admin autenticado → 200 con todos los campos requeridos."""
        headers = _admin_headers(db, email="admin_rep_ok@test.com")
        response = client.get("/admin/reportes", headers=headers)
        assert response.status_code == 200
        data = response.json()
        campos_requeridos = (
            "periodo_inicio",
            "periodo_fin",
            "total_reservas",
            "reservas_confirmadas",
            "reservas_canceladas",
            "ingresos_totales",
            "noches_totales",
            "tasa_cancelacion",
            "ingreso_promedio_noche",
            "reservas_por_estado",
            "reservas_detalle",
        )
        for campo in campos_requeridos:
            assert campo in data, f"Falta el campo '{campo}' en la respuesta"

    def test_reportes_campos_numericos(self, client, db):
        """Los campos numericos son numeros >= 0."""
        _crear_reserva(db, "HLC-RPT-0001", "rep1@test.com", estado="confirmada")
        headers = _admin_headers(db, email="admin_rep_num@test.com")
        response = client.get("/admin/reportes", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["total_reservas"], int)
        assert isinstance(data["reservas_confirmadas"], int)
        assert isinstance(data["reservas_canceladas"], int)
        assert isinstance(data["ingresos_totales"], (int, float))
        assert isinstance(data["noches_totales"], int)
        assert isinstance(data["tasa_cancelacion"], (int, float))
        assert isinstance(data["ingreso_promedio_noche"], (int, float))
        assert data["total_reservas"] >= 0
        assert data["reservas_confirmadas"] >= 0
        assert data["reservas_canceladas"] >= 0
        assert data["ingresos_totales"] >= 0
        assert data["noches_totales"] >= 0
        assert data["tasa_cancelacion"] >= 0
        assert data["ingreso_promedio_noche"] >= 0

    def test_reportes_fecha_invalida(self, client, db):
        """?desde=foo → 422 (formato invalido)."""
        headers = _admin_headers(db, email="admin_rep_inv@test.com")
        response = client.get("/admin/reportes?desde=foo", headers=headers)
        assert response.status_code == 422

    def test_reportes_rango_invertido(self, client, db):
        """?hasta < ?desde → 422."""
        headers = _admin_headers(db, email="admin_rep_rng@test.com")
        response = client.get("/admin/reportes?hasta=2025-01-01&desde=2025-12-31", headers=headers)
        assert response.status_code == 422

    def test_reportes_con_rango_especifico(self, client, db):
        """?desde=2025-01-01&hasta=2025-12-31 → 200 con periodo correcto."""
        headers = _admin_headers(db, email="admin_rep_rng2@test.com")
        response = client.get("/admin/reportes?desde=2025-01-01&hasta=2025-12-31", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["periodo_inicio"] == "2025-01-01"
        assert data["periodo_fin"] == "2025-12-31"

    def test_reportes_reservas_detalle_es_lista(self, client, db):
        """El campo reservas_detalle es una lista."""
        headers = _admin_headers(db, email="admin_rep_lista@test.com")
        response = client.get("/admin/reportes", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["reservas_detalle"], list)

    def test_reportes_reservas_por_estado_es_dict(self, client, db):
        """El campo reservas_por_estado es un diccionario."""
        headers = _admin_headers(db, email="admin_rep_dict@test.com")
        response = client.get("/admin/reportes", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["reservas_por_estado"], dict)

    def test_reportes_sin_params_usa_ultimos_30_dias(self, client, db):
        """Sin params, periodo_fin es hoy y periodo_inicio es hace 30 dias."""
        from datetime import timedelta
        hoy = date.today()
        hace_30 = hoy - timedelta(days=30)
        headers = _admin_headers(db, email="admin_rep_default@test.com")
        response = client.get("/admin/reportes", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["periodo_inicio"] == hace_30.isoformat()
        assert data["periodo_fin"] == hoy.isoformat()

    def test_reportes_hasta_invalida(self, client, db):
        """?hasta=bar → 422 (formato invalido)."""
        headers = _admin_headers(db, email="admin_rep_inv2@test.com")
        response = client.get("/admin/reportes?hasta=bar", headers=headers)
        assert response.status_code == 422

    def test_reportes_guest_rechazado(self, client, db):
        """Usuario con rol guest → 403."""
        headers = _guest_headers(db, email="guest_rep@test.com")
        response = client.get("/admin/reportes", headers=headers)
        assert response.status_code == 403

    def test_reportes_contabiliza_reservas_confirmadas(self, client, db):
        """Las reservas confirmadas del periodo aparecen en reservas_confirmadas."""
        _crear_reserva(db, "HLC-RPT-0010", "rep10@test.com", estado="confirmada")
        headers = _admin_headers(db, email="admin_rep_conf@test.com")
        # Use a very wide range to ensure the reservation's created_at is captured
        response = client.get("/admin/reportes?desde=2020-01-01&hasta=2030-12-31", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["reservas_confirmadas"] >= 1
        assert data["total_reservas"] >= 1

    def test_reportes_contabiliza_reservas_canceladas(self, client, db):
        """Las reservas canceladas aparecen en reservas_canceladas."""
        _crear_reserva(db, "HLC-RPT-0011", "rep11@test.com", estado="cancelada")
        headers = _admin_headers(db, email="admin_rep_canc@test.com")
        # Use a very wide range to ensure the reservation's created_at is captured
        response = client.get("/admin/reportes?desde=2020-01-01&hasta=2030-12-31", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert data["reservas_canceladas"] >= 1

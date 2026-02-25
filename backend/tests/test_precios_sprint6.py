"""Tests de precios dinámicos (admin) — Sprint 6 (Agente Sprint6C).

Cubre los endpoints:
  GET    /admin/precios
  PUT    /admin/precios

Requiere autenticación de administrador (JWT con rol='admin').
La DB de tests es SQLite en memoria; cada test arranca con DB limpia.
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from app.auth.jwt import crear_access_token
from app.database import get_sync_db
from app.main import app
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


# ── TestObtenerPrecios ────────────────────────────────────────────────────────

class TestObtenerPrecios:
    def test_obtener_precios_sin_auth_retorna_403(self, client, db):
        """GET /admin/precios sin token de autorizacion → 401 o 403."""
        resp = client.get("/admin/precios")
        assert resp.status_code in (401, 403)

    def test_obtener_precios_con_admin_retorna_200(self, client, db):
        """Admin autenticado → 200 con campo 'tarifas' (lista)."""
        headers = _admin_headers(db, email="admin_get_pr@test.com")
        resp = client.get("/admin/precios", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "tarifas" in data
        assert isinstance(data["tarifas"], list)

    def test_obtener_precios_estructura(self, client, db):
        """Cada tarifa tiene los campos: temporada, tarifa_cop, descripcion, activo."""
        headers = _admin_headers(db, email="admin_str_pr@test.com")
        resp = client.get("/admin/precios", headers=headers)
        assert resp.status_code == 200
        tarifas = resp.json()["tarifas"]
        assert len(tarifas) >= 1, "Debe haber al menos una tarifa (o los defaults)"
        for tarifa in tarifas:
            for campo in ("temporada", "tarifa_cop", "descripcion", "activo"):
                assert campo in tarifa, f"Campo '{campo}' falta en tarifa: {tarifa}"
            assert isinstance(tarifa["temporada"], str)
            assert isinstance(tarifa["tarifa_cop"], (int, float))
            assert isinstance(tarifa["descripcion"], str)
            assert isinstance(tarifa["activo"], bool)

    def test_obtener_precios_defaults(self, client, db):
        """Si la DB está vacía, devuelve tarifas por defecto: baja=800000, alta=1200000."""
        headers = _admin_headers(db, email="admin_def_pr@test.com")
        # La DB está vacía (no hay filas en tarifas), el endpoint devuelve defaults
        resp = client.get("/admin/precios", headers=headers)
        assert resp.status_code == 200
        tarifas = resp.json()["tarifas"]
        temporadas = {t["temporada"]: t for t in tarifas}
        # Verificar tarifas por defecto
        assert "baja" in temporadas, "Falta la tarifa de temporada 'baja' en los defaults"
        assert "alta" in temporadas, "Falta la tarifa de temporada 'alta' en los defaults"
        assert temporadas["baja"]["tarifa_cop"] == 800000.0
        assert temporadas["alta"]["tarifa_cop"] == 1200000.0


# ── TestActualizarPrecios ─────────────────────────────────────────────────────

class TestActualizarPrecios:
    def test_actualizar_precios_sin_auth_retorna_403(self, client, db):
        """PUT /admin/precios sin token de autorizacion → 401 o 403."""
        payload = {
            "tarifas": [
                {
                    "temporada": "baja",
                    "descripcion": "Lunes a Jueves",
                    "tarifa_cop": 900000,
                    "activo": True,
                }
            ]
        }
        resp = client.put("/admin/precios", json=payload)
        assert resp.status_code in (401, 403)

    def test_actualizar_precios_validos(self, client, db):
        """PUT con tarifas válidas y admin autenticado → 200."""
        headers = _admin_headers(db, email="admin_put_v@test.com")
        payload = {
            "tarifas": [
                {
                    "temporada": "baja",
                    "descripcion": "Lunes a Jueves actualizado",
                    "tarifa_cop": 850000,
                    "activo": True,
                },
                {
                    "temporada": "alta",
                    "descripcion": "Viernes a Domingo actualizado",
                    "tarifa_cop": 1300000,
                    "activo": True,
                },
            ]
        }
        resp = client.put("/admin/precios", json=payload, headers=headers)
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data.get("ok") is True

    def test_actualizar_precios_tarifa_cero_retorna_422(self, client, db):
        """tarifa_cop = 0 → 422 (la tarifa debe ser mayor a 0)."""
        headers = _admin_headers(db, email="admin_cero@test.com")
        payload = {
            "tarifas": [
                {
                    "temporada": "baja",
                    "descripcion": "Temporada baja",
                    "tarifa_cop": 0,
                    "activo": True,
                }
            ]
        }
        resp = client.put("/admin/precios", json=payload, headers=headers)
        assert resp.status_code in (400, 422)

    def test_actualizar_precios_tarifa_negativa_retorna_422(self, client, db):
        """tarifa_cop negativa → 422 (la tarifa debe ser mayor a 0)."""
        headers = _admin_headers(db, email="admin_neg@test.com")
        payload = {
            "tarifas": [
                {
                    "temporada": "alta",
                    "descripcion": "Temporada alta",
                    "tarifa_cop": -100,
                    "activo": True,
                }
            ]
        }
        resp = client.put("/admin/precios", json=payload, headers=headers)
        assert resp.status_code in (400, 422)

    def test_actualizar_precios_persiste(self, client, db):
        """Después de PUT, GET /admin/precios refleja los nuevos valores guardados."""
        headers = _admin_headers(db, email="admin_persist@test.com")
        nueva_tarifa_baja = 777000.0
        nueva_tarifa_alta = 1111000.0

        # Actualizar
        payload = {
            "tarifas": [
                {
                    "temporada": "baja",
                    "descripcion": "Tarifa baja persistencia test",
                    "tarifa_cop": nueva_tarifa_baja,
                    "activo": True,
                },
                {
                    "temporada": "alta",
                    "descripcion": "Tarifa alta persistencia test",
                    "tarifa_cop": nueva_tarifa_alta,
                    "activo": True,
                },
            ]
        }
        put_resp = client.put("/admin/precios", json=payload, headers=headers)
        assert put_resp.status_code in (200, 201)

        # Verificar que el GET refleja los nuevos valores
        get_resp = client.get("/admin/precios", headers=headers)
        assert get_resp.status_code == 200
        tarifas = get_resp.json()["tarifas"]
        temporadas = {t["temporada"]: t for t in tarifas}

        assert "baja" in temporadas
        assert "alta" in temporadas
        assert temporadas["baja"]["tarifa_cop"] == nueva_tarifa_baja
        assert temporadas["alta"]["tarifa_cop"] == nueva_tarifa_alta

"""Tests de autenticación — Sprint 1."""

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_sync_db
from app.models.usuario import Usuario


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


class TestRegistro:
    def test_registro_nuevo_usuario(self, client):
        """Registrar un usuario nuevo debe retornar 201."""
        response = client.post("/auth/registro", json={
            "email": "nuevo@test.com",
            "nombre": "Juan",
            "apellido": "García",
            "telefono": "+573001234567",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "nuevo@test.com"
        assert data["nombre"] == "Juan"
        assert "id" in data

    def test_registro_email_existente_retorna_usuario(self, client):
        """Si el email ya existe, debe retornar el usuario existente (no error)."""
        payload = {
            "email": "existente@test.com",
            "nombre": "María",
            "apellido": "López",
            "telefono": "+573009876543",
        }
        r1 = client.post("/auth/registro", json=payload)
        r2 = client.post("/auth/registro", json=payload)
        assert r1.status_code == 201
        assert r2.status_code == 201
        assert r1.json()["id"] == r2.json()["id"]

    def test_registro_email_invalido(self, client):
        """Un email inválido debe retornar 422."""
        response = client.post("/auth/registro", json={
            "email": "no-es-un-email",
            "nombre": "Test",
            "apellido": "Test",
            "telefono": "+573001234567",
        })
        assert response.status_code == 422

    def test_registro_nombre_vacio(self, client):
        """Un nombre vacío debe retornar 422."""
        response = client.post("/auth/registro", json={
            "email": "test@test.com",
            "nombre": "   ",
            "apellido": "García",
            "telefono": "+573001234567",
        })
        assert response.status_code == 422


class TestHealth:
    def test_health_ok(self, client):
        """Health check debe retornar 200."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    def test_root_ok(self, client):
        """Root endpoint debe retornar 200."""
        response = client.get("/")
        assert response.status_code == 200

"""Tests del endpoint POST /reservas y operaciones de reserva — Sprint 2.

Fixtures propias db/client con SQLite en memoria, siguiendo el patrón
de test_auth.py.

Nota sobre crear_otp_token: la firma real es
    crear_otp_token(otp_id: str, usuario_id: str) -> str
por lo tanto en cada test se crea también un OTP en la BD para tener
un otp_id válido.
"""
from __future__ import annotations

import uuid
import pytest
from datetime import date, datetime, timedelta
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_sync_db
from app.auth.jwt import crear_otp_token
from app.models.usuario import Usuario
from app.models.reserva import Reserva
from app.models.otp import OTP

# ─── Fixtures ─────────────────────────────────────────────────────────────────

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


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _crear_usuario(db: Session, email: str = "huesped@test.com") -> Usuario:
    """Crea y persiste un usuario de prueba."""
    usuario = Usuario(
        email=email,
        nombre="Ana",
        apellido="Lopez",
        rol="guest",
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def _crear_otp(db: Session, usuario_id: uuid.UUID) -> OTP:
    """Crea y persiste un OTP de prueba verificado."""
    otp = OTP(
        usuario_id=usuario_id,
        canal="email",
        destino="huesped@test.com",
        codigo="hash_placeholder",
        proposito="reserva",
        verificado=True,
        expires_at=datetime.utcnow() + timedelta(minutes=30),
    )
    db.add(otp)
    db.commit()
    db.refresh(otp)
    return otp


def _token_y_headers(db: Session, email: str = "huesped@test.com") -> tuple:
    """Crea usuario + OTP y devuelve (usuario, headers con Bearer token)."""
    usuario = _crear_usuario(db, email=email)
    otp = _crear_otp(db, usuario.id)
    token = crear_otp_token(str(otp.id), str(usuario.id))
    headers = {"Authorization": f"Bearer {token}"}
    return usuario, headers


# Body base para POST /reservas (fechas libres de conflictos)
_BODY_BASE = {
    "fecha_checkin": "2025-10-01",
    "fecha_checkout": "2025-10-05",
    "huespedes": 2,
    "sku_id": "hacienda-completa",
    "addon_ids": [],
    "notas_huesped": None,
}


# ─── TestCrearReserva ─────────────────────────────────────────────────────────

class TestCrearReserva:
    def test_crear_exitosa_retorna_201(self, client, db):
        """POST /reservas con token OTP válido debe retornar 201."""
        _, headers = _token_y_headers(db)
        response = client.post("/reservas", json=_BODY_BASE, headers=headers)
        assert response.status_code == 201

    def test_codigo_formato_hlc(self, client, db):
        """El código de la reserva creada debe comenzar con 'HLC-'."""
        _, headers = _token_y_headers(db)
        response = client.post("/reservas", json=_BODY_BASE, headers=headers)
        assert response.status_code == 201
        assert response.json()["codigo"].startswith("HLC-")

    def test_estado_inicial_otp_verificado(self, client, db):
        """El estado inicial de la reserva debe ser 'otp_verificado'."""
        _, headers = _token_y_headers(db)
        response = client.post("/reservas", json=_BODY_BASE, headers=headers)
        assert response.status_code == 201
        assert response.json()["estado"] == "otp_verificado"

    def test_sin_token_retorna_401(self, client):
        """POST /reservas sin header Authorization debe retornar 401."""
        response = client.post("/reservas", json=_BODY_BASE)
        assert response.status_code == 401

    def test_1_noche_retorna_400(self, client, db):
        """Solicitar 1 noche (checkin = checkout - 1 día) debe retornar 400."""
        _, headers = _token_y_headers(db)
        body = {**_BODY_BASE, "fecha_checkin": "2025-10-04", "fecha_checkout": "2025-10-05"}
        response = client.post("/reservas", json=body, headers=headers)
        assert response.status_code == 400

    def test_fechas_bloqueadas_retornan_409(self, client, db):
        """Si ya existe una reserva confirmada en esas fechas, debe retornar 409."""
        # Primera reserva: crea y confirma manualmente las fechas
        usuario1 = _crear_usuario(db, email="primero@test.com")
        reserva_existente = Reserva(
            codigo="HLC-PREV-0001",
            usuario_id=usuario1.id,
            canal="directo",
            estado="confirmada",
            fecha_checkin=date(2025, 10, 1),
            fecha_checkout=date(2025, 10, 5),
            noches=4,
            huespedes=2,
            precio_total_cop=Decimal("3200000"),
            moneda="COP",
        )
        db.add(reserva_existente)
        db.commit()

        # Segunda reserva con las mismas fechas
        _, headers = _token_y_headers(db, email="segundo@test.com")
        response = client.post("/reservas", json=_BODY_BASE, headers=headers)
        assert response.status_code == 409

    def test_respuesta_incluye_noches(self, client, db):
        """La respuesta debe incluir el campo 'noches' calculado correctamente."""
        _, headers = _token_y_headers(db)
        response = client.post("/reservas", json=_BODY_BASE, headers=headers)
        assert response.status_code == 201
        assert response.json()["noches"] == 4

    def test_respuesta_incluye_precio_cop(self, client, db):
        """La respuesta debe incluir 'precio_total_cop' distinto de None."""
        _, headers = _token_y_headers(db)
        response = client.post("/reservas", json=_BODY_BASE, headers=headers)
        assert response.status_code == 201
        assert response.json()["precio_total_cop"] is not None


# ─── TestObtenerReserva ───────────────────────────────────────────────────────

class TestObtenerReserva:
    def _insertar_reserva(self, db: Session, codigo: str = "HLC-2025-0001") -> Reserva:
        usuario = _crear_usuario(db, email=f"get_{codigo}@test.com")
        reserva = Reserva(
            codigo=codigo,
            usuario_id=usuario.id,
            canal="directo",
            estado="otp_verificado",
            fecha_checkin=date(2025, 11, 1),
            fecha_checkout=date(2025, 11, 5),
            noches=4,
            huespedes=2,
            precio_total_cop=Decimal("3200000"),
            moneda="COP",
        )
        db.add(reserva)
        db.commit()
        db.refresh(reserva)
        return reserva

    def test_por_codigo_existente_retorna_200(self, client, db):
        """GET /reservas/{codigo} con un código existente debe retornar 200."""
        reserva = self._insertar_reserva(db)
        response = client.get(f"/reservas/{reserva.codigo}")
        assert response.status_code == 200

    def test_por_codigo_existente_retorna_datos_correctos(self, client, db):
        """El body de la respuesta debe contener el código de la reserva."""
        reserva = self._insertar_reserva(db)
        response = client.get(f"/reservas/{reserva.codigo}")
        assert response.status_code == 200
        assert response.json()["codigo"] == reserva.codigo

    def test_codigo_inexistente_retorna_404(self, client):
        """GET /reservas/HLC-FAKE-0000 debe retornar 404."""
        response = client.get("/reservas/HLC-FAKE-0000")
        assert response.status_code == 404

    def test_codigo_case_insensitive(self, client, db):
        """El router normaliza el código a mayúsculas; minúsculas deben funcionar."""
        reserva = self._insertar_reserva(db, codigo="HLC-2025-0002")
        response = client.get(f"/reservas/{reserva.codigo.lower()}")
        assert response.status_code == 200

"""Tests de integración del motor de disponibilidad y precio — Sprint 2.

Incluye fixtures propias db/client con SQLite en memoria, siguiendo
el patrón de test_auth.py.
"""
from __future__ import annotations

import pytest
from datetime import date
from decimal import Decimal

from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool

from app.main import app
from app.database import get_sync_db
from app.models.bloqueo_calendario import BloqueoCalendario
from app.models.reserva import Reserva
from app.models.usuario import Usuario

# ─── Fechas base ──────────────────────────────────────────────────────────────
DESDE = date(2025, 9, 1)
HASTA = date(2025, 9, 5)


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

def _crear_usuario(db: Session, email: str = "helper@test.com") -> Usuario:
    usuario = Usuario(
        email=email,
        nombre="Test",
        apellido="User",
        rol="guest",
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def _crear_reserva(db: Session, estado: str, email: str = "reserva@test.com") -> Reserva:
    usuario = _crear_usuario(db, email=email)
    reserva = Reserva(
        codigo="HLC-TEST-001",
        usuario_id=usuario.id,
        canal="directo",
        estado=estado,
        fecha_checkin=DESDE,
        fecha_checkout=HASTA,
        noches=4,
        huespedes=2,
        precio_total_cop=Decimal("3200000"),
        moneda="COP",
    )
    db.add(reserva)
    db.commit()
    return reserva


# ─── TestDisponibilidadEndpoint ───────────────────────────────────────────────

class TestDisponibilidadEndpoint:
    def test_rango_libre_retorna_disponible(self, client):
        """Sin bloqueos ni reservas el rango debe estar disponible."""
        response = client.get(
            "/disponibilidad",
            params={"desde": "2025-09-01", "hasta": "2025-09-05"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["disponible"] is True
        assert data["fechas_bloqueadas"] == []

    def test_bloqueo_manual_bloquea_fechas(self, client, db):
        """Un BloqueoCalendario en el rango debe hacer disponible=False."""
        bloqueo = BloqueoCalendario(
            fecha_inicio=DESDE,
            fecha_fin=HASTA,
            motivo="mantenimiento",
            origen="manual",
        )
        db.add(bloqueo)
        db.commit()

        response = client.get(
            "/disponibilidad",
            params={"desde": "2025-09-01", "hasta": "2025-09-05"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["disponible"] is False
        assert len(data["fechas_bloqueadas"]) > 0

    def test_reserva_confirmada_bloquea_fechas(self, client, db):
        """Una reserva con estado='confirmada' debe bloquear las fechas."""
        _crear_reserva(db, estado="confirmada")

        response = client.get(
            "/disponibilidad",
            params={"desde": "2025-09-01", "hasta": "2025-09-05"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["disponible"] is False

    def test_reserva_cancelada_no_bloquea(self, client, db):
        """Una reserva cancelada NO debe bloquear las fechas."""
        _crear_reserva(db, estado="cancelada")

        response = client.get(
            "/disponibilidad",
            params={"desde": "2025-09-01", "hasta": "2025-09-05"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["disponible"] is True
        assert data["fechas_bloqueadas"] == []

    def test_fechas_invalidas_retornan_422(self, client):
        """Una fecha con formato incorrecto debe retornar 422."""
        response = client.get(
            "/disponibilidad",
            params={"desde": "no-es-fecha", "hasta": "2025-09-05"},
        )
        assert response.status_code == 422

    def test_hasta_antes_que_desde_retorna_400(self, client):
        """Si 'hasta' es anterior a 'desde' debe retornar 400."""
        response = client.get(
            "/disponibilidad",
            params={"desde": "2025-09-10", "hasta": "2025-09-05"},
        )
        assert response.status_code == 400

    def test_desde_igual_hasta_retorna_400(self, client):
        """Si 'desde' == 'hasta' (0 noches) debe retornar 400."""
        response = client.get(
            "/disponibilidad",
            params={"desde": "2025-09-05", "hasta": "2025-09-05"},
        )
        assert response.status_code == 400

    def test_reserva_otp_verificado_bloquea(self, client, db):
        """Estado 'otp_verificado' está en ESTADOS_OCUPADOS y debe bloquear."""
        _crear_reserva(db, estado="otp_verificado")

        response = client.get(
            "/disponibilidad",
            params={"desde": "2025-09-01", "hasta": "2025-09-05"},
        )
        assert response.status_code == 200
        assert response.json()["disponible"] is False


# ─── TestPrecioEndpoint ───────────────────────────────────────────────────────

class TestPrecioEndpoint:
    def test_precio_2_noches_baja(self, client):
        """2 noches de lunes a miércoles → total_cop == TARIFA_BAJA * 2."""
        # 2025-08-04 = Lunes, 2025-08-06 = Miércoles
        from app.services.precio import TARIFA_BAJA
        response = client.get(
            "/disponibilidad/precio",
            params={"desde": "2025-08-04", "hasta": "2025-08-06"},
        )
        assert response.status_code == 200
        data = response.json()
        assert Decimal(str(data["total_cop"])) == TARIFA_BAJA * 2

    def test_precio_incluye_desglose(self, client):
        """2 noches → len(desglose) == 2."""
        response = client.get(
            "/disponibilidad/precio",
            params={"desde": "2025-08-04", "hasta": "2025-08-06"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data["desglose"]) == 2

    def test_1_noche_retorna_400(self, client):
        """Solicitar 1 noche debe retornar 400 (mínimo 2 noches)."""
        response = client.get(
            "/disponibilidad/precio",
            params={"desde": "2025-09-01", "hasta": "2025-09-02"},
        )
        assert response.status_code == 400

    def test_precio_incluye_noches_en_respuesta(self, client):
        """La respuesta debe incluir el campo 'noches' con el valor correcto."""
        response = client.get(
            "/disponibilidad/precio",
            params={"desde": "2025-08-04", "hasta": "2025-08-06"},
        )
        assert response.status_code == 200
        assert response.json()["noches"] == 2

    def test_precio_hasta_antes_de_desde_retorna_400(self, client):
        """'hasta' anterior a 'desde' debe retornar 400."""
        response = client.get(
            "/disponibilidad/precio",
            params={"desde": "2025-09-10", "hasta": "2025-09-05"},
        )
        assert response.status_code == 400

    def test_precio_total_usd_presente(self, client):
        """La respuesta debe incluir el campo 'total_usd'."""
        response = client.get(
            "/disponibilidad/precio",
            params={"desde": "2025-08-04", "hasta": "2025-08-06"},
        )
        assert response.status_code == 200
        assert "total_usd" in response.json()

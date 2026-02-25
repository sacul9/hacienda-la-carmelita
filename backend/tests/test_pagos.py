"""Tests de integración del router de pagos — Sprint 3.

Cubre los endpoints:
  POST /pagos/wompi/iniciar
  POST /pagos/wompi/webhook
  GET  /pagos/{pago_id}/estado

Fixtures propias db/client con SQLite en memoria, siguiendo el patrón
de test_reservas.py.

La firma Wompi se calcula como:
    SHA256(timestamp + payload_json + integrity_key)
"""
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool

from app.auth.jwt import crear_otp_token
from app.config import settings
from app.database import get_sync_db
from app.main import app
from app.models.otp import OTP
from app.models.pago import Pago
from app.models.reserva import Reserva
from app.models.usuario import Usuario


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
    usuario = Usuario(
        email=email,
        nombre="Juan",
        apellido="Perez",
        rol="guest",
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def _crear_otp(db: Session, usuario_id: uuid.UUID) -> OTP:
    otp = OTP(
        usuario_id=usuario_id,
        canal="email",
        destino="huesped@test.com",
        codigo="hash_placeholder",
        proposito="pago",
        verificado=True,
        expires_at=datetime.utcnow() + timedelta(minutes=30),
    )
    db.add(otp)
    db.commit()
    db.refresh(otp)
    return otp


def _otp_headers(db: Session, email: str = "huesped@pagos@test.com") -> dict:
    """Crea usuario + OTP y retorna headers con Bearer token tipo otp_verified."""
    usuario = _crear_usuario(db, email=email)
    otp = _crear_otp(db, usuario.id)
    token = crear_otp_token(str(otp.id), str(usuario.id))
    return {"Authorization": f"Bearer {token}"}


def _crear_reserva_en_estado(
    db: Session,
    estado: str,
    codigo: str = "HLC-TEST-0001",
    email: str = "reserva@test.com",
) -> Reserva:
    """Crea y persiste una reserva con el estado dado."""
    usuario = _crear_usuario(db, email=email)
    reserva = Reserva(
        codigo=codigo,
        usuario_id=usuario.id,
        canal="directo",
        estado=estado,
        fecha_checkin=date(2026, 3, 15),
        fecha_checkout=date(2026, 3, 17),
        noches=2,
        huespedes=2,
        precio_total_cop=Decimal("2400000"),
        moneda="COP",
    )
    db.add(reserva)
    db.commit()
    db.refresh(reserva)
    return reserva


def _crear_pago(
    db: Session,
    reserva_id: uuid.UUID,
    estado: str = "pendiente",
    pasarela: str = "wompi",
    referencia: str = "HLC-TEST-0001",
) -> Pago:
    """Crea y persiste un pago de prueba."""
    pago = Pago(
        reserva_id=reserva_id,
        pasarela=pasarela,
        monto=Decimal("2400000"),
        moneda="COP",
        estado=estado,
        metadatos={"referencia": referencia},
    )
    db.add(pago)
    db.commit()
    db.refresh(pago)
    return pago


def _calcular_firma_wompi(timestamp: str, payload_bytes: bytes) -> str:
    """SHA256(timestamp + payload_json + integrity_key) — mismo algoritmo que el servicio."""
    cadena = timestamp + payload_bytes.decode("utf-8") + settings.WOMPI_INTEGRITY_KEY
    return hashlib.sha256(cadena.encode()).hexdigest()


# ─── TestWompiIniciar ─────────────────────────────────────────────────────────


class TestWompiIniciar:
    def test_wompi_iniciar_ok(self, client, db):
        """Reserva en pago_pendiente + OTP token → 201 con checkout_url."""
        reserva = _crear_reserva_en_estado(
            db, "pago_pendiente", codigo="HLC-TEST-0001", email="ok1@test.com"
        )
        headers = _otp_headers(db, email="otp1@test.com")
        response = client.post(
            "/pagos/wompi/iniciar",
            json={"reserva_id": str(reserva.id)},
            headers=headers,
        )
        assert response.status_code == 201
        data = response.json()
        assert "checkout_url" in data
        assert "pago_id" in data
        assert data["pasarela"] == "wompi"
        assert data["monto_cop"] == float(reserva.precio_total_cop)

    def test_wompi_iniciar_referencia_en_respuesta(self, client, db):
        """La respuesta debe incluir el campo 'referencia'."""
        reserva = _crear_reserva_en_estado(
            db, "pago_pendiente", codigo="HLC-TEST-0002", email="ok2@test.com"
        )
        headers = _otp_headers(db, email="otp2@test.com")
        response = client.post(
            "/pagos/wompi/iniciar",
            json={"reserva_id": str(reserva.id)},
            headers=headers,
        )
        assert response.status_code == 201
        assert response.json()["referencia"] == reserva.codigo

    def test_wompi_iniciar_sin_auth(self, client, db):
        """Sin header Authorization → 401."""
        reserva = _crear_reserva_en_estado(
            db, "pago_pendiente", codigo="HLC-TEST-0003", email="noauth@test.com"
        )
        response = client.post(
            "/pagos/wompi/iniciar",
            json={"reserva_id": str(reserva.id)},
        )
        assert response.status_code == 401

    def test_wompi_iniciar_reserva_no_existe(self, client, db):
        """UUID inventado → 404."""
        headers = _otp_headers(db, email="otp3@test.com")
        fake_id = str(uuid.uuid4())
        response = client.post(
            "/pagos/wompi/iniciar",
            json={"reserva_id": fake_id},
            headers=headers,
        )
        assert response.status_code == 404

    def test_wompi_iniciar_estado_incorrecto_confirmada(self, client, db):
        """Reserva en estado 'confirmada' → 409."""
        reserva = _crear_reserva_en_estado(
            db, "confirmada", codigo="HLC-TEST-0004", email="conf1@test.com"
        )
        headers = _otp_headers(db, email="otp4@test.com")
        response = client.post(
            "/pagos/wompi/iniciar",
            json={"reserva_id": str(reserva.id)},
            headers=headers,
        )
        assert response.status_code == 409

    def test_wompi_iniciar_con_reserva_pendiente(self, client, db):
        """Reserva en estado 'pendiente' (no es pago_pendiente) → 409."""
        reserva = _crear_reserva_en_estado(
            db, "pendiente", codigo="HLC-TEST-0005", email="pend1@test.com"
        )
        headers = _otp_headers(db, email="otp5@test.com")
        response = client.post(
            "/pagos/wompi/iniciar",
            json={"reserva_id": str(reserva.id)},
            headers=headers,
        )
        assert response.status_code == 409

    def test_wompi_iniciar_otp_verificado_estado_incorrecto(self, client, db):
        """Reserva en estado 'otp_verificado' → 409 (tampoco es pago_pendiente)."""
        reserva = _crear_reserva_en_estado(
            db, "otp_verificado", codigo="HLC-TEST-0006", email="otp6a@test.com"
        )
        headers = _otp_headers(db, email="otp6b@test.com")
        response = client.post(
            "/pagos/wompi/iniciar",
            json={"reserva_id": str(reserva.id)},
            headers=headers,
        )
        assert response.status_code == 409


# ─── TestWompiWebhook ─────────────────────────────────────────────────────────


class TestWompiWebhook:
    def _payload_transaccion(
        self,
        referencia: str = "HLC-TEST-0001",
        status: str = "APPROVED",
        evento: str = "transaction.updated",
    ) -> bytes:
        """Construye un payload de evento Wompi como bytes JSON."""
        body = {
            "event": evento,
            "data": {
                "transaction": {
                    "id": "wompi-tx-001",
                    "reference": referencia,
                    "status": status,
                    "payment_method_type": "CARD",
                }
            },
        }
        return json.dumps(body, separators=(",", ":")).encode()

    def test_wompi_webhook_sin_headers(self, client, db):
        """Sin timestamp ni checksum headers → 400."""
        payload = self._payload_transaccion()
        response = client.post(
            "/pagos/wompi/webhook",
            content=payload,
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 400

    def test_wompi_webhook_firma_invalida(self, client, db):
        """Headers presentes pero checksum incorrecto → 400."""
        payload = self._payload_transaccion()
        response = client.post(
            "/pagos/wompi/webhook",
            content=payload,
            headers={
                "Content-Type": "application/json",
                "X-Event-Signature-Timestamp": "1700000000",
                "X-Event-Signature-Checksum": "firma_completamente_incorrecta",
            },
        )
        assert response.status_code == 400

    def test_wompi_webhook_solo_timestamp_sin_checksum(self, client, db):
        """Solo timestamp sin checksum → 400."""
        payload = self._payload_transaccion()
        response = client.post(
            "/pagos/wompi/webhook",
            content=payload,
            headers={
                "Content-Type": "application/json",
                "X-Event-Signature-Timestamp": "1700000000",
            },
        )
        assert response.status_code == 400

    def test_wompi_webhook_transaccion_approved(self, client, db):
        """Firma válida + evento APPROVED → 200, pago actualizado a aprobado."""
        reserva = _crear_reserva_en_estado(
            db, "pago_pendiente", codigo="HLC-TEST-0010", email="wh1@test.com"
        )
        _crear_pago(db, reserva.id, estado="pendiente", referencia="HLC-TEST-0010")

        payload = self._payload_transaccion(
            referencia="HLC-TEST-0010", status="APPROVED"
        )
        timestamp = "1700000000"
        checksum = _calcular_firma_wompi(timestamp, payload)

        response = client.post(
            "/pagos/wompi/webhook",
            content=payload,
            headers={
                "Content-Type": "application/json",
                "X-Event-Signature-Timestamp": timestamp,
                "X-Event-Signature-Checksum": checksum,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True

    def test_wompi_webhook_evento_ignorado(self, client, db):
        """Firma válida pero evento diferente a 'transaction.updated' → 200 con procesado=False."""
        payload = self._payload_transaccion(evento="charge.created")
        timestamp = "1700000001"
        checksum = _calcular_firma_wompi(timestamp, payload)

        response = client.post(
            "/pagos/wompi/webhook",
            content=payload,
            headers={
                "Content-Type": "application/json",
                "X-Event-Signature-Timestamp": timestamp,
                "X-Event-Signature-Checksum": checksum,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert data["procesado"] is False


# ─── TestEstadoPago ───────────────────────────────────────────────────────────


class TestEstadoPago:
    def test_estado_pago_ok(self, client, db):
        """Pago existente → 200 con los datos correctos."""
        reserva = _crear_reserva_en_estado(
            db, "pago_pendiente", codigo="HLC-TEST-0020", email="ep1@test.com"
        )
        pago = _crear_pago(db, reserva.id, estado="pendiente")

        response = client.get(f"/pagos/{pago.id}/estado")
        assert response.status_code == 200
        data = response.json()
        assert data["pago_id"] == str(pago.id)
        assert data["estado"] == "pendiente"
        assert data["pasarela"] == "wompi"
        assert data["moneda"] == "COP"
        assert "monto" in data

    def test_estado_pago_campos_presentes(self, client, db):
        """La respuesta de estado incluye todos los campos esperados."""
        reserva = _crear_reserva_en_estado(
            db, "pago_pendiente", codigo="HLC-TEST-0021", email="ep2@test.com"
        )
        pago = _crear_pago(db, reserva.id, estado="aprobado")

        response = client.get(f"/pagos/{pago.id}/estado")
        assert response.status_code == 200
        data = response.json()
        for campo in ("pago_id", "estado", "pasarela", "monto", "moneda"):
            assert campo in data, f"Falta el campo '{campo}' en la respuesta"

    def test_estado_pago_no_existe(self, client, db):
        """UUID inventado → 404."""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/pagos/{fake_id}/estado")
        assert response.status_code == 404

    def test_estado_pago_uuid_invalido(self, client, db):
        """String 'abc' (no UUID) → 422."""
        response = client.get("/pagos/abc/estado")
        assert response.status_code == 422

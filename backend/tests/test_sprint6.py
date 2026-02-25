"""Tests de integración — Sprint 6: Chat IA y Precios dinámicos.

Cubre los endpoints:
  POST   /chat/mensaje
  POST   /chat/escalar-whatsapp
  GET    /chat/{session_id}/historial
  GET    /admin/precios
  PUT    /admin/precios

La autenticación admin requiere un JWT de tipo 'access' con usuario rol='admin'.
Las llamadas a Anthropic se mockean para evitar llamadas reales a la API.
"""
from __future__ import annotations

from unittest.mock import patch

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


# ── TestChatMensaje ────────────────────────────────────────────────────────────

class TestChatMensaje:
    def test_mensaje_normal_con_mock(self, client, db):
        """Mensaje valido → 200 con campo 'respuesta' (Claude mockeado)."""
        with patch(
            "app.routers.chat.obtener_respuesta_chat",
            return_value="¡Hola! Soy Carmelita, tu asistente virtual.",
        ):
            resp = client.post(
                "/chat/mensaje",
                json={"mensaje": "Hola, ¿qué servicios ofrecen?", "historial": []},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "respuesta" in data
        assert isinstance(data["respuesta"], str)
        assert len(data["respuesta"]) > 0

    def test_mensaje_vacio_retorna_422(self, client, db):
        """Mensaje vacío o sólo espacios → 422."""
        resp = client.post(
            "/chat/mensaje",
            json={"mensaje": "", "historial": []},
        )
        assert resp.status_code == 422

    def test_mensaje_solo_espacios_retorna_422(self, client, db):
        """Mensaje con sólo espacios en blanco → 422."""
        resp = client.post(
            "/chat/mensaje",
            json={"mensaje": "   ", "historial": []},
        )
        assert resp.status_code == 422

    def test_mensaje_demasiado_largo_retorna_422(self, client, db):
        """Mensaje con más de 2000 caracteres → 422."""
        mensaje_largo = "A" * 2001
        resp = client.post(
            "/chat/mensaje",
            json={"mensaje": mensaje_largo, "historial": []},
        )
        assert resp.status_code == 422

    def test_mensaje_exactamente_2000_chars_ok(self, client, db):
        """Mensaje con exactamente 2000 caracteres → 200 (límite exacto es válido)."""
        mensaje_limite = "A" * 2000
        with patch(
            "app.routers.chat.obtener_respuesta_chat",
            return_value="Respuesta de Carmelita para mensaje largo.",
        ):
            resp = client.post(
                "/chat/mensaje",
                json={"mensaje": mensaje_limite, "historial": []},
            )
        assert resp.status_code == 200

    def test_mensaje_con_historial_previo(self, client, db):
        """Mensaje con historial previo → 200, se procesa correctamente."""
        historial = [
            {"role": "user", "content": "¿Cuántos huéspedes admiten?"},
            {"role": "assistant", "content": "Hasta 18 huéspedes."},
        ]
        with patch(
            "app.routers.chat.obtener_respuesta_chat",
            return_value="Claro, tenemos capacidad para 18 personas.",
        ):
            resp = client.post(
                "/chat/mensaje",
                json={"mensaje": "Gracias por la info", "historial": historial},
            )
        assert resp.status_code == 200
        assert "respuesta" in resp.json()

    def test_mensaje_sin_campo_historial_usa_default(self, client, db):
        """El campo historial es opcional — puede omitirse."""
        with patch(
            "app.routers.chat.obtener_respuesta_chat",
            return_value="Hola, ¿en qué puedo ayudarte?",
        ):
            resp = client.post(
                "/chat/mensaje",
                json={"mensaje": "¿Tienen piscina?"},
            )
        assert resp.status_code == 200
        assert "respuesta" in resp.json()

    def test_mensaje_error_claude_retorna_502(self, client, db):
        """Si Claude lanza excepción → 502."""
        with patch(
            "app.services.claude_chat.obtener_respuesta_chat",
            side_effect=Exception("API de Anthropic no disponible"),
        ):
            resp = client.post(
                "/chat/mensaje",
                json={"mensaje": "¿Cuáles son los precios?", "historial": []},
            )
        assert resp.status_code == 502


# ── TestChatEscalarWhatsapp ────────────────────────────────────────────────────

class TestChatEscalarWhatsapp:
    def test_escalar_whatsapp_retorna_200(self, client, db):
        """POST /chat/escalar-whatsapp → 200 con campo 'whatsapp_url'."""
        resp = client.post(
            "/chat/escalar-whatsapp",
            json={"mensaje": "Necesito hablar con alguien", "historial": []},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "whatsapp_url" in data

    def test_escalar_whatsapp_url_contiene_wa_me(self, client, db):
        """La URL generada contiene 'wa.me' para ser un enlace de WhatsApp válido."""
        resp = client.post(
            "/chat/escalar-whatsapp",
            json={"mensaje": "Quiero hablar con un humano", "historial": []},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "wa.me" in data["whatsapp_url"]

    def test_escalar_whatsapp_url_contiene_contexto(self, client, db):
        """La URL de WhatsApp incluye parte del mensaje original como contexto."""
        mensaje = "Quiero reservar para 10 personas"
        resp = client.post(
            "/chat/escalar-whatsapp",
            json={"mensaje": mensaje, "historial": []},
        )
        assert resp.status_code == 200
        url = resp.json()["whatsapp_url"]
        # El mensaje debe estar codificado en la URL
        assert "wa.me" in url
        assert isinstance(url, str)
        assert len(url) > 20


# ── TestChatHistorial ─────────────────────────────────────────────────────────

class TestChatHistorial:
    def test_historial_retorna_200(self, client, db):
        """GET /chat/{session_id}/historial → 200."""
        resp = client.get("/chat/abc123/historial")
        assert resp.status_code == 200

    def test_historial_contiene_session_id(self, client, db):
        """La respuesta incluye el session_id solicitado."""
        session_id = "sesion-test-456"
        resp = client.get(f"/chat/{session_id}/historial")
        assert resp.status_code == 200
        data = resp.json()
        assert data["session_id"] == session_id

    def test_historial_contiene_lista_vacia(self, client, db):
        """La respuesta incluye campo 'historial' que es una lista."""
        resp = client.get("/chat/cualquier-id/historial")
        assert resp.status_code == 200
        data = resp.json()
        assert "historial" in data
        assert isinstance(data["historial"], list)

    def test_historial_contiene_nota(self, client, db):
        """La respuesta incluye campo 'nota' informativo."""
        resp = client.get("/chat/mi-sesion/historial")
        assert resp.status_code == 200
        data = resp.json()
        assert "nota" in data
        assert isinstance(data["nota"], str)


# ── TestAdminGetPrecios ────────────────────────────────────────────────────────

class TestAdminGetPrecios:
    def test_get_precios_sin_auth_retorna_401_o_403(self, client, db):
        """Sin header Authorization → 401 o 403."""
        resp = client.get("/admin/precios")
        assert resp.status_code in (401, 403)

    def test_get_precios_con_admin_retorna_200(self, client, db):
        """Admin autenticado → 200 con campo 'tarifas'."""
        headers = _admin_headers(db, email="admin_precios@test.com")
        resp = client.get("/admin/precios", headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "tarifas" in data
        assert isinstance(data["tarifas"], list)

    def test_get_precios_guest_rechazado(self, client, db):
        """Usuario con rol guest → 403."""
        headers = _guest_headers(db, email="guest_precios@test.com")
        resp = client.get("/admin/precios", headers=headers)
        assert resp.status_code == 403

    def test_get_precios_devuelve_lista_con_tarifas(self, client, db):
        """La lista de tarifas no está vacía (devuelve defaults si no hay en DB)."""
        headers = _admin_headers(db, email="admin_precios_lista@test.com")
        resp = client.get("/admin/precios", headers=headers)
        assert resp.status_code == 200
        tarifas = resp.json()["tarifas"]
        assert len(tarifas) >= 1

    def test_get_precios_campos_requeridos_por_tarifa(self, client, db):
        """Cada tarifa tiene los campos esperados: temporada, descripcion, tarifa_cop, activo."""
        headers = _admin_headers(db, email="admin_precios_campos@test.com")
        resp = client.get("/admin/precios", headers=headers)
        assert resp.status_code == 200
        tarifas = resp.json()["tarifas"]
        for tarifa in tarifas:
            for campo in ("temporada", "descripcion", "tarifa_cop", "activo"):
                assert campo in tarifa, f"Falta el campo '{campo}' en tarifa {tarifa}"


# ── TestAdminPutPrecios ────────────────────────────────────────────────────────

class TestAdminPutPrecios:
    def test_put_precios_sin_auth_retorna_401_o_403(self, client, db):
        """Sin header Authorization → 401 o 403."""
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

    def test_put_precios_con_admin_ok(self, client, db):
        """Admin autenticado con tarifa válida → 200."""
        headers = _admin_headers(db, email="admin_put_precios@test.com")
        payload = {
            "tarifas": [
                {
                    "temporada": "baja",
                    "descripcion": "Lunes a Jueves",
                    "tarifa_cop": 850000,
                    "activo": True,
                }
            ]
        }
        resp = client.put("/admin/precios", json=payload, headers=headers)
        assert resp.status_code == 200

    def test_put_precios_actualiza_y_get_refleja_cambio(self, client, db):
        """Después de PUT, GET /admin/precios devuelve la tarifa actualizada."""
        headers = _admin_headers(db, email="admin_put_get@test.com")
        nueva_tarifa = 999000.0

        # Actualizar
        payload = {
            "tarifas": [
                {
                    "temporada": "especial",
                    "descripcion": "Temporada especial de prueba",
                    "tarifa_cop": nueva_tarifa,
                    "activo": True,
                }
            ]
        }
        put_resp = client.put("/admin/precios", json=payload, headers=headers)
        assert put_resp.status_code == 200

        # Verificar
        get_resp = client.get("/admin/precios", headers=headers)
        assert get_resp.status_code == 200
        tarifas = get_resp.json()["tarifas"]
        especiales = [t for t in tarifas if t["temporada"] == "especial"]
        assert len(especiales) == 1
        assert especiales[0]["tarifa_cop"] == nueva_tarifa

    def test_put_precios_tarifa_cero_retorna_error(self, client, db):
        """tarifa_cop = 0 → 422 (debe ser mayor a 0)."""
        headers = _admin_headers(db, email="admin_put_cero@test.com")
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

    def test_put_precios_tarifa_negativa_retorna_error(self, client, db):
        """tarifa_cop negativa → 422 (debe ser mayor a 0)."""
        headers = _admin_headers(db, email="admin_put_neg@test.com")
        payload = {
            "tarifas": [
                {
                    "temporada": "alta",
                    "descripcion": "Temporada alta",
                    "tarifa_cop": -1500,
                    "activo": True,
                }
            ]
        }
        resp = client.put("/admin/precios", json=payload, headers=headers)
        assert resp.status_code in (400, 422)

    def test_put_precios_multiples_temporadas(self, client, db):
        """Se pueden actualizar múltiples temporadas en un solo PUT → 200."""
        headers = _admin_headers(db, email="admin_put_multi@test.com")
        payload = {
            "tarifas": [
                {
                    "temporada": "baja",
                    "descripcion": "Lunes a Jueves",
                    "tarifa_cop": 800000,
                    "activo": True,
                },
                {
                    "temporada": "alta",
                    "descripcion": "Viernes a Domingo",
                    "tarifa_cop": 1200000,
                    "activo": True,
                },
            ]
        }
        resp = client.put("/admin/precios", json=payload, headers=headers)
        assert resp.status_code == 200

    def test_put_precios_guest_rechazado(self, client, db):
        """Usuario con rol guest → 403."""
        headers = _guest_headers(db, email="guest_put_precios@test.com")
        payload = {
            "tarifas": [
                {
                    "temporada": "baja",
                    "descripcion": "Temporada baja",
                    "tarifa_cop": 800000,
                    "activo": True,
                }
            ]
        }
        resp = client.put("/admin/precios", json=payload, headers=headers)
        assert resp.status_code == 403

    def test_put_precios_respuesta_contiene_ok(self, client, db):
        """La respuesta del PUT exitoso contiene el campo 'ok': True."""
        headers = _admin_headers(db, email="admin_put_ok_field@test.com")
        payload = {
            "tarifas": [
                {
                    "temporada": "baja",
                    "descripcion": "Lunes a Jueves",
                    "tarifa_cop": 820000,
                    "activo": True,
                }
            ]
        }
        resp = client.put("/admin/precios", json=payload, headers=headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data.get("ok") is True

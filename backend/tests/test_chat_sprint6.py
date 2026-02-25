"""Tests del router de Chat IA — Sprint 6 (Agente Sprint6C).

Cubre los endpoints:
  POST   /chat/mensaje
  POST   /chat/escalar-whatsapp

Las llamadas a Claude se mockean con unittest.mock.patch sobre la
referencia importada en el router: app.routers.chat.obtener_respuesta_chat.
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
    email: str = "user@test.com",
    rol: str = "guest",
    nombre: str = "Test",
    apellido: str = "User",
) -> Usuario:
    usuario = Usuario(email=email, nombre=nombre, apellido=apellido, rol=rol)
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


def _user_headers(db: Session, email: str = "user@test.com") -> dict:
    usuario = _crear_usuario(db, email=email)
    token = crear_access_token({"sub": str(usuario.id)})
    return {"Authorization": f"Bearer {token}"}


# ── TestMensajeChat ────────────────────────────────────────────────────────────

class TestMensajeChat:
    def test_mensaje_vacio_retorna_422(self, client, db):
        """POST /chat/mensaje con mensaje vacío → 422 (validación de negocio)."""
        resp = client.post(
            "/chat/mensaje",
            json={"mensaje": "", "historial": []},
        )
        assert resp.status_code == 422

    def test_mensaje_muy_largo_retorna_422(self, client, db):
        """Mensaje de 2001 caracteres → 422 (supera el límite de 2000)."""
        mensaje_largo = "X" * 2001
        resp = client.post(
            "/chat/mensaje",
            json={"mensaje": mensaje_largo, "historial": []},
        )
        assert resp.status_code == 422

    def test_mensaje_normal_retorna_respuesta(self, client, db):
        """Mensaje válido → 200, body tiene campo 'respuesta' (str no vacío).

        Se mockea obtener_respuesta_chat en el namespace del router para
        evitar llamadas reales a la API de Anthropic/Claude.
        """
        with patch(
            "app.routers.chat.obtener_respuesta_chat",
            return_value="Hola, soy Carmelita, tu asistente virtual.",
        ):
            resp = client.post(
                "/chat/mensaje",
                json={"mensaje": "Buenos días, ¿qué actividades tienen?", "historial": []},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "respuesta" in data
        assert isinstance(data["respuesta"], str)
        assert len(data["respuesta"]) > 0

    def test_mensaje_con_historial(self, client, db):
        """Enviar historial con 2 mensajes previos → 200, respuesta presente."""
        historial = [
            {"role": "user", "content": "¿Cuál es la capacidad máxima?"},
            {"role": "assistant", "content": "Hasta 18 huéspedes."},
        ]
        with patch(
            "app.routers.chat.obtener_respuesta_chat",
            return_value="Con gusto le ayudo con más información.",
        ):
            resp = client.post(
                "/chat/mensaje",
                json={"mensaje": "¿Y el precio por noche?", "historial": historial},
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "respuesta" in data
        assert isinstance(data["respuesta"], str)

    def test_mensaje_sin_historial_key(self, client, db):
        """Omitir el campo 'historial' → usa valor por defecto (lista vacía) → 200."""
        with patch(
            "app.routers.chat.obtener_respuesta_chat",
            return_value="Claro, puedo ayudarle con esa información.",
        ):
            resp = client.post(
                "/chat/mensaje",
                json={"mensaje": "¿Tienen piscina climatizada?"},
            )
        # historial tiene default=[] en el schema, por lo que no mandarlo es válido
        assert resp.status_code == 200
        assert "respuesta" in resp.json()

    def test_mensaje_con_nombre_usuario(self, client, db):
        """Incluir usuario autenticado en payload → 200, el nombre se pasa a Claude."""
        headers = _user_headers(db, email="lucia@test.com")
        # La función mockeada recibirá nombre_usuario="Test User" desde el router
        with patch(
            "app.routers.chat.obtener_respuesta_chat",
            return_value="Hola Test, bienvenido a Hacienda La Carmelita.",
        ) as mock_fn:
            resp = client.post(
                "/chat/mensaje",
                json={"mensaje": "Hola", "historial": []},
                headers=headers,
            )
        assert resp.status_code == 200
        data = resp.json()
        assert "respuesta" in data
        # El mock debe haber sido invocado con keyword nombre_usuario
        mock_fn.assert_called_once()
        _, call_kwargs = mock_fn.call_args
        assert "nombre_usuario" in call_kwargs


# ── TestEscalarWhatsapp ────────────────────────────────────────────────────────

class TestEscalarWhatsapp:
    def test_escalar_retorna_url(self, client, db):
        """POST /chat/escalar-whatsapp → 200, body tiene 'whatsapp_url' con https://wa.me/."""
        resp = client.post(
            "/chat/escalar-whatsapp",
            json={"mensaje": "necesito info sobre precios", "historial": []},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "whatsapp_url" in data
        assert data["whatsapp_url"].startswith("https://wa.me/")

    def test_escalar_contexto_vacio(self, client, db):
        """Contexto con string vacío → 200, el link de WhatsApp se genera de todas formas."""
        resp = client.post(
            "/chat/escalar-whatsapp",
            json={"mensaje": "", "historial": []},
        )
        # El endpoint escalar-whatsapp NO valida si el mensaje está vacío (a diferencia de /mensaje)
        assert resp.status_code == 200
        data = resp.json()
        assert "whatsapp_url" in data
        assert "wa.me" in data["whatsapp_url"]

    def test_escalar_contexto_largo(self, client, db):
        """Contexto de 500 chars → 200, la URL se genera (el servicio trunca a 200 internamente)."""
        contexto_largo = "Necesito información detallada sobre la hacienda. " * 10  # ~500 chars
        resp = client.post(
            "/chat/escalar-whatsapp",
            json={"mensaje": contexto_largo, "historial": []},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "whatsapp_url" in data
        url = data["whatsapp_url"]
        assert url.startswith("https://wa.me/")
        # El servicio trunca el texto a 200 chars internamente
        # La URL puede ser larga (URL-encoded) pero debe ser un string válido
        assert isinstance(url, str)
        assert len(url) > 20

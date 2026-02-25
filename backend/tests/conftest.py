import pytest
import uuid
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool
from app.main import app
from app.database import get_sync_db
from app.models.usuario import Usuario
from app.auth.jwt import crear_access_token


@pytest.fixture(name="engine")
def engine_fixture():
    """Motor SQLite en memoria para tests."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture(name="db")
def db_fixture(engine):
    """Sesión de BD para tests."""
    with Session(engine) as session:
        yield session


# Alias db_session → misma sesión que db (usado en TestImportarReservaOTA)
@pytest.fixture(name="db_session")
def db_session_fixture(db):
    """Alias de db para tests de sincronización."""
    yield db


@pytest.fixture(name="admin_user")
def admin_user_fixture(db):
    """Crea y persiste un usuario admin en la BD de test."""
    usuario = Usuario(
        id=uuid.uuid4(),
        email="admin@test.com",
        nombre="Admin",
        apellido="Test",
        rol="admin",
        email_verificado=True,
    )
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@pytest.fixture(name="admin_token")
def admin_token_fixture(admin_user):
    """JWT de acceso para el usuario admin de test."""
    token = crear_access_token({"sub": str(admin_user.id), "rol": "admin"})
    return token


@pytest.fixture(name="client")
def client_fixture(db):
    """TestClient de FastAPI con BD de test."""
    def override_get_db():
        yield db

    app.dependency_overrides[get_sync_db] = override_get_db
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()

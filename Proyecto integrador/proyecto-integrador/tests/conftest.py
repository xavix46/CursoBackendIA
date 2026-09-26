import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.database import Base, get_db
from app.main import app
from app.auth import create_access_token

try:
    from app.models.usuario import Usuario
    from app.models.producto import Producto  # noqa: F401
except ImportError:
    Usuario = None
    Producto = None

# In-memory SQLite for isolated test runs
TEST_DATABASE_URL = "sqlite:///:memory:"

test_engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """Crea una base de datos limpia en memoria para cada test."""
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Cliente de pruebas FastAPI con override de base de datos en memoria."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def make_auth_headers():
    """Generador de cabeceras de autorización Bearer para un usuario dado."""
    def _make(usuario: Usuario) -> dict[str, str]:
        token = create_access_token(data={"sub": usuario.email, "user_id": usuario.id})
        return {"Authorization": f"Bearer {token}"}
    return _make

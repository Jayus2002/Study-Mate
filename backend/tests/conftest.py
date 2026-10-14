import pytest
from fastapi.testclient import TestClient
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool
from backend.app.db.models import Plan, Task
from backend.app.db.session import get_session
from backend.app.main import app

@pytest.fixture
def test_engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )

    SQLModel.metadata.create_all(engine)
    return engine

@pytest.fixture
def session(test_engine):
    with Session(test_engine) as session:
        yield session

@pytest.fixture
def client(test_engine):
    # Override the get_session dependency to use the test database
    def override_get_session():
        with Session(test_engine) as session:
            yield session
    app.dependency_overrides[get_session] = override_get_session
    yield TestClient(app)
    app.dependency_overrides.clear()
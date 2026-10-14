import pytest
from sqlmodel import SQLModel, Session, create_engine
from sqlmodel.pool import StaticPool
from backend.app.db.models import Plan, Task

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
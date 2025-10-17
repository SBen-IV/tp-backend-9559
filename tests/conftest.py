from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from app.api.deps import get_db
from app.core.db import init_db
from app.main import app
from tests.utils.utils import get_cliente_token_headers, get_empleado_token_headers


@pytest.fixture(scope="session", name="session", autouse=True)
def session_fixture() -> Generator[Session, None, None]:
    engine = create_engine(
        "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
    )
    # This creates all models for tests even if there is no version/revision created
    # for a particular class
    SQLModel.metadata.create_all(engine)
    
    connection = engine.connect()
    transaction = connection.begin()
    session = Session(bind=connection)
    
    init_db(session)
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="module", name="client")
def client_fixture(session: Session):
    def get_session_override():
        return session

    app.dependency_overrides[get_db] = get_session_override

    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


@pytest.fixture(scope="module", name="empleado_token_headers")
def empleado_token_headers(client: TestClient) -> dict[str, str]:
    return get_empleado_token_headers(client)


@pytest.fixture(scope="module", name="cliente_token_headers")
def cliente_token_headers(client: TestClient) -> dict[str, str]:
    return get_cliente_token_headers(client)

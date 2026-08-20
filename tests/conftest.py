from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.core.database import SessionLocal
from app.core.security import get_current_tenant
from app.main import app


@pytest.fixture(scope="session")
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def default_tenant_id(db_session):
    from app.models.empresa import Empresa

    empresa = db_session.query(Empresa).filter(Empresa.nome == "Empresa Padrão").first()
    return empresa.id


@pytest.fixture(scope="function")
def client(default_tenant_id) -> Generator[TestClient, None, None]:
    app.dependency_overrides[get_current_tenant] = lambda: default_tenant_id
    with TestClient(app) as c:
        yield c
    # Instead of clear(), we could just pop it, but since tests might use clear() we'll just clear it here too.
    app.dependency_overrides.clear()

import pytest
from fastapi.testclient import TestClient
from typing import Generator

from app.main import app


@pytest.fixture(scope="session")
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as c:
        yield c

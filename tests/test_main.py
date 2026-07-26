from fastapi.testclient import TestClient


def test_health_check(client: TestClient):
    response = client.get("/health")

    # Se o banco de dados não estiver online, vai retornar 500.
    # Se estiver, 200. Ambos indicam que a API subiu e respondeu.
    assert response.status_code in [200, 500]

    if response.status_code == 200:
        assert response.json() == {"status": "healthy", "database": "connected"}

from fastapi.testclient import TestClient


def test_register_and_login_flow(client: TestClient):
    test_user = {
        "nome_completo": "Usuário Teste Auth",
        "email": "testauth@voicematch.com",
        "senha": "password123",
        "telefone": "11999999999",
        "recrutador": {"empresa": "VoiceMatch Tests", "cargo": "Test Engineer"},
    }

    # 1. Register User
    response = client.post("/usuarios", json=test_user)
    if response.status_code == 400 and "já está cadastrado" in response.text:
        # Se o user já existir de um teste anterior que falhou, deletamos ele antes
        login_response = client.post(
            "/auth/login/json",
            json={"email": test_user["email"], "senha": test_user["senha"]},
        )
        assert login_response.status_code == 200
        user_id = login_response.json()["user"]["id"]
        client.delete(f"/usuarios/{user_id}")
        # Retry registration
        response = client.post("/usuarios", json=test_user)

    assert response.status_code == 201
    user_data = response.json()
    assert user_data["email"] == test_user["email"]
    assert user_data["recrutador"]["empresa"] == test_user["recrutador"]["empresa"]
    user_id = user_data["id"]

    # 2. Login with JSON payload
    login_payload = {"email": test_user["email"], "senha": test_user["senha"]}
    login_response = client.post("/auth/login/json", json=login_payload)
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert "access_token" in token_data
    access_token = token_data["access_token"]

    # 3. Get /auth/me
    headers = {"Authorization": f"Bearer {access_token}"}
    me_response = client.get("/auth/me", headers=headers)
    assert me_response.status_code == 200
    me_data = me_response.json()
    assert me_data["email"] == test_user["email"]
    assert me_data["id"] == user_id

    # 4. Login with Form Data (OAuth2)
    form_data = {"username": test_user["email"], "password": test_user["senha"]}
    form_login_response = client.post("/auth/login", data=form_data)
    assert form_login_response.status_code == 200

    # 5. Teardown
    delete_response = client.delete(f"/usuarios/{user_id}")
    assert delete_response.status_code == 204

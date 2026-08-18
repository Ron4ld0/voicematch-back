import uuid

from fastapi.testclient import TestClient


def test_seed_grupos_habilidades_loaded(client: TestClient):
    """
    Verifica se os grupos de habilidades padrão foram criados no lifespan.
    """
    response = client.get("/grupos-habilidades/")
    assert response.status_code == 200
    grupos = response.json()
    assert len(grupos) >= 7

    nomes = [g["nome"] for g in grupos]
    assert "Desenvolvedor Frontend Pleno/Sênior" in nomes
    assert "Desenvolvedor Backend Python" in nomes
    assert "Desenvolvedor Backend Node.js" in nomes
    assert "Engenheiro DevOps & Cloud" in nomes
    assert "Perfil Colaborativo & Ágil" in nomes
    assert "Liderança & Mentoria Técnica" in nomes
    assert "Resolução de Problemas sob Pressão" in nomes


def test_criar_e_obter_grupo_habilidade(client: TestClient):
    """
    Testa criação de um novo grupo com itens associados e busca por ID.
    """
    # 1. Obter habilidades disponíveis para vincular
    habs_resp = client.get("/habilidades/?limit=5")
    assert habs_resp.status_code == 200
    habilidades = habs_resp.json()
    assert len(habilidades) >= 2

    hab_1_id = habilidades[0]["id"]
    hab_2_id = habilidades[1]["id"]

    # 2. Criar novo grupo
    payload = {
        "nome": "Grupo Teste QA Automation",
        "tipo": "HARD",
        "descricao": "Grupo para automação de testes",
        "empresa_id": None,
        "itens": [
            {
                "habilidade_id": hab_1_id,
                "peso": 8,
                "obrigatoriedade": "OBRIGATORIA",
            },
            {
                "habilidade_id": hab_2_id,
                "peso": 6,
                "obrigatoriedade": "DESEJAVEL",
            },
        ],
    }

    create_resp = client.post("/grupos-habilidades/", json=payload)
    assert create_resp.status_code == 201
    created_data = create_resp.json()
    grupo_id = created_data["id"]

    assert created_data["nome"] == payload["nome"]
    assert created_data["tipo"] == "HARD"
    assert len(created_data["itens"]) == 2

    # 3. Obter por ID
    get_resp = client.get(f"/grupos-habilidades/{grupo_id}")
    assert get_resp.status_code == 200
    grupo_detalhes = get_resp.json()
    assert grupo_detalhes["id"] == grupo_id
    assert grupo_detalhes["nome"] == payload["nome"]
    assert len(grupo_detalhes["itens"]) == 2
    assert grupo_detalhes["itens"][0]["habilidade"] is not None

    # Limpeza
    del_resp = client.delete(f"/grupos-habilidades/{grupo_id}")
    assert del_resp.status_code == 204


def test_listar_com_filtros_e_busca(client: TestClient):
    """
    Testa listagem com filtro por tipo HARD / SOFT e busca textual.
    """
    # Filtro HARD
    resp_hard = client.get("/grupos-habilidades/?tipo=HARD")
    assert resp_hard.status_code == 200
    for g in resp_hard.json():
        assert g["tipo"] == "HARD"

    # Filtro SOFT
    resp_soft = client.get("/grupos-habilidades/?tipo=SOFT")
    assert resp_soft.status_code == 200
    for g in resp_soft.json():
        assert g["tipo"] == "SOFT"

    # Busca textual
    resp_busca = client.get("/grupos-habilidades/?busca=Python")
    assert resp_busca.status_code == 200
    grupos_python = resp_busca.json()
    assert any("Python" in g["nome"] for g in grupos_python)


def test_atualizar_grupo_habilidade_e_itens(client: TestClient):
    """
    Testa atualização cadastral e sincronização de itens de um grupo.
    """
    # 1. Buscar habilidades
    habs_resp = client.get("/habilidades/?limit=3")
    habilidades = habs_resp.json()
    assert len(habilidades) >= 3

    # 2. Criar grupo inicial com 1 item
    create_resp = client.post(
        "/grupos-habilidades/",
        json={
            "nome": "Grupo Temp Para Update",
            "tipo": "SOFT",
            "descricao": "Descricao antiga",
            "itens": [
                {
                    "habilidade_id": habilidades[0]["id"],
                    "peso": 5,
                    "obrigatoriedade": "DESEJAVEL",
                }
            ],
        },
    )
    assert create_resp.status_code == 201
    grupo_id = create_resp.json()["id"]

    # 3. Atualizar dados e lista de itens (substituindo por 2 novos itens)
    update_payload = {
        "nome": "Grupo Atualizado com Sucesso",
        "descricao": "Nova descricao atualizada",
        "itens": [
            {
                "habilidade_id": habilidades[1]["id"],
                "peso": 9,
                "obrigatoriedade": "OBRIGATORIA",
            },
            {
                "habilidade_id": habilidades[2]["id"],
                "peso": 7,
                "obrigatoriedade": "DESEJAVEL",
            },
        ],
    }

    update_resp = client.put(f"/grupos-habilidades/{grupo_id}", json=update_payload)
    assert update_resp.status_code == 200
    updated_data = update_resp.json()
    assert updated_data["nome"] == "Grupo Atualizado com Sucesso"
    assert updated_data["descricao"] == "Nova descricao atualizada"
    assert len(updated_data["itens"]) == 2

    # 4. Deletar
    del_resp = client.delete(f"/grupos-habilidades/{grupo_id}")
    assert del_resp.status_code == 204


def test_grupo_habilidade_nao_encontrado(client: TestClient):
    """
    Testa respostas 404 para ID inexistente.
    """
    fake_id = uuid.uuid4()
    assert client.get(f"/grupos-habilidades/{fake_id}").status_code == 404
    assert (
        client.put(f"/grupos-habilidades/{fake_id}", json={"nome": "X"}).status_code
        == 404
    )
    assert client.delete(f"/grupos-habilidades/{fake_id}").status_code == 404

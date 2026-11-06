import pytest
import uuid

@pytest.fixture
def auth_usuario_avaliacao(client):
    """Usuário dono da avaliação"""
    client.post('/auth/register', json={"user": "claralves", "email": "claralves@gmail.com", "password": "romancereal"})
    res = client.post('/auth/login', json={"email": "claralves@gmail.com", "password": "romancereal"})
    return {"Authorization": f"Bearer {res.get_json()['access_token']}"}

@pytest.fixture
def auth_invasor(client):
    """Usuário sem permissão"""
    client.post('/auth/register', json={"user": "claraneves", "email": "claraneves@gmail.com", "password": "claraneves"})
    res = client.post('/auth/login', json={"email": "claraneves@gmail.com", "password": "claraneves"})
    return {"Authorization": f"Bearer {res.get_json()['access_token']}"}

@pytest.fixture
def avaliacao_criada(client, auth_usuario_avaliacao):
    """Cria Artista, Álbum e Avaliação via HTTP para os testes"""
    # 1. Cria Artista
    res_artista = client.post('/artistas/', json={
        "nome": f"Artista_{uuid.uuid4().hex[:6]}",
        "genero": "K-POP",
        "pais": "Coreia do Sul"
    }, headers=auth_usuario_avaliacao)
    assert res_artista.status_code in (200, 201), f"Erro artista: {res_artista.get_data(as_text=True)}"
    artista_id = res_artista.get_json()["artista"]["id"]

    # 2. Cria Álbum
    res_album = client.post('/albuns/', json={
        "titulo": f"Album_{uuid.uuid4().hex[:6]}",
        "ano": 2023,
        "artista_id": artista_id
    }, headers=auth_usuario_avaliacao)
    assert res_album.status_code in (200, 201), f"Erro album: {res_album.get_data(as_text=True)}"
    album_id = res_album.get_json()["album"]["id"]

    # 3. Cria Avaliação
    res_aval = client.post('/avaliacoes/', json={
        "album_id": album_id,
        "nota": 5,
        "comentario": "Obra-prima!",
        "data_escuta": "2026-03-12"
    }, headers=auth_usuario_avaliacao)
    assert res_aval.status_code in (200, 201), f"Erro avaliacao: {res_aval.get_data(as_text=True)}"

    return res_aval.get_json()["avaliacao"]

def test_criar_avaliacao_sucesso(client, auth_usuario_avaliacao):
    res_artista = client.post('/artistas/', json={"nome": f"Art_{uuid.uuid4().hex[:6]}", "genero": "Pop", "pais": "Brasil"}, headers=auth_usuario_avaliacao)
    artista_id = res_artista.get_json()["artista"]["id"]

    res_album = client.post('/albuns/', json={"titulo": f"Alb_{uuid.uuid4().hex[:6]}", "ano": 2022, "artista_id": artista_id}, headers=auth_usuario_avaliacao)
    album_id = res_album.get_json()["album"]["id"]

    payload = {
        "album_id": album_id,
        "nota": 4,
        "comentario": "Muito bom álbum",
        "data_escuta": "2026-03-12"
    }
    response = client.post('/avaliacoes/', json=payload, headers=auth_usuario_avaliacao)

    assert response.status_code in (200, 201)
    assert response.get_json()["message"] == "A avaliação foi criada com sucesso"

def test_obter_todas_avaliacoes(client, auth_usuario_avaliacao, avaliacao_criada):
    response = client.get('/avaliacoes/', headers=auth_usuario_avaliacao)

    assert response.status_code == 200
    dados = response.get_json()
    assert len(dados) >= 1
    assert dados[0]["id"] == avaliacao_criada["id"]

def test_obter_avaliacao_de_outro_usuario(client, auth_invasor, avaliacao_criada):
    """Garante proteção IDOR no GET de avaliação"""
    aval_id = avaliacao_criada["id"]
    response = client.get(f'/avaliacoes/{aval_id}', headers=auth_invasor)

    assert response.status_code == 403
    assert "não tem permissão" in response.get_json()["error"]

def test_editar_avaliacao_de_outro_usuario(client, auth_invasor, avaliacao_criada):
    """Garante proteção IDOR no PUT de avaliação"""
    aval_id = avaliacao_criada["id"]
    payload = {"nota": 1, "comentario": "Tentativa de alteração"}

    response = client.put(f'/avaliacoes/{aval_id}', json=payload, headers=auth_invasor)

    assert response.status_code == 403
    assert "não tem permissão" in response.get_json()["error"]

def test_deletar_avaliacao_de_outro_usuario(client, auth_invasor, avaliacao_criada):
    """Garante proteção IDOR no DELETE de avaliação"""
    aval_id = avaliacao_criada["id"]
    response = client.delete(f'/avaliacoes/{aval_id}', headers=auth_invasor)

    assert response.status_code == 403
    assert "não tem permissão" in response.get_json()["error"]

def test_deletar_avaliacao_sucesso(client, auth_usuario_avaliacao, avaliacao_criada):
    """Garante a exclusão de avaliação pelo próprio dono"""
    aval_id = avaliacao_criada["id"]
    response = client.delete(f'/avaliacoes/{aval_id}', headers=auth_usuario_avaliacao)

    assert response.status_code == 200
    assert "foi deletada com sucesso" in response.get_json()["message"]
import pytest
import uuid

@pytest.fixture
def auth_usuario_artista(client):
    """Usuário que cadastrou artista"""
    client.post('/auth/register', json={"user":"claralves", "email": "claralves@gmail.com", "password": "romancereal"})
    res = client.post('/auth/login', json={"email": "claralves@gmail.com", "password": "romancereal"})
    return {"Authorization": f"Bearer {res.get_json()['access_token']}"}

@pytest.fixture
def auth_invasor(client):
    """Usuario mal intencionado"""
    client.post('/auth/register', json={"user": "clananeves", "email": "claraneves@gmail.com", "password": "claraneves"})
    res = client.post('/auth/login', json={"email": "claraneves@gmail.com", "password": "claraneves"})
    return {"Authorization": f"Bearer {res.get_json()['access_token']}"}

@pytest.fixture
def artista_criado(client, auth_usuario_artista):
    """Criar artista base"""
    nome_unico = f"TWICE_{uuid.uuid4().hex[:6]}"
    payload = {
        "nome": nome_unico,
        "genero": "K-POP",
        "pais": "Coreia do Sul"
    }

    response = client.post('/artistas/', json=payload, headers=auth_usuario_artista)
    assert response.status_code in (200, 201), f"Erro ao criar artista na fixture: {response.get_data(as_text=True)}"

    return response.get_json()["artista"]

def test_criar_artista_sucesso(client, auth_usuario_artista):
    nome_unico = f"NewJeans_{uuid.uuid4().hex[:6]}"
    payload = {
        "nome": nome_unico,
        "genero": "K-POP",
        "pais": "Coreia do Sul"
    }

    response = client.post('/artistas/', json=payload, headers=auth_usuario_artista)
    assert response.status_code in (200, 201)
    assert response.get_json()["message"] == "O artista foi criado com sucesso"

def test_obter_todos_artistas(client, auth_usuario_artista, artista_criado):
    response = client.get('/artistas/', headers=auth_usuario_artista)

    assert response.status_code == 200
    dados = response.get_json()
    assert len(dados) >= 1
    assert dados[0]["id"] == artista_criado["id"]

def test_artista_criado_por_outro_usuario(client, auth_invasor, artista_criado):
    """Garante que ninguem pode acessar artistas de outros usuarios"""
    artista_id = artista_criado["id"]
    response = client.get(f'/artistas/{artista_id}', headers=auth_invasor)

    assert response.status_code == 403
    assert "não tem permissão" in response.get_json()["error"]

def editar_artista_outro_usuario(client, auth_invasor, artista_criado):
    """Garante que ninguem possa editar artistas de outros usuários"""
    artista_id = artista_criado["id"]
    payload = {"nome": "BlackPink"}

    response = client.put(f'/artistas/{artista_id}', json=payload, headers=auth_invasor)
    assert response.status_code == 403
    assert "não tem permissão" in response.get_json()["error"]

def test_deletar_artista_de_outro_usuario(client, auth_invasor, artista_criado):
    artista_id = artista_criado["id"]
    response = client.delete(f'/artistas/{artista_id}', headers=auth_invasor)

    assert response.status_code == 403
    assert "não tem permissão" in response.get_json()["error"]


def test_deletar_artistas_sucesso(client, auth_usuario_artista, artista_criado):
    artista_id = artista_criado["id"]
    response = client.delete(f'/artistas/{artista_id}', headers=auth_usuario_artista)

    assert response.status_code == 200
    assert "deletados com sucesso" in response.get_json()["mensagem"]
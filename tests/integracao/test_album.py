import pytest
import uuid

@pytest.fixture
def auth_user_dono(client):
    """Usuário dono do album"""
    client.post('/auth/register', json={"user": "claralves", "email":"claralves@gmail.com", "password": "romancereal"})
    res = client.post('/auth/login', json={"email": "claralves@gmail.com", "password": "romancereal"})
    return {"Authorization": f"Bearer {res.get_json()['access_token']}"}

@pytest.fixture
def auth_user_invasor(client):
    """Usuário mal intencionado"""
    client.post('/auth/register', json={"user": "claraneves", "email": "claraneves@gmail.com", "password": "claraneves"})
    res = client.post('/auth/login', json={"email": "claraneves@gmail.com", "password": "claraneves"})
    return {"Authorization": f"Bearer {res.get_json()['access_token']}"}

@pytest.fixture
def album_criado(client, auth_user_dono):
    nome_unico = f"TWICE_{uuid.uuid4().hex[:6]}"
    payload_artista = {
        "nome": nome_unico,
        "genero": "K-POP",
        "pais": "Coreia do Sul"
    }

    res_artista = client.post('/artistas/', json=payload_artista, headers=auth_user_dono)
    assert res_artista.status_code in (200, 201), f"Erro ao criar artista: {res_artista.get_data(as_text=True)}"

    artista_id = res_artista.get_json()["artista"]["id"]

    payload_album = {
        "titulo": f"Album_{uuid.uuid4().hex[:6]}",
        "ano": 2021,
        "artista_id": artista_id
    }

    res_album = client.post('/albuns/', json=payload_album, headers=auth_user_dono)
    assert res_album.status_code in (200, 201), f"Erro ao criar album na fixture: {res_album.get_data(as_text=True)}"

    return res_album.get_json().get("album")

def test_criar_album_sucesso(client, auth_user_dono):
    nome_unico = f"NewJeans_{uuid.uuid4().hex[:6]}"

    res_artista = client.post('/artistas/', json={"nome": nome_unico, "genero": "K-POP", "pais": "Coreia do Sul"}, headers=auth_user_dono)

    assert res_artista.status_code in (200, 201), f"Erro ao criar artista no teste: {res_artista.get_data(as_ext=True)}"
    
    artista_id = res_artista.get_json()["artista"]["id"]

    payload = {
        "titulo": f"Get_Up_{uuid.uuid4().hex[:6]}",
        "ano": 2023,
        "artista_id": artista_id
    }
    response = client.post('/albuns/', json=payload, headers=auth_user_dono)

    assert response.status_code in (200, 201)
    assert response.get_json()["message"] == "O álbum foi criado com sucesso"

def test_obter_todos_albuns(client, auth_user_dono, album_criado):
    response = client.get('/albuns/', headers=auth_user_dono)

    assert response.status_code == 200
    dados = response.get_json()
    assert len(dados) >= 1
    assert dados[0]["id"] == album_criado["id"]

def test_obter_album_de_outro_usuario(client, auth_user_invasor, album_criado):
    """Garante que ninguem possa acessar albuns de outros usuários"""
    album_id = album_criado["id"]
    response = client.get(f'/albuns/{album_id}', headers=auth_user_invasor)

    assert response.status_code == 403
    assert "não tem permissão" in response.get_json()["error"]

def test_editar_album_de_outro_usuario(client, auth_user_invasor, album_criado):
    """Garante que outro usuario não consigo editar albuns"""
    album_id = album_criado["id"]
    payload = {"titulo": "Ditto"}

    response = client.put(f'/albuns/{album_id}', json=payload, headers=auth_user_invasor)

    assert response.status_code == 403
    assert "não tem permissão" in response.get_json()["error"]

def test_deletar_album_outro_usuario(client, auth_user_invasor, album_criado):
    """Garante que outro usuário não delete um album que não pertence a ele"""
    album_id = album_criado["id"]
    response = client.delete(f'/albuns/{album_id}', headers=auth_user_invasor)

    assert response.status_code == 403
    assert "não tem permissão" in response.get_json()["error"]

def test_deletar_album_sucesso(client, auth_user_dono, album_criado):
    """Garante que o dono do album consiga deletar seu album"""
    album_id = album_criado["id"]
    response = client.delete(f'/albuns/{album_id}', headers=auth_user_dono)

    assert response.status_code == 200
    assert "deletado com sucesso" in response.get_json()["message"]
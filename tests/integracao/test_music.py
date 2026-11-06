import pytest
import uuid

@pytest.fixture
def auth_usuario_musica(client):
    """Usuário que cadastrou a música"""
    client.post('/auth/register', json={"user": "claralves", "email": "claralves@gmail.com", "password": "romancereal"})
    res = client.post('/auth/login', json={"email": "claralves@gmail.com", "password": "romancereal"})
    return {"Authorization": f"Bearer {res.get_json()['access_token']}"}

@pytest.fixture
def auth_invasor(client):
    """Usuário maldoso"""
    client.post('/auth/register', json={"user": "claraneves", "email": "claraneves@gmail.com", "password": "claraneves"})
    res = client.post('/auth/login', json={"email": "claraneves@gmail.com", "password": "claraneves"})
    return {"Authorization": f"Bearer {res.get_json()['access_token']}"}

@pytest.fixture
def musica_criada(client, auth_usuario_musica):
    res_artista = client.post('/artistas/', json={"nome": f"Artista_{uuid.uuid4().hex[:6]}", "genero": "K-POP", "pais": "Coreia do Sul"}, headers=auth_usuario_musica)
    
    assert res_artista.status_code in (200, 201), f"Erro artista: {res_artista.get_data(as_text=True)}"
    artista_id = res_artista.get_json()["artista"]["id"]

    res_album = client.post('/albuns/', json={"titulo": f"Album_{uuid.uuid4().hex[:6]}", "ano": 2023, "artista_id": artista_id}, headers=auth_usuario_musica)
    assert res_album.status_code in (200, 201), f"Erro album: {res_album.get_data(as_text=True)}"
    album_id = res_album.get_json()["album"]["id"]

    res_musica = client.post('/musicas/', json={"titulo": f"Super Shy_{uuid.uuid4().hex[:6]}", "duracao": "3:15", "album_id": album_id, "artista_id": artista_id }, headers=auth_usuario_musica)
    assert res_musica.status_code in (200, 201), f"Erro musica: {res_musica.get_data(as_text=True)}"

    return res_musica.get_json()["musica"]

def test_criar_musica_sucesso(client, auth_usuario_musica):
    res_artista = client.post('/artistas/', json={"nome": f"Art_{uuid.uuid4().hex[:6]}", "genero": "Pop", "pais": "Brasil"}, headers=auth_usuario_musica)
    artista_id = res_artista.get_json()["artista"]["id"]

    res_album = client.post('/albuns/', json={"titulo": f"Alb_{uuid.uuid4().hex[:6]}", "ano": 2022, "artista_id": artista_id}, headers=auth_usuario_musica)
    album_id = res_album.get_json()["album"]["id"]

    payload = {
        "titulo": f"Musica_{uuid.uuid4().hex[:6]}",
        "duracao": "3:22",
        "album_id": album_id,
        "artista_id": artista_id
    }
    response = client.post('/musicas/', json=payload, headers=auth_usuario_musica)

    assert response.status_code in (200, 201)
    assert response.get_json()["message"] == "A música foi criada com sucesso"

def test_obter_todas_musicas(client, auth_usuario_musica, musica_criada):
    response = client.get('/musicas/', headers=auth_usuario_musica)

    assert response.status_code == 200
    dados = response.get_json()
    assert len(dados) >= 1
    assert dados[0]["id"] == musica_criada["id"]

def test_obter_musica_de_outro_usuario(client, auth_invasor, musica_criada):
    """Garante que ninguem possa ver as musicas cadastradas de outro usuário"""
    musica_id = musica_criada["id"]
    response = client.get(f'/musicas/{musica_id}', headers=auth_invasor)

    assert response.status_code == 403
    assert "não tem permissão" in response.get_json()["error"]

def test_editar_musica_de_outro_usuario(client, auth_invasor, musica_criada):
    """Garante que ninguem pode editar a musica além de quem a cadastrou"""
    musica_id = musica_criada["id"]
    payload = {"titulo": "Hacked Song"}

    response = client.put(f'/musicas/{musica_id}', json=payload, headers=auth_invasor)

    assert response.status_code == 403
    assert "não tem permissão" in response.get_json()["error"]

def test_deletar_musica_de_outro_usuario(client, auth_invasor, musica_criada):
    """Garante que ninguem além de quem cadastrou pode deletar a música"""
    musica_id = musica_criada["id"]
    response = client.delete(f'/musicas/{musica_id}', headers=auth_invasor)

    assert response.status_code == 403
    assert "não tem permissão" in response.get_json()["error"]

def test_deletar_musica_sucesso(client, auth_usuario_musica, musica_criada):
    """Garante que o dono consiga deletar sua música"""
    musica_id = musica_criada["id"]
    response = client.delete(f'/musicas/{musica_id}', headers=auth_usuario_musica)

    assert response.status_code == 200
    assert "foi deletada com sucesso" in response.get_json()["message"]
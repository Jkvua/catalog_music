import pytest

@pytest.fixture
def auth_user_dono(client):
    """Autentica o usuário proprietário do álbum."""
    # Arrange
    payload = {
        "user": "claralves",
        "email": "claralves@gmail.com",
        "password": "romancereal"
    }
    # Act
    registro = client.post("/auth/register", json=payload)
    assert registro.status_code == 201
    login = client.post(
        "/auth/login",
        json={
            "email": payload["email"],
            "password": payload["password"]
        }
    )
    # Assert
    assert login.status_code == 200
    token = login.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def auth_user_invasor(client):
    """Autentica um segundo usuário para verificar permissões."""
    # Arrange
    payload = {
        "user": "claraneves",
        "email": "claraneves@gmail.com",
        "password": "claraneves"
    }
    # Act
    registro = client.post("/auth/register", json=payload)
    assert registro.status_code == 201
    login = client.post(
        "/auth/login",
        json={
            "email": payload["email"],
            "password": payload["password"]
        }
    )
    # Assert
    assert login.status_code == 200
    token = login.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def artista_criado(client, auth_user_dono):
    """Cria um artista pertencente ao usuário autenticado."""
    # Arrange
    payload = {
        "nome": "TWICE",
        "genero": "K-POP",
        "pais": "Coreia do Sul"
    }
    # Act
    resposta = client.post(
        "/artistas/",
        json=payload,
        headers=auth_user_dono
    )
    # Assert
    assert resposta.status_code == 201, (
        resposta.get_data(as_text=True)
    )
    return resposta.get_json()["artista"]

@pytest.fixture
def album_criado(client, auth_user_dono, artista_criado):
    """Cria um álbum pertencente ao usuário autenticado."""
    # Arrange
    payload = {
        "titulo": "Formula of Love",
        "ano": 2021,
        "artista_id": artista_criado["id"]
    }
    # Act
    resposta = client.post(
        "/albuns/",
        json=payload,
        headers=auth_user_dono
    )
    # Assert
    assert resposta.status_code == 201, (
        resposta.get_data(as_text=True)
    )
    return resposta.get_json()["album"]

def test_criar_album_sucesso(client, auth_user_dono, artista_criado):
    """Verifica a criação de um álbum com dados válidos."""
    # Arrange
    payload = {
        "titulo": "Get Up",
        "ano": 2023,
        "artista_id": artista_criado["id"]
    }
    # Act
    resposta = client.post(
        "/albuns/",
        json=payload,
        headers=auth_user_dono
    )
    # Assert
    assert resposta.status_code == 201
    dados = resposta.get_json()
    assert dados["message"] == "O álbum foi criado com sucesso"
    assert dados["album"]["titulo"] == payload["titulo"]

def test_obter_todos_albuns(client, auth_user_dono, album_criado):
    """Verifica se o álbum aparece na listagem do proprietário."""
    # Arrange
    album_id = album_criado["id"]
    # Act
    resposta = client.get(
        "/albuns/",
        headers=auth_user_dono
    )
    # Assert
    assert resposta.status_code == 200
    dados = resposta.get_json()
    assert isinstance(dados, list)
    assert any(album["id"] == album_id for album in dados)

def test_obter_album_de_outro_usuario(client, auth_user_invasor, album_criado):
    """Impede a consulta de álbuns pertencentes a outro usuário."""
    # Arrange
    album_id = album_criado["id"]
    # Act
    resposta = client.get(
        f"/albuns/{album_id}",
        headers=auth_user_invasor
    )
    # Assert
    assert resposta.status_code == 403
    assert "não tem permissão" in resposta.get_json()["error"]

def test_editar_album_sucesso(client, auth_user_dono, album_criado):
    """Verifica se o proprietário consegue editar seu álbum."""
    # Arrange
    album_id = album_criado["id"]
    payload = {
        "titulo": "Formula of Love - Special Edition"
    }
    # Act
    resposta = client.put(
        f"/albuns/{album_id}",
        json=payload,
        headers=auth_user_dono
    )
    # Assert
    assert resposta.status_code == 200

    consulta = client.get(
        f"/albuns/{album_id}",
        headers=auth_user_dono
    )

    assert consulta.status_code == 200

    dados = consulta.get_json()

    assert dados["titulo"] == payload["titulo"]


def test_editar_album_de_outro_usuario(
    client, auth_user_invasor, album_criado
):
    """Impede a edição de álbuns pertencentes a outro usuário."""
    # Arrange
    album_id = album_criado["id"]
    payload = {
        "titulo": "Ditto"
    }
    # Act
    resposta = client.put(
        f"/albuns/{album_id}",
        json=payload,
        headers=auth_user_invasor
    )
    # Assert
    assert resposta.status_code == 403
    assert "não tem permissão" in resposta.get_json()["error"]

def test_deletar_album_de_outro_usuario(client, auth_user_invasor, album_criado):
    """Impede a exclusão de álbuns pertencentes a outro usuário."""
    # Arrange
    album_id = album_criado["id"]
    # Act
    resposta = client.delete(
        f"/albuns/{album_id}",
        headers=auth_user_invasor
    )
    # Assert
    assert resposta.status_code == 403
    assert "não tem permissão" in resposta.get_json()["error"]

def test_deletar_album_sucesso(client, auth_user_dono, album_criado):
    """Verifica se o proprietário consegue excluir seu álbum."""
    # Arrange
    album_id = album_criado["id"]
    # Act
    resposta = client.delete(
        f"/albuns/{album_id}",
        headers=auth_user_dono
    )
    # Assert
    assert resposta.status_code == 200
    assert "deletado com sucesso" in resposta.get_json()["message"]

    consulta = client.get(
        f"/albuns/{album_id}",
        headers=auth_user_dono
    )
    assert consulta.status_code == 404
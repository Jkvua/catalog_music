import pytest

@pytest.fixture
def auth_usuario_musica(client):
    """Autentica o usuário proprietário dos registros."""
    # Arrange
    payload = {
        "user": "usuario_musica", "email": "usuario_musica@teste.com", "password": "senha_teste_123"}
    # Act
    registro = client.post("/auth/register", json=payload)
    # Assert
    assert registro.status_code == 201, (registro.get_data(as_text=True))
    login = client.post("/auth/login", json={"email": payload["email"], "password": payload["password"]})

    assert login.status_code == 200
    token = login.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def auth_invasor(client):
    """Autentica um segundo usuário para verificar permissões."""
    # Arrange
    payload = {"user": "usuario_invasor", "email": "usuario_invasor@teste.com", "password": "senha_invasor_123"}
    # Act
    registro = client.post("/auth/register", json=payload)
    # Assert
    assert registro.status_code == 201, ( registro.get_data(as_text=True))
    login = client.post("/auth/login", json={"email": payload["email"], "password": payload["password"]})

    assert login.status_code == 200
    token = login.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def artista_criado(client, auth_usuario_musica):
    """Cria um artista pertencente ao usuário autenticado."""
    # Arrange
    payload = {"nome": "NewJeans", "genero": "K-POP", "pais": "Coreia do Sul"}
    # Act
    resposta = client.post("/artistas/", json=payload, headers=auth_usuario_musica)
    # Assert
    assert resposta.status_code == 201, ( resposta.get_data(as_text=True))
    return resposta.get_json()["artista"]

@pytest.fixture
def album_criado(client, auth_usuario_musica, artista_criado):
    """Cria um álbum associado ao artista do usuário."""
    # Arrange
    payload = {"titulo": "Get Up", "ano": 2023, "artista_id": artista_criado["id"]}
    # Act
    resposta = client.post("/albuns/", json=payload, headers=auth_usuario_musica)
    # Assert
    assert resposta.status_code == 201, (resposta.get_data(as_text=True))
    return resposta.get_json()["album"]

@pytest.fixture
def musica_criada(client, auth_usuario_musica, album_criado):
    """Cria uma música associada ao álbum do usuário."""
    # Arrange
    payload = {"titulo": "Super Shy", "duracao": "03:15", "album_id": album_criado["id"]}
    # Act
    resposta = client.post("/musicas/", json=payload, headers=auth_usuario_musica)
    # Assert
    assert resposta.status_code == 201, (resposta.get_data(as_text=True))
    return resposta.get_json()["musica"]

def test_criar_musica_sucesso(client, auth_usuario_musica, album_criado):
    """Verifica a criação de uma música com dados válidos."""
    # Arrange
    payload = { "titulo": "ETA", "duracao": "03:22", "album_id": album_criado["id"]}
    # Act
    resposta = client.post("/musicas/", json=payload, headers=auth_usuario_musica)
    # Assert
    assert resposta.status_code == 201
    dados = resposta.get_json()

    assert dados["message"] == "A música foi criada com sucesso"
    assert dados["musica"]["titulo"] == payload["titulo"]
    assert dados["musica"]["duracao"] == payload["duracao"]

def test_criar_musica_sem_autenticacao(client, album_criado):
    """Impede a criação de músicas sem autenticação JWT."""
    # Arrange
    payload = {"titulo": "Musica sem autenticacao", "duracao": "03:22", "album_id": album_criado["id"]}
    # Act
    resposta = client.post("/musicas/", json=payload)
    # Assert
    assert resposta.status_code == 401

def test_criar_musica_album_de_outro_usuario(client, auth_invasor, album_criado):
    """Impede a criação de músicas em álbuns de terceiros."""
    # Arrange
    payload = {"titulo": "Musica nao autorizada", "duracao": "03:22", "album_id": album_criado["id"]}
    # Act
    resposta = client.post("/musicas/", json=payload, headers=auth_invasor)
    # Assert
    assert resposta.status_code == 404

def test_obter_todas_musicas(client, auth_usuario_musica, musica_criada):
    """Verifica se a música aparece na listagem do proprietário."""
    # Arrange
    musica_id = musica_criada["id"]
    # Act
    resposta = client.get("/musicas/", headers=auth_usuario_musica)
    # Assert
    assert resposta.status_code == 200
    dados = resposta.get_json()

    assert isinstance(dados, list)
    assert any(musica["id"] == musica_id for musica in dados)

def test_obter_musica_de_outro_usuario(client, auth_invasor, musica_criada):
    """Impede a consulta de músicas pertencentes a outro usuário."""
    # Arrange
    musica_id = musica_criada["id"]
    # Act
    resposta = client.get(f"/musicas/{musica_id}", headers=auth_invasor)
    # Assert
    assert resposta.status_code == 403
    assert "não tem permissão" in resposta.get_json()["error"]

def test_editar_musica_sucesso(client, auth_usuario_musica, musica_criada):
    """Verifica se o proprietário consegue editar sua música."""
    # Arrange
    musica_id = musica_criada["id"]
    payload = {"titulo": "Super Shy Remix", "duracao": "04:10"}
    # Act
    resposta = client.put(f"/musicas/{musica_id}", json=payload, headers=auth_usuario_musica)
    # Assert
    assert resposta.status_code == 200
    consulta = client.get(f"/musicas/{musica_id}", headers=auth_usuario_musica)

    assert consulta.status_code == 200
    dados = consulta.get_json()

    assert dados["titulo"] == payload["titulo"]
    assert dados["duracao"] == payload["duracao"]

def test_editar_musica_de_outro_usuario(client, auth_invasor, musica_criada):
    """Impede a edição de músicas pertencentes a outro usuário."""
    # Arrange
    musica_id = musica_criada["id"]
    payload = { "titulo": "Hacked Song"}
    # Act
    resposta = client.put(f"/musicas/{musica_id}", json=payload, headers=auth_invasor)
    # Assert
    assert resposta.status_code == 403
    assert "não tem permissão" in resposta.get_json()["error"]

def test_deletar_musica_de_outro_usuario(client, auth_invasor, musica_criada):
    """Impede a exclusão de músicas pertencentes a outro usuário."""
    # Arrange
    musica_id = musica_criada["id"]
    # Act
    resposta = client.delete(f"/musicas/{musica_id}", headers=auth_invasor)
    # Assert
    assert resposta.status_code == 403
    assert "não tem permissão" in resposta.get_json()["error"]

def test_deletar_musica_sucesso(client, auth_usuario_musica, musica_criada):
    """Verifica se o proprietário consegue excluir sua música."""
    # Arrange
    musica_id = musica_criada["id"]
    # Act
    resposta = client.delete(f"/musicas/{musica_id}", headers=auth_usuario_musica)
    # Assert
    assert resposta.status_code == 200
    assert "foi deletada com sucesso" in resposta.get_json()["message"]

    consulta = client.get(f"/musicas/{musica_id}", headers=auth_usuario_musica)
    assert consulta.status_code == 404
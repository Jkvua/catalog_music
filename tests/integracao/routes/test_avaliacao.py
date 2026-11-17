import pytest

@pytest.fixture
def auth_usuario_avaliacao(client):
    """Autentica o usuário proprietário da avaliação."""
    # Arrange
    payload = {"user": "claralves", "email": "claralves@gmail.com", "password": "romancereal"}
    # Act
    registro = client.post("/auth/register", json=payload)
    assert registro.status_code == 201
    login = client.post("/auth/login", json={ "email": payload["email"], "password": payload["password"]})
    # Assert
    assert login.status_code == 200
    token = login.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def auth_invasor(client):
    """Autentica outro usuário para verificar permissões."""
    # Arrange
    payload = { "user": "claraneves", "email": "claraneves@gmail.com", "password": "claraneves"}
    # Act
    registro = client.post("/auth/register", json=payload)
    assert registro.status_code == 201
    login = client.post("/auth/login", json={"email": payload["email"], "password": payload["password"]})
    # Assert
    assert login.status_code == 200
    token = login.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def artista_criado(client, auth_usuario_avaliacao):
    """Cria um artista pertencente ao usuário autenticado."""
    # Arrange
    payload = {"nome": "TWICE", "genero": "K-POP", "pais": "Coreia do Sul"}
    # Act
    resposta = client.post("/artistas/", json=payload, headers=auth_usuario_avaliacao)
    # Assert
    assert resposta.status_code == 201, (resposta.get_data(as_text=True))
    return resposta.get_json()["artista"]

@pytest.fixture
def album_criado(client, auth_usuario_avaliacao, artista_criado):
    """Cria um álbum associado ao artista do usuário."""
    # Arrange
    payload = { "titulo": "Formula of Love", "ano": 2021, "artista_id": artista_criado["id"]}
    # Act
    resposta = client.post( "/albuns/", json=payload, headers=auth_usuario_avaliacao)
    # Assert
    assert resposta.status_code == 201, ( resposta.get_data(as_text=True) )
    return resposta.get_json()["album"]

@pytest.fixture
def avaliacao_criada(client, auth_usuario_avaliacao, album_criado):
    """Cria uma avaliação pertencente ao usuário autenticado."""
    # Arrange
    payload = {"album_id": album_criado["id"], "nota": 5, "comentario": "Obra-prima!", "data_escuta": "2026-03-12"}
    # Act
    resposta = client.post("/avaliacoes/", json=payload, headers=auth_usuario_avaliacao)
    # Assert
    assert resposta.status_code == 201, ( resposta.get_data(as_text=True))
    return resposta.get_json()["avaliacao"]

def test_criar_avaliacao_sucesso(client, auth_usuario_avaliacao, album_criado):
    """Verifica a criação de uma avaliação com dados válidos."""
    # Arrange
    payload = {"album_id": album_criado["id"], "nota": 4, "comentario": "Muito bom álbum", "data_escuta": "2026-03-12"}
    # Act
    resposta = client.post("/avaliacoes/", json=payload, headers=auth_usuario_avaliacao)
    # Assert
    assert resposta.status_code == 201
    dados = resposta.get_json()

    assert dados["message"] == "A avaliação foi criada com sucesso"
    assert dados["avaliacao"]["nota"] == payload["nota"]
    assert dados["avaliacao"]["comentario"] == payload["comentario"]

def test_obter_todas_avaliacoes( client, auth_usuario_avaliacao, avaliacao_criada):
    """Verifica se a avaliação aparece na listagem do proprietário."""
    # Arrange
    avaliacao_id = avaliacao_criada["id"]
    # Act
    resposta = client.get("/avaliacoes/", headers=auth_usuario_avaliacao)
    # Assert
    assert resposta.status_code == 200
    dados = resposta.get_json()

    assert isinstance(dados, list)
    assert any(avaliacao["id"] == avaliacao_id for avaliacao in dados)

def test_obter_avaliacao_de_outro_usuario(client, auth_invasor, avaliacao_criada):
    """Impede a consulta de avaliações pertencentes a outro usuário."""
    # Arrange
    avaliacao_id = avaliacao_criada["id"]
    # Act
    resposta = client.get(f"/avaliacoes/{avaliacao_id}", headers=auth_invasor)
    # Assert
    assert resposta.status_code == 403
    assert "não tem permissão" in resposta.get_json()["error"]

def test_editar_avaliacao_sucesso(client, auth_usuario_avaliacao, avaliacao_criada):
    """Verifica se o proprietário consegue editar sua avaliação."""
    # Arrange
    avaliacao_id = avaliacao_criada["id"]
    payload = {"nota": 3, "comentario": "Minha opinião mudou"}
    # Act
    resposta = client.put(f"/avaliacoes/{avaliacao_id}", json=payload, headers=auth_usuario_avaliacao)
    # Assert
    assert resposta.status_code == 200
    consulta = client.get(f"/avaliacoes/{avaliacao_id}", headers=auth_usuario_avaliacao)

    assert consulta.status_code == 200
    dados = consulta.get_json()

    assert dados["nota"] == payload["nota"]
    assert dados["comentario"] == payload["comentario"]

def test_editar_avaliacao_de_outro_usuario(client, auth_invasor, avaliacao_criada):
    """Impede a edição de avaliações pertencentes a outro usuário."""
    # Arrange
    avaliacao_id = avaliacao_criada["id"]
    payload = {"nota": 1, "comentario": "Tentativa de alteração"}
    # Act
    resposta = client.put(f"/avaliacoes/{avaliacao_id}", json=payload, headers=auth_invasor)
    # Assert
    assert resposta.status_code == 403
    assert "não tem permissão" in resposta.get_json()["error"]

def test_deletar_avaliacao_de_outro_usuario(client, auth_invasor, avaliacao_criada):
    """Impede a exclusão de avaliações pertencentes a outro usuário."""
    # Arrange
    avaliacao_id = avaliacao_criada["id"]
    # Act
    resposta = client.delete(f"/avaliacoes/{avaliacao_id}", headers=auth_invasor)
    # Assert
    assert resposta.status_code == 403
    assert "não tem permissão" in resposta.get_json()["error"]

def test_deletar_avaliacao_sucesso(client, auth_usuario_avaliacao, avaliacao_criada):
    """Verifica se o proprietário consegue excluir sua avaliação."""
    # Arrange
    avaliacao_id = avaliacao_criada["id"]
    # Act
    resposta = client.delete(f"/avaliacoes/{avaliacao_id}", headers=auth_usuario_avaliacao)
    # Assert
    assert resposta.status_code == 200
    assert "foi deletada com sucesso" in resposta.get_json()["message"]

    consulta = client.get(f"/avaliacoes/{avaliacao_id}", headers=auth_usuario_avaliacao)
    assert consulta.status_code == 404
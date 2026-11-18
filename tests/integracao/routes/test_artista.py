import pytest

@pytest.fixture
def auth_usuario_artista(client):
    """Autentica o usuário proprietário dos artistas."""
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
    payload = {"user": "claraneves", "email": "claraneves@gmail.com", "password": "claraneves"}
    # Act
    registro = client.post("/auth/register", json=payload)
    assert registro.status_code == 201
    login = client.post("/auth/login", json={"email": payload["email"], "password": payload["password"]})
    # Assert
    assert login.status_code == 200
    token = login.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def artista_criado(client, auth_usuario_artista):
    """Cria um artista pertencente ao usuário autenticado."""
    # Arrange
    payload = { "nome": "TWICE", "genero": "K-POP", "pais": "Coreia do Sul"}
    # Act
    resposta = client.post("/artistas/", json=payload, headers=auth_usuario_artista)
    # Assert
    assert resposta.status_code == 201, (resposta.get_data(as_text=True))
    return resposta.get_json()["artista"]

def test_criar_artista_sucesso(client, auth_usuario_artista):
    """Verifica a criação de um artista com dados válidos."""
    # Arrange
    payload = {"nome": "NewJeans", "genero": "K-POP", "pais": "Coreia do Sul"}
    # Act
    resposta = client.post("/artistas/", json=payload, headers=auth_usuario_artista)
    # Assert
    assert resposta.status_code == 201
    dados = resposta.get_json()

    assert dados["message"] == "O artista foi criado com sucesso"
    assert dados["artista"]["nome"] == payload["nome"]

def test_obter_todos_artistas(client, auth_usuario_artista, artista_criado):
    """Verifica se o artista aparece na listagem do proprietário."""
    # Arrange
    artista_id = artista_criado["id"]
    # Act
    resposta = client.get("/artistas/", headers=auth_usuario_artista)
    # Assert
    assert resposta.status_code == 200
    dados = resposta.get_json()

    assert isinstance(dados, list)
    assert any(artista["id"] == artista_id for artista in dados)

def test_obter_artista_de_outro_usuario(client, auth_invasor, artista_criado):
    """Impede a consulta de artistas pertencentes a outro usuário."""
    # Arrange
    artista_id = artista_criado["id"]
    # Act
    resposta = client.get(f"/artistas/{artista_id}", headers=auth_invasor)
    # Assert
    assert resposta.status_code == 403
    assert "não tem permissão" in resposta.get_json()["error"]

def test_editar_artista_sucesso(client, auth_usuario_artista, artista_criado):
    """Verifica se o proprietário consegue editar seu artista."""
    # Arrange
    artista_id = artista_criado["id"]
    payload = {"nome": "TWICE Updated", "genero": "Pop"}
    # Act
    resposta = client.put(f"/artistas/{artista_id}", json=payload, headers=auth_usuario_artista)
    # Assert
    assert resposta.status_code == 200
    consulta = client.get( f"/artistas/{artista_id}", headers=auth_usuario_artista)

    assert consulta.status_code == 200
    dados = consulta.get_json()

    assert dados["nome"] == payload["nome"]
    assert dados["genero"] == payload["genero"]

def test_editar_artista_de_outro_usuario(client, auth_invasor, artista_criado):
    """Impede a edição de artistas pertencentes a outro usuário."""
    # Arrange
    artista_id = artista_criado["id"]
    payload = {"nome": "BlackPink"}
    # Act
    resposta = client.put(f"/artistas/{artista_id}", json=payload, headers=auth_invasor)
    # Assert
    assert resposta.status_code == 403
    assert "não tem permissão" in resposta.get_json()["error"]

def test_deletar_artista_de_outro_usuario(client, auth_invasor, artista_criado):
    """Impede a exclusão de artistas pertencentes a outro usuário."""
    # Arrange
    artista_id = artista_criado["id"]
    # Act
    resposta = client.delete(f"/artistas/{artista_id}", headers=auth_invasor)
    # Assert
    assert resposta.status_code == 403
    assert "não tem permissão" in resposta.get_json()["error"]

def test_deletar_artista_sucesso(client, auth_usuario_artista, artista_criado):
    """Verifica se o proprietário consegue excluir seu artista."""
    # Arrange
    artista_id = artista_criado["id"]
    # Act
    resposta = client.delete(f"/artistas/{artista_id}", headers=auth_usuario_artista)
    # Assert
    assert resposta.status_code == 200
    assert "deletados com sucesso" in resposta.get_json()["mensagem"]

    consulta = client.get(f"/artistas/{artista_id}", headers=auth_usuario_artista)
    assert consulta.status_code == 404

def test_criar_artista_sem_json(client, auth_usuario_artista):
    """Verifica se a criação rejeita uma requisição sem JSON."""
    # Arrange
    headers = auth_usuario_artista
    # Act
    resposta = client.post("/artistas/", headers=headers)
    # Assert
    assert resposta.status_code == 400
    assert resposta.get_json()["error"] == (
        "Os dados do artista devem ser enviados em um objeto JSON válido")
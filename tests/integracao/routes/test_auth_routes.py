import pytest

@pytest.fixture
def payload_usuario():
    """Fornece os dados de um usuário para os testes."""
    return {"user": "Jkvua", "email": "camilalmeida@gmail.com", "password": "senhaSeCreta123"}

@pytest.fixture
def usuario_cadastro(client, payload_usuario):
    """Cadastra um usuário para os testes de autenticação."""
    # Arrange
    payload = payload_usuario
    # Act
    resposta = client.post("/auth/register", json=payload)
    # Assert
    assert resposta.status_code == 201, (resposta.get_data(as_text=True))
    return payload

def test_registro_usuario_sucesso(client, payload_usuario):
    """Verifica o cadastro de um usuário com dados válidos."""
    # Arrange
    payload = payload_usuario
    # Act
    resposta = client.post("/auth/register", json=payload)
    # Assert
    assert resposta.status_code == 201
    dados = resposta.get_json()
    assert "id" in dados or "message" in dados

def test_login_usuario_sucesso(client, usuario_cadastro):
    """Verifica o login com credenciais válidas."""
    # Arrange
    payload = {"email": usuario_cadastro["email"], "password": usuario_cadastro["password"]}
    # Act
    resposta = client.post( "/auth/login", json=payload)
    # Assert
    assert resposta.status_code == 200
    dados = resposta.get_json()

    assert "access_token" in dados
    assert isinstance(dados["access_token"], str)
    assert dados["access_token"]

def test_login_senha_invalida(client, usuario_cadastro):
    """Verifica a rejeição de uma senha incorreta."""
    # Arrange
    payload = {"email": usuario_cadastro["email"], "password": "senhamuitoErrada21"}
    # Act
    resposta = client.post("/auth/login", json=payload)
    # Assert
    assert resposta.status_code == 401

def test_login_usuario_nao_cadastrado(client):
    """Verifica a rejeição de um usuário inexistente."""
    # Arrange
    payload = {"email": "walter@sales.com", "password": "aindaestouaqui"}
    # Act
    resposta = client.post("/auth/login", json=payload)
    # Assert
    assert resposta.status_code == 401
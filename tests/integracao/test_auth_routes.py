import pytest

@pytest.fixture
def payload_usuario():
    """Usuario base para cadastro de usuario"""
    return {
        "user": "Jkvua",
        "email": "camilalmeida@gmail.com",
        "password": "senhaSeCreta123"
    }

@pytest.fixture
def usuario_cadastro(client, payload_usuario):
    """Cadastra um usuario isolado e retorna suas credenciais"""
    res = client.post('/auth/register', json=payload_usuario)
    
    assert res.status_code in (200, 201), f"Erro no setup da fixture: {res.get_data(as_text=True)}"
    
    return payload_usuario

def test_registro_usuario_sucesso(client, payload_usuario):
    response = client.post('/auth/register', json=payload_usuario)

    assert response.status_code in (200, 201)
    data = response.get_json()
    assert "id" in data or "message" in data

def test_login_usuario_sucesso(client, usuario_cadastro):
    payload_login = {
        "email": usuario_cadastro["email"],
        "password": usuario_cadastro["password"]
    }

    response = client.post('/auth/login', json=payload_login)

    assert response.status_code == 200
    data = response.get_json()
    assert "access_token" in data or "token" in data

def test_login_senha_invalida(client, usuario_cadastro):
    payload_invalido = {
        "email": usuario_cadastro["email"],
        "password": "senhamuitoErrada21"
    }

    response = client.post('/auth/login', json=payload_invalido)

    assert response.status_code in (400, 401)

def test_login_usuario_nao_cadastrado(client):
    payload_inexistente = {
        "email": "walter@sales.com",
        "password": "aindaestouaqui"
    }

    response = client.post('/auth/login', json=payload_inexistente)

    assert response.status_code in (400, 401, 404)
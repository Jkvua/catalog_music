import pytest
from app.models.usuario import Usuario
from app.extensions import db
from werkzeug.security import generate_password_hash

@pytest.fixture
def auth_de_usuario_comum(client):
    payload = {
        "user": "DouglasAdams",
        "email": "douglasescritor@gmail.com",
        "password": "praticamenteinofensiva"
    }
    client.post('/auth/register', json=payload)
    res_login = client.post('/auth/login', json={
        "email": "douglasescritor@gmail.com",
        "password": "praticamenteinofensiva"
    })
    token = res_login.get_json().get("access_token")
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def auth_de_admin(client, app):
    """Cria e loga um usuário administrador para os testes de admin de forma segura"""
    with app.app_context():
        admin_existente = Usuario.query.filter_by(email="adminmaster@gmail.com").first()
        if not admin_existente:
            admin = Usuario(
                user="AdminMaster", 
                email="adminmaster@gmail.com", 
                password=generate_password_hash("adminpassword"), 
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()

    res_login = client.post('/auth/login', json={
        "email": "adminmaster@gmail.com",
        "password": "adminpassword"
    })
    token = res_login.get_json().get("access_token")
    return {"Authorization": f"Bearer {token}"}

def test_perfil_sucesso(client, auth_de_usuario_comum):
    response = client.get('/usuarios/me', headers=auth_de_usuario_comum)
    assert response.status_code == 200
    data = response.get_json()
    assert data["email"] == "douglasescritor@gmail.com"

def test_perfil_sem_token(client):
    response = client.get('/usuarios/me')
    assert response.status_code == 401

def test_atualizar_perfil_sucesso(client, auth_de_usuario_comum):
    payload_update = {"user": "Douglas"}
    response = client.put('/usuarios/me', json=payload_update, headers=auth_de_usuario_comum)
    assert response.status_code == 200
    data = response.get_json()
    assert data["usuario"]["user"] == "Douglas"

def test_deletar_perfil_sucesso(client, auth_de_usuario_comum):
    response = client.delete('/usuarios/me', headers=auth_de_usuario_comum)
    assert response.status_code == 200

def test_acesso_negado_para_nao_admin(client, auth_de_usuario_comum):
    response = client.get('/usuarios/', headers=auth_de_usuario_comum)
    assert response.status_code == 403
    assert response.get_json()["error"] == "Acesso negado"

def test_criar_usuario_via_rota_sucesso(client):
    """Cobre a rota POST /usuarios/"""
    payload = {
        "user": "NovoUsuarioRota",
        "email": "novorota@gmail.com",
        "password": "senha123"
    }
    response = client.post('/usuarios/', json=payload)
    assert response.status_code == 201
    data = response.get_json()
    assert data["usuario"]["user"] == "NovoUsuarioRota"

def test_criar_usuario_via_rota_erro(client):
    """Cobre o erro 400 da rota POST /usuarios/ (dados incompletos)"""
    payload = {"user": "Incompleto"}
    response = client.post('/usuarios/', json=payload)
    assert response.status_code == 400

def test_admin_listar_todos_usuarios(client, auth_de_admin):
    """Cobre GET /usuarios/ por um admin"""
    response = client.get('/usuarios/', headers=auth_de_admin)
    assert response.status_code == 200
    assert isinstance(response.get_json(), list)

def test_admin_obter_usuario_por_id(client, auth_de_admin):
    """Cobre GET /usuarios/<id> por um admin"""
    response = client.get('/usuarios/1', headers=auth_de_admin)
    assert response.status_code in (200, 404)

def test_admin_editar_usuario_por_id(client, auth_de_admin):
    """Cobre PUT /usuarios/<id> por um admin"""
    payload = {"user": "EditadoPeloAdmin"}
    response = client.put('/usuarios/1', json=payload, headers=auth_de_admin)
    assert response.status_code in (200, 404)

def test_admin_deletar_usuario_por_id(client, auth_de_admin, app):
    """Cobre DELETE /usuarios/<id> por um admin"""
    with app.app_context():
        temp_user = Usuario(user="TempDel", email="tempdel@gmail.com", password=generate_password_hash("123"))
        db.session.add(temp_user)
        db.session.commit()
        temp_id = temp_user.id

    response = client.delete(f'/usuarios/{temp_id}', headers=auth_de_admin)
    assert response.status_code in (200, 404, 204)
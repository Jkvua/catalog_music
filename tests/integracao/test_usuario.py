import pytest
from app.models.usuario import Usuario
from app.extensions import db
from werkzeug.security import generate_password_hash
from app.models.artista import Artista
from app.models.album import Album
from app.models.musica import Musica
from app.models.avaliacao import Avaliacao

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

# ------ testando se os dados são realmente removidos -----#

def test_exclusao_usuario_remove_dados_relacionados(client, app):
    """Verifica a exclusão em cascata dos dados associados ao usuário."""

    # 1. Cadastrar usuário pela API
    dados_usuario = {
        "user": "UsuarioCascade",
        "email": "usuario.cascade@teste.com",
        "password": "senha123"
    }

    resposta_registro = client.post("/auth/register",json=dados_usuario)
    assert resposta_registro.status_code == 201

    # 2. Autenticar usuário
    resposta_login = client.post("/auth/login",json={"email": dados_usuario["email"], "password": dados_usuario["password"]})
    assert resposta_login.status_code == 200

    token = resposta_login.get_json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 3. Criar artista
    resposta_artista = client.post("/artistas/",json={"nome": "Artista Cascade", "genero": "Rock", "pais": "Brasil"}, headers=headers)
    assert resposta_artista.status_code == 201
    artista_id = resposta_artista.get_json()["artista"]["id"]

    # 4. Criar álbum
    resposta_album = client.post("/albuns/",json={"titulo": "Album Cascade","ano": 2026,"artista_id": artista_id},headers=headers)
    assert resposta_album.status_code == 201
    album_id = resposta_album.get_json()["album"]["id"]

    # 5. Criar música
    resposta_musica = client.post("/musicas/", json={ "titulo": "Musica Cascade",
            "duracao": "3:30",
            "album_id": album_id,
            "artista_id": artista_id
        },
        headers=headers
    )
    assert resposta_musica.status_code == 201
    musica_id = resposta_musica.get_json()["musica"]["id"]

    # 6. Criar avaliação
    resposta_avaliacao = client.post(
        "/avaliacoes/",
        json={
            "nota": 5,
            "comentario": "Excelente álbum",
            "data_escuta": "2026-11-01",
            "album_id": album_id
        },
        headers=headers
    )
    assert resposta_avaliacao.status_code == 201
    avaliacao_id = resposta_avaliacao.get_json()["avaliacao"]["id"]

    # 7. Confirmar que os registros existem no banco
    with app.app_context():
        usuario = Usuario.query.filter_by(
            email=dados_usuario["email"]
        ).first()

        assert usuario is not None
        usuario_id = usuario.id

        assert db.session.get(Artista, artista_id) is not None
        assert db.session.get(Album, album_id) is not None
        assert db.session.get(Musica, musica_id) is not None
        assert db.session.get(Avaliacao, avaliacao_id) is not None

    # 8. Excluir usuário pela API
    resposta_exclusao = client.delete(
        "/usuarios/me",
        headers=headers
    )
    assert resposta_exclusao.status_code == 200

    # 9. Verificar exclusão dos registros no banco
    with app.app_context():
        db.session.expire_all()

        assert db.session.get(Usuario, usuario_id) is None
        assert db.session.get(Artista, artista_id) is None
        assert db.session.get(Album, album_id) is None
        assert db.session.get(Musica, musica_id) is None
        assert db.session.get(Avaliacao, avaliacao_id) is None

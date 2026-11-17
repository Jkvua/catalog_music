import pytest
from werkzeug.security import generate_password_hash
from app.extensions import db
from app.models.usuario import Usuario
from app.models.artista import Artista
from app.models.album import Album
from app.models.musica import Musica
from app.models.avaliacao import Avaliacao

@pytest.fixture
def auth_de_usuario_comum(client):
    """Autentica um usuário comum."""
    payload = {"user": "DouglasAdams", "email": "douglasescritor@gmail.com", "password": "praticamenteinofensiva"}
    registro = client.post("/auth/register", json=payload)
    assert registro.status_code == 201

    login = client.post("/auth/login", json={"email": payload["email"], "password": payload["password"]})

    assert login.status_code == 200
    token = login.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def auth_de_admin(client, app):
    """Cria e autentica um administrador."""
    with app.app_context():
        admin = Usuario(
            user="AdminMaster",
            email="adminmaster@gmail.com",
            password=generate_password_hash("adminpassword"),
            is_admin=True
        )

        db.session.add(admin)
        db.session.commit()

    login = client.post("/auth/login", json={"email": "adminmaster@gmail.com", "password": "adminpassword"})
    assert login.status_code == 200
    token = login.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def usuario_para_admin(client):
    """Cria um usuário para os testes administrativos."""
    payload = {"user": "UsuarioTesteAdmin", "email": "usuario.admin@teste.com", "password": "senha123"}

    resposta = client.post("/usuarios/", json=payload)
    assert resposta.status_code == 201
    return resposta.get_json()["usuario"]

def test_perfil_sucesso(client, auth_de_usuario_comum):
    """Verifica a consulta do próprio perfil."""
    # Act
    resposta = client.get("/usuarios/me", headers=auth_de_usuario_comum)
    # Assert
    assert resposta.status_code == 200
    assert resposta.get_json()["email"] == "douglasescritor@gmail.com"

def test_perfil_sem_token(client):
    """Impede a consulta do perfil sem autenticação."""
    # Act
    resposta = client.get("/usuarios/me")
    # Assert
    assert resposta.status_code == 401

def test_atualizar_perfil_sucesso(client, auth_de_usuario_comum):
    """Verifica a atualização do próprio perfil."""
    # Arrange
    payload = {"user": "Douglas"}
    # Act
    resposta = client.put("/usuarios/me", json=payload, headers=auth_de_usuario_comum)
    # Assert
    assert resposta.status_code == 200
    assert resposta.get_json()["usuario"]["user"] == payload["user"]
    consulta = client.get("/usuarios/me", headers=auth_de_usuario_comum)

    assert consulta.status_code == 200
    assert consulta.get_json()["user"] == payload["user"]

def test_acesso_negado_para_nao_admin(client, auth_de_usuario_comum):
    """Impede o acesso de usuários comuns à listagem administrativa."""
    # Act
    resposta = client.get("/usuarios/", headers=auth_de_usuario_comum)
    # Assert
    assert resposta.status_code == 403
    assert resposta.get_json()["error"] == "Acesso negado"

def test_criar_usuario_via_rota_sucesso(client):
    """Verifica a criação de usuário pela rota /usuarios/."""
    # Arrange
    payload = {"user": "NovoUsuarioRota", "email": "novorota@gmail.com", "password": "senha123"}
    # Act
    resposta = client.post("/usuarios/", json=payload)
    # Assert
    assert resposta.status_code == 201
    assert resposta.get_json()["usuario"]["user"] == payload["user"]

def test_criar_usuario_via_rota_erro(client):
    """Verifica a rejeição de dados incompletos."""
    # Arrange
    payload = {"user": "Incompleto"}
    # Act
    resposta = client.post("/usuarios/", json=payload)
    # Assert
    assert resposta.status_code == 400

def test_admin_listar_todos_usuarios(client, auth_de_admin):
    """Verifica a listagem de usuários pelo administrador."""
    # Act
    resposta = client.get("/usuarios/", headers=auth_de_admin)
    # Assert
    assert resposta.status_code == 200
    dados = resposta.get_json()

    assert isinstance(dados, list)
    assert any(usuario["email"] == "adminmaster@gmail.com" for usuario in dados)

def test_admin_obter_usuario_por_id(client, auth_de_admin, usuario_para_admin):
    """Verifica a consulta de um usuário pelo administrador."""
    # Arrange
    usuario_id = usuario_para_admin["id"]
    # Act
    resposta = client.get(f"/usuarios/{usuario_id}", headers=auth_de_admin)
    # Assert
    assert resposta.status_code == 200
    assert resposta.get_json()["email"] == usuario_para_admin["email"]

def test_admin_editar_usuario_por_id(client, auth_de_admin, usuario_para_admin):
    """Verifica a edição de um usuário pelo administrador."""
    # Arrange
    usuario_id = usuario_para_admin["id"]
    payload = {"user": "EditadoPeloAdmin"}
    # Act
    resposta = client.put(f"/usuarios/{usuario_id}", json=payload, headers=auth_de_admin)
    # Assert
    assert resposta.status_code == 200
    consulta = client.get(f"/usuarios/{usuario_id}", headers=auth_de_admin)

    assert consulta.status_code == 200
    assert consulta.get_json()["user"] == payload["user"]

def test_admin_deletar_usuario_por_id(client, auth_de_admin, usuario_para_admin):
    """Verifica a exclusão de um usuário pelo administrador."""
    # Arrange
    usuario_id = usuario_para_admin["id"]
    # Act
    resposta = client.delete(f"/usuarios/{usuario_id}", headers=auth_de_admin)
    # Assert
    assert resposta.status_code == 200
    consulta = client.get(f"/usuarios/{usuario_id}", headers=auth_de_admin)
    assert consulta.status_code == 404

def test_exclusao_usuario_remove_dados_relacionados(client, app):
    """Verifica a exclusão em cascata dos registros associados ao usuário."""
    # Arrange: cadastrar e autenticar usuário
    payload_usuario = {"user": "UsuarioCascade", "email": "usuario.cascade@teste.com", "password": "senha123"}
    registro = client.post("/auth/register", json=payload_usuario)

    assert registro.status_code == 201
    login = client.post("/auth/login", json={"email": payload_usuario["email"], "password": payload_usuario["password"]})

    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.get_json()['access_token']}"}
    # Arrange: criar artista
    resposta_artista = client.post("/artistas/",
        json={
            "nome": "Artista Cascade",
            "genero": "Rock",
            "pais": "Brasil"
        },headers=headers)

    assert resposta_artista.status_code == 201
    artista_id = resposta_artista.get_json()["artista"]["id"]
    # Arrange: criar álbum
    resposta_album = client.post("/albuns/",
        json={
            "titulo": "Album Cascade",
            "ano": 2026,
            "artista_id": artista_id
        }, headers=headers)

    assert resposta_album.status_code == 201
    album_id = resposta_album.get_json()["album"]["id"]

    # Arrange: criar música
    resposta_musica = client.post("/musicas/",
        json={
            "titulo": "Musica Cascade",
            "duracao": "03:30",
            "album_id": album_id
        }, headers=headers)

    assert resposta_musica.status_code == 201
    musica_id = resposta_musica.get_json()["musica"]["id"]

    # Arrange: criar avaliação
    resposta_avaliacao = client.post("/avaliacoes/",
        json={
            "nota": 5,
            "comentario": "Excelente álbum",
            "data_escuta": "2026-11-01",
            "album_id": album_id
        }, headers=headers)

    assert resposta_avaliacao.status_code == 201
    avaliacao_id = resposta_avaliacao.get_json()["avaliacao"]["id"]
    # Arrange: recuperar ID do usuário
    with app.app_context():
        usuario = Usuario.query.filter_by(email=payload_usuario["email"]).first()

        assert usuario is not None
        usuario_id = usuario.id
    # Act: excluir usuário
    resposta = client.delete("/usuarios/me", headers=headers)
    # Assert: verificar resposta
    assert resposta.status_code == 200
    # Assert: verificar exclusão em cascata no banco
    with app.app_context():
        db.session.expire_all()

        assert db.session.get(Usuario, usuario_id) is None
        assert db.session.get(Artista, artista_id) is None
        assert db.session.get(Album, album_id) is None
        assert db.session.get(Musica, musica_id) is None
        assert db.session.get(Avaliacao, avaliacao_id) is None
import pytest
from app.services.usuario import UsuarioService
from app.models.usuario import Usuario
from app.extensions import db
from werkzeug.security import check_password_hash

@pytest.fixture
def usuario_comum(app):
    """"Criando usuario comum"""
    with app.app_context():
        user = Usuario(user="mara", email="mara@gmail.com", password="123456", is_admin=False)
        db.session.add(user)
        db.session.commit()
        yield user

@pytest.fixture
def usuario_admin(app):
    """Criando usuario admin"""
    with app.app_context():
        admin = Usuario(user="adminuser", email="admin@gmail.com", password="adminsenhat5y", is_admin=True)
        db.session.add(admin)
        db.session.commit()
        yield admin

def test_validar_email():
    """Garante que emails validos passem e emails invalidos falhem"""
    assert UsuarioService.validar_email("camila@gmail.com") is not None
    assert UsuarioService.validar_email("camila.ferreira.almeida") is None
    assert UsuarioService.validar_email("camila@") is None

def test_correto_admin(app, usuario_admin):
    """Garante que a função identifique o admin corretamente"""
    with app.app_context():
        assert UsuarioService.is_admin(usuario_admin.id) is True

def test_falto_admin(app, usuario_comum):
    """Garante que o usuáio comum não seja identificado como admin"""
    with app.app_context():
        assert UsuarioService.is_admin(usuario_comum.id) is False

def test_admin_inexistente(app):
    """Garante que buscar um id que não existe não quebre o sistema"""
    with app.app_context():
        assert UsuarioService.is_admin(999) is False

def test_criar_usuario_sucesso(app):
    """Garante a criação correta de um usuário"""
    with app.app_context():
        dados = {"user": "juca", "email": "juca@gmail.com", "password": "b23a56"}
        resultado, status = UsuarioService.criar_usuario(dados)

        assert status == 201
        assert resultado.user == "juca"
        assert check_password_hash(resultado.password, "b23a56")

def test_criar_usuario_campo_incompleto(app):
    """Garante que campos obrigatórios não preenchidos retornem error"""
    with app.app_context():
        dados = {"user": "juca"}
        resultado, status = UsuarioService.criar_usuario(dados)

        assert status == 400
        assert "obrigatórios" in resultado["error"]

def test_criar_usuario_email_duplicado(app, usuario_comum):
    """Garante que emails duplicados não sejam aceitos"""
    with app.app_context():
        dados = {"user": "marisa", "email": "mara@gmail.com", "password": "marisacarla"}
        resultado, status = UsuarioService.criar_usuario(dados)

        assert status == 400
        assert "já está em uso" in resultado["error"]

def test_criar_nome_duplicado(app, usuario_comum):
    """Garante que nomes duplicados não sejam aceitos"""
    with app.app_context():
        dados = {"user": "mara", "email": "maracosta@gmail.com", "password": "maracostasilva"}
        resultado, status = UsuarioService.criar_usuario(dados)

        assert status == 400
        assert "já está em uso" in resultado["error"]

def test_editar_usuario_sucesso(app, usuario_comum):
    """Testa a edição parcial de um usuário"""
    with app.app_context():
        dados = {"user": "mari", "email": "marisa@gmail.com"}
        resultado, status = UsuarioService.editar_usuario(usuario_comum.id, dados)

        assert status == 200
        assert resultado.user == "mari"
        assert resultado.email == "marisa@gmail.com"

def test_editar_usuario_email_duplicado(app, usuario_comum, usuario_admin):
    """Garante que não seja possível cadastrar um email já existente ao editar"""
    with app.app_context():
        dados = {"email": "mara@gmail.com"}
        resultado, status = UsuarioService.editar_usuario(usuario_admin.id, dados)

        assert status == 400
        assert "já está em uso por outro usuário" in resultado["error"]


def test_deletar_usuario_sucesso(app, usuario_comum):
    """Testa a exclusão de um usuário"""
    with app.app_context():
        resultado, status = UsuarioService.delete_usuario(usuario_comum.id)

        assert status == 200
        assert "excluídos com sucesso" in resultado["message"]
        assert Usuario.query.get(usuario_comum.id) is None
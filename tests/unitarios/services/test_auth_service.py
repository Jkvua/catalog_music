import pytest
from app.services.auth_service import AuthService
from app.models.usuario import Usuario
from app.extensions import db
from werkzeug.security import generate_password_hash

@pytest.fixture
def usuario_cadastrado(app):
    """Criar um usuário base com senha criptografada para os testes"""
    with app.app_context():
        usuario = Usuario(
            user="Camila",
            email="camilatcf@gmail.com",
            password=generate_password_hash("grande_senha_g1230!")
        )
        db.session.add(usuario)
        db.session.commit()
        yield usuario

def test_registrar_sucesso(app):
    """"Testa se o registro cria o usuário e retorna 201"""
    with app.app_context():
        resultado, status = AuthService.register("Pedro", "pedro@exemplo.com", "senhasecreta")

        assert status == 201
        assert resultado["status"] == "success"

        usuario_db = Usuario.query.filter_by(email="pedro@exemplo.com").first()
        assert usuario_db is not None
        assert usuario_db.user == "Pedro"

def test_registrar_email_duplicado(app, usuario_cadastrado):
    """Testa se um email já existente é barrado"""
    with app.app_context():
        resultado, status = AuthService.register("Joana Camila", "camilatcf@gmail.com", "123outrasenha")

        assert status == 400
        assert "já registrado" in resultado["message"]

def test_login_sucesso(app, usuario_cadastrado):
    """Testa se o login correto gera o token"""
    with app.app_context():
        resultado, status = AuthService.login("camilatcf@gmail.com", "grande_senha_g1230!")

        assert status == 200
        assert "access_token" in resultado
        assert resultado["user"]["email"] == "camilatcf@gmail.com"

def test_login_senha_incorreta(app, usuario_cadastrado):
    """Testa se o login com senha incorreta retorna erro"""
    with app.app_context():
        resultado, status = AuthService.login("camilatcf@gmail.com", "senhaincorreta")

        assert status == 401
        assert "Credenciais inválidas" in resultado["error"]

def test_email_nao_cadastrado(app):
    """Testa se o login com email não cadastrado retorna erro"""
    with app.app_context():
        resultado, status = AuthService.login("giganteitalia@gmail.com", "palmeiramaiordobrasil")

        assert status == 401
        assert "Credenciais inválidas" in resultado["error"]
import pytest
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from app.models.usuario import Usuario
from app.services.auth_service import AuthService

@pytest.fixture
def usuario_cadastrado(app):
    """Cria um usuário com senha criptografada."""
    with app.app_context():
        usuario = Usuario(user="Camila", email="camila@exemplo.com", password=generate_password_hash("grande_senha_g1230!"))

        db.session.add(usuario)
        db.session.commit()
        return usuario.email

def test_registrar_sucesso(app):
    """Verifica o cadastro e a persistência de um usuário."""
    with app.app_context():
        # Arrange
        nome = "Pedro"
        email = "pedro@exemplo.com"
        senha = "senhasecreta"

        # Act
        resultado, status = AuthService.register(nome, email, senha)
        # Assert
        assert status == 201
        assert resultado["status"] == "success"

        usuario = Usuario.query.filter_by(email=email).first()

        assert usuario is not None
        assert usuario.user == nome
        assert usuario.password != senha
        assert check_password_hash(usuario.password, senha)

def test_registrar_email_duplicado(app, usuario_cadastrado):
    """Impede o cadastro de um e-mail já existente."""
    with app.app_context():
        # Arrange
        nome = "Joana Camila"
        email = usuario_cadastrado
        senha = "123outrasenha"

        # Act
        resultado, status = AuthService.register(nome, email, senha)
        # Assert
        assert status == 400
        assert "já registrado" in resultado["message"]

        quantidade = Usuario.query.filter_by(email=email).count()
        assert quantidade == 1

def test_login_sucesso(app, usuario_cadastrado):
    """Verifica a autenticação e a geração do token JWT."""
    with app.app_context():
        # Arrange
        email = usuario_cadastrado
        senha = "grande_senha_g1230!"

        # Act
        resultado, status = AuthService.login(email, senha)
        # Assert
        assert status == 200
        assert "access_token" in resultado
        assert isinstance(resultado["access_token"], str)
        assert resultado["access_token"]
        assert resultado["user"]["email"] == email

def test_login_senha_incorreta(app, usuario_cadastrado):
    """Impede a autenticação com senha incorreta."""
    with app.app_context():
        # Arrange
        email = usuario_cadastrado
        senha = "senhaincorreta"

        # Act
        resultado, status = AuthService.login(email, senha)
        # Assert
        assert status == 401
        assert "Credenciais inválidas" in resultado["error"]

def test_login_email_nao_cadastrado(app):
    """Impede a autenticação de um usuário inexistente."""
    with app.app_context():
        # Arrange
        email = "usuario.inexistente@exemplo.com"
        senha = "senha123"

        # Act
        resultado, status = AuthService.login(email, senha)
        # Assert
        assert status == 401
        assert "Credenciais inválidas" in resultado["error"]
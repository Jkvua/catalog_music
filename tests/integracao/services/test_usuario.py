import pytest
from werkzeug.security import check_password_hash
from app.extensions import db
from app.models.usuario import Usuario
from app.services.usuario import UsuarioService

@pytest.fixture
def usuario_comum(app):
    with app.app_context():
        usuario = Usuario(
            user="mara",
            email="mara@gmail.com",
            password="123456",
            is_admin=False
        )

        db.session.add(usuario)
        db.session.commit()
        return usuario.id

@pytest.fixture
def usuario_admin(app):
    with app.app_context():
        usuario = Usuario(
            user="adminuser",
            email="admin@gmail.com",
            password="123456",
            is_admin=True
        )

        db.session.add(usuario)
        db.session.commit()
        return usuario.id

@pytest.mark.parametrize(
    "tipo_usuario, esperado",
    [
        ("admin", True),
        ("comum", False),
    ]
)

def test_identificar_admin(app, usuario_admin, usuario_comum, tipo_usuario, esperado):
    """Verifica a identificação de administradores e usuários comuns."""
    with app.app_context():
        # Arrange
        usuario_id = (usuario_admin if tipo_usuario == "admin"else usuario_comum)
        # Act
        resultado = UsuarioService.is_admin(usuario_id)
        # Assert
        assert resultado is esperado

def test_criar_usuario_sucesso(app):
    """Verifica a criação de usuário com senha protegida."""
    with app.app_context():
        # Arrange
        dados = {"user": "juca", "email": "juca@gmail.com", "password": "b23a56"}
        # Act
        resultado, status = UsuarioService.criar_usuario(dados)
        # Assert
        assert status == 201
        assert resultado.user == dados["user"]
        assert resultado.email == dados["email"]

        usuario = db.session.get(Usuario, resultado.id)

        assert usuario is not None
        assert usuario.password != dados["password"]
        assert check_password_hash(usuario.password, dados["password"])

def test_criar_usuario_email_duplicado(app, usuario_comum):
    """Impede o cadastro de um e-mail já utilizado."""
    with app.app_context():
        # Arrange
        dados = {"user": "marisa", "email": "mara@gmail.com", "password": "marisacarla"}
        # Act
        resultado, status = UsuarioService.criar_usuario(dados)
        # Assert
        assert status == 400
        assert "já está em uso" in resultado["error"]

        quantidade = Usuario.query.filter_by(email=dados["email"]).count()
        assert quantidade == 1

def test_criar_usuario_nome_duplicado(app, usuario_comum):
    """Impede o cadastro de nomes de usuário duplicados."""
    with app.app_context():
        # Arrange
        dados = {"user": "mara", "email": "maracosta@gmail.com", "password": "maracostasilva"}
        # Act
        resultado, status = UsuarioService.criar_usuario(dados)
        # Assert
        assert status == 400
        assert "já está em uso" in resultado["error"]

        quantidade = Usuario.query.filter_by(user=dados["user"]).count()
        assert quantidade == 1

def test_obter_usuario_proprio(app, usuario_comum):
    """Permite que o usuário consulte seus próprios dados."""
    with app.app_context():
        # Act
        resultado, status = UsuarioService.obter_usuario(usuario_comum, solicitante_id=usuario_comum)
        # Assert
        assert status == 200
        assert resultado.id == usuario_comum
        assert resultado.email == "mara@gmail.com"

def test_obter_usuario_sem_permissao(app, usuario_comum, usuario_admin):
    """Impede que um usuário comum consulte outra conta."""
    with app.app_context():
        # Act
        resultado, status = UsuarioService.obter_usuario( usuario_admin, solicitante_id=usuario_comum)
        # Assert
        assert status == 403
        assert resultado["error"] == "Acesso negado"

def test_obter_todos_usuarios_por_admin(app, usuario_admin, usuario_comum):
    """Permite que um administrador liste os usuários."""
    with app.app_context():
        # Act
        resultado, status = UsuarioService.obter_todos_usuarios(solicitante_id=usuario_admin)
        # Assert
        assert status == 200
        assert len(resultado) == 2

        ids = {usuario.id for usuario in resultado}
        assert ids == {usuario_admin, usuario_comum}

def test_obter_todos_usuarios_negado_para_comum(app, usuario_comum):
    """Impede que usuários comuns listem todas as contas."""
    with app.app_context():
        # Act
        resultado, status = UsuarioService.obter_todos_usuarios(solicitante_id=usuario_comum)
        # Assert
        assert status == 403
        assert resultado["error"] == "Acesso negado"

def test_editar_usuario_sucesso(app, usuario_comum):
    """Verifica a atualização do nome e do e-mail."""
    with app.app_context():
        # Arrange
        dados = {"user": "mari", "email": "marisa@gmail.com"}
        # Act
        resultado, status = UsuarioService.editar_usuario(usuario_comum, dados, solicitante_id=usuario_comum)
        # Assert
        assert status == 200
        assert resultado.user == dados["user"]
        assert resultado.email == dados["email"]

        db.session.expire_all()
        usuario = db.session.get(Usuario, usuario_comum)

        assert usuario is not None
        assert usuario.user == dados["user"]
        assert usuario.email == dados["email"]

def test_editar_usuario_senha(app, usuario_comum):
    """Verifica a atualização da senha com hash."""
    with app.app_context():
        # Arrange
        dados = {"password": "novasenha123"}
        # Act
        resultado, status = UsuarioService.editar_usuario(usuario_comum, dados, solicitante_id=usuario_comum)
        # Assert
        assert status == 200
        db.session.expire_all()
        usuario = db.session.get(Usuario, usuario_comum)

        assert usuario is not None
        assert usuario.password != dados["password"]
        assert check_password_hash(usuario.password, dados["password"])

def test_editar_usuario_sem_permissao(app, usuario_comum, usuario_admin):
    """Impede a edição de outra conta sem autorização."""
    with app.app_context():
        # Arrange
        dados = {"user": "nome_alterado"}
        # Act
        resultado, status = UsuarioService.editar_usuario(usuario_admin, dados, solicitante_id=usuario_comum)
        # Assert
        assert status == 403
        assert resultado["error"] == "Acesso negado"

        db.session.expire_all()
        usuario = db.session.get(Usuario, usuario_admin)

        assert usuario is not None
        assert usuario.user == "adminuser"

def test_deletar_usuario_sucesso(app, usuario_comum):
    """Verifica a exclusão da própria conta."""
    with app.app_context():
        # Act
        resultado, status = UsuarioService.deletar_usuario(usuario_comum, solicitante_id=usuario_comum)
        # Assert
        assert status == 200
        assert "excluídos com sucesso" in resultado["message"]

        db.session.expire_all()
        assert db.session.get(Usuario, usuario_comum) is None

def test_editar_usuario_email_duplicado(app, usuario_comum, usuario_admin):
    """Impede a alteração para um e-mail utilizado por outro usuário."""
    with app.app_context():
        # Arrange
        dados = {"email": "mara@gmail.com"}
        # Act
        resultado, status = UsuarioService.editar_usuario(usuario_admin, dados, solicitante_id=usuario_admin)

        # Assert
        assert status == 400
        assert "já está em uso por outro usuário" in resultado["error"]

        db.session.expire_all()
        usuario = db.session.get(Usuario, usuario_admin)

        assert usuario is not None
        assert usuario.email == "admin@gmail.com"

def test_deletar_usuario_sem_permissao(app, usuario_comum, usuario_admin):
    """Impede a exclusão de outra conta sem autorização."""
    with app.app_context():
        # Act
        resultado, status = UsuarioService.deletar_usuario(usuario_admin, solicitante_id=usuario_comum)
        # Assert
        assert status == 403
        assert resultado["error"] == "Acesso negado"
        assert db.session.get(Usuario, usuario_admin) is not None
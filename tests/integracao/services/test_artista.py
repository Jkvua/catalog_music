import pytest
from app.extensions import db
from app.models.usuario import Usuario
from app.models.artista import Artista
from app.services.artista import ArtistaService

@pytest.fixture
def usuario_padrao(app):
    """Cria um usuário para os testes."""
    with app.app_context():
        usuario = Usuario(user="Camila", email="camila@example.com", password="123456")

        db.session.add(usuario)
        db.session.commit()
        return usuario.id

@pytest.fixture
def usuario_secundario(app):
    """Cria um segundo usuário para testar autorização e isolamento."""
    with app.app_context():
        usuario = Usuario(user="Carol", email="carol@example.com", password="123456")
        db.session.add(usuario)
        db.session.commit()

        return usuario.id

@pytest.fixture
def artista_padrao(app, usuario_padrao):
    """Cria um artista associado ao usuário padrão."""
    with app.app_context():
        artista = Artista(
            nome="TWICE",
            genero="K-POP",
            pais="Coreia do Sul",
            usuario_id=usuario_padrao)

        db.session.add(artista)
        db.session.commit()
        return artista.id

def test_criar_artista_sucesso(app, usuario_padrao):
    """Verifica a criação e persistência de um artista."""
    with app.app_context():
        # Arrange
        dados = { "nome": "TWICE", "genero": "K-POP", "pais": "Coreia do Sul"}
        # Act
        resultado, status = ArtistaService.criar_artista( dados, usuario_id=usuario_padrao)
        # Assert
        assert status == 201
        assert resultado.nome == dados["nome"]
        assert resultado.usuario_id == usuario_padrao

        artista = db.session.get(Artista, resultado.id)

        assert artista is not None
        assert artista.genero == dados["genero"]

def test_criar_artista_duplicado(app, usuario_padrao, artista_padrao):
    """Impede a criação de artistas duplicados no mesmo catálogo."""
    with app.app_context():
        # Arrange
        dados = {"nome": "TWICE","genero": "K-POP", "pais": "Coreia do Sul"}
        # Act
        resultado, status = ArtistaService.criar_artista(dados, usuario_id=usuario_padrao)
        # Assert
        assert status == 400
        assert "já existe no catálogo" in resultado["error"]

        quantidade = Artista.query.filter_by(nome=dados["nome"], usuario_id=usuario_padrao).count()
        assert quantidade == 1

def test_usuarios_diferentes_podem_criar_artistas_com_mesmo_nome(app, usuario_padrao, usuario_secundario):
    """Permite nomes iguais em catálogos de usuários diferentes."""
    with app.app_context():
        # Arrange
        dados = {"nome": "NewJeans", "genero": "K-POP", "pais": "Coreia do Sul"}
        # Act
        artista1, status1 = ArtistaService.criar_artista( dados,  usuario_id=usuario_padrao)
        artista2, status2 = ArtistaService.criar_artista(dados, usuario_id=usuario_secundario)
        # Assert
        assert status1 == 201
        assert status2 == 201

        assert artista1.id != artista2.id
        assert artista1.nome == artista2.nome

        assert artista1.usuario_id == usuario_padrao
        assert artista2.usuario_id == usuario_secundario

def test_editar_artista_sucesso(app, usuario_padrao, artista_padrao):
    """Verifica a atualização dos dados de um artista."""
    with app.app_context():
        # Arrange
        novos_dados = {"nome": "TWICE Official", "genero": "Pop", "pais": "Japão"}
        # Act
        resultado, status = ArtistaService.editar_artista(artista_padrao, novos_dados, usuario_id=usuario_padrao)

        # Assert
        assert status == 200
        assert resultado.nome == novos_dados["nome"]
        assert resultado.genero == novos_dados["genero"]
        assert resultado.pais == novos_dados["pais"]

        db.session.expire_all()
        artista = db.session.get(Artista, artista_padrao)

        assert artista is not None
        assert artista.nome == novos_dados["nome"]
        assert artista.genero == novos_dados["genero"]
        assert artista.pais == novos_dados["pais"]

def test_editar_artista_sem_permissao(app, artista_padrao, usuario_secundario):
    """Impede que outro usuário edite o artista."""
    with app.app_context():
        # Arrange
        dados = {"nome": "Artista Alterado"}
        # Act
        resultado, status = ArtistaService.editar_artista(artista_padrao, dados, usuario_id=usuario_secundario)
        # Assert
        assert status == 403
        assert "não tem permissão" in resultado["error"]

        artista = db.session.get(Artista, artista_padrao)

        assert artista is not None
        assert artista.nome == "TWICE"

def test_editar_artista_nome_duplicado(app, usuario_padrao, artista_padrao):
    """Impede renomear um artista para um nome já usado no catálogo."""
    with app.app_context():
        # Arrange
        segundo_artista = Artista(
            nome="IVE",
            genero="K-POP",
            pais="Coreia do Sul",
            usuario_id=usuario_padrao)

        db.session.add(segundo_artista)
        db.session.commit()
        segundo_artista_id = segundo_artista.id

        # Act
        resultado, status = ArtistaService.editar_artista(segundo_artista_id, {"nome": "TWICE"}, usuario_id=usuario_padrao)
        # Assert
        assert status == 400
        assert "já existe no catálogo" in resultado["error"]

        artista = db.session.get(Artista, segundo_artista_id)
        assert artista.nome == "IVE"

def test_editar_artista_nome_existente_em_outro_usuario(app, usuario_padrao, usuario_secundario, artista_padrao):
    """Permite usar um nome existente no catálogo de outro usuário."""
    with app.app_context():
        # Arrange
        artista_secundario = Artista(
            nome="NewJeans",
            genero="K-POP",
            pais="Coreia do Sul",
            usuario_id=usuario_secundario)

        db.session.add(artista_secundario)
        db.session.commit()
        artista_secundario_id = artista_secundario.id
        # Act
        resultado, status = ArtistaService.editar_artista( artista_secundario_id, {"nome": "TWICE"}, usuario_id=usuario_secundario)
        # Assert
        assert status == 200
        assert resultado.nome == "TWICE"
        assert resultado.usuario_id == usuario_secundario

        db.session.expire_all()
        artista = db.session.get(Artista, artista_secundario_id)

        assert artista is not None
        assert artista.nome == "TWICE"
        assert artista.usuario_id == usuario_secundario

        artista_original = db.session.get(Artista, artista_padrao)

        assert artista_original.nome == "TWICE"
        assert artista_original.usuario_id == usuario_padrao

def test_deletar_artista_sem_permissao(app, artista_padrao, usuario_secundario):
    """Impede que outro usuário exclua o artista."""
    with app.app_context():
        # Arrange
        artista_id = artista_padrao
        # Act
        resultado, status = ArtistaService.deletar_artista(artista_id, usuario_id=usuario_secundario)
        # Assert
        assert status == 403
        assert "não tem permissão" in resultado["error"]

        artista = db.session.get(Artista, artista_id)
        assert artista is not None
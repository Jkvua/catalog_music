import pytest
from app.extensions import db
from app.models.usuario import Usuario
from app.models.artista import Artista
from app.models.album import Album
from app.services.album import AlbumService

@pytest.fixture
def usuario_padrao(app):
    """Cria um usuário para os testes."""
    with app.app_context():
        usuario = Usuario( user="Camila", email="camila@example.com", password="123456")
        db.session.add(usuario)
        db.session.commit()
        return usuario.id

@pytest.fixture
def artista_padrao(app, usuario_padrao):
    """Cria um artista pertencente ao usuário padrão."""
    with app.app_context():
        artista = Artista( nome="TWICE", genero="K-POP", pais="Coreia do Sul", usuario_id=usuario_padrao)

        db.session.add(artista)
        db.session.commit()
        return artista.id

@pytest.fixture
def album_padrao(app, usuario_padrao, artista_padrao):
    """Cria um álbum associado ao artista e ao usuário."""
    with app.app_context():
        album = Album( titulo="Fancy You", ano=2019, artista_id=artista_padrao, usuario_id=usuario_padrao)

        db.session.add(album)
        db.session.commit()
        return album.id

@pytest.fixture
def usuario_invasor(app):
    """Cria um segundo usuário para os testes de autorização."""
    with app.app_context():
        usuario = Usuario( user="UsuarioInvasor", email="invasor@example.com", password="123456")

        db.session.add(usuario)
        db.session.commit()
        return usuario.id

def test_criar_album_com_artista_id(app, usuario_padrao, artista_padrao):
    """Verifica a criação de álbum utilizando o ID do artista."""
    with app.app_context():
        # Arrange
        dados = {"titulo": "Formula of Love", "ano": 2021, "artista_id": artista_padrao}
        # Act
        resultado, status = AlbumService.criar_album(dados, usuario_id=usuario_padrao)
        # Assert
        assert status == 201
        assert resultado.titulo == dados["titulo"]
        assert resultado.artista_id == artista_padrao

        album = db.session.get(Album, resultado.id)

        assert album is not None
        assert album.usuario_id == usuario_padrao

def test_criar_album_com_nome_artista(app, usuario_padrao, artista_padrao):
    """Verifica a criação de álbum buscando o artista pelo nome."""
    with app.app_context():
        # Arrange
        dados = { "titulo": "Feel Special", "ano": 2019, "artista": "TWICE"}
        # Act
        resultado, status = AlbumService.criar_album(dados, usuario_id=usuario_padrao)

        # Assert
        assert status == 201
        assert resultado.artista_id == artista_padrao

        album = db.session.get(Album, resultado.id)

        assert album is not None
        assert album.titulo == dados["titulo"]

def test_criar_album_artista_inexistente(app, usuario_padrao):
    """Impede a criação de álbum com artista inexistente."""
    with app.app_context():
        # Arrange
        dados = {"titulo": "Album Teste", "ano": 2023, "artista_id": 9999}
        # Act
        resultado, status = AlbumService.criar_album(dados, usuario_id=usuario_padrao)
        # Assert
        assert status == 404
        assert "não encontrado" in resultado["error"]

def test_criar_album_duplicado(app, usuario_padrao, album_padrao):
    """Impede a criação de álbum duplicado para o mesmo artista."""
    with app.app_context():
        # Arrange
        album_existente = db.session.get(Album, album_padrao)
        dados = {"titulo": album_existente.titulo, "ano": 2023, "artista_id": album_existente.artista_id}
        # Act
        resultado, status = AlbumService.criar_album(dados, usuario_id=usuario_padrao)
        # Assert
        assert status == 400
        assert "já existe para esse artista" in resultado["error"]

        quantidade = Album.query.filter_by(
            titulo=dados["titulo"], artista_id=dados["artista_id"], usuario_id=usuario_padrao).count()
        assert quantidade == 1

def test_editar_album_sucesso(app, usuario_padrao, album_padrao):
    """Verifica a atualização de título e ano do álbum."""
    with app.app_context():
        # Arrange
        dados_novos = {"titulo": "Fancy You Deluxe", "ano": 2020}
        # Act
        resultado, status = AlbumService.editar_album(album_padrao, dados_novos, usuario_id=usuario_padrao)
        # Assert
        assert status == 200
        assert resultado.titulo == dados_novos["titulo"]
        assert resultado.ano == dados_novos["ano"]

        db.session.expire_all()
        album = db.session.get(Album, album_padrao)

        assert album is not None
        assert album.titulo == dados_novos["titulo"]
        assert album.ano == dados_novos["ano"]

def test_editar_album_bloqueia_editar_artista(app, usuario_padrao, album_padrao):
    """Impede a alteração do artista associado ao álbum."""
    with app.app_context():
        # Arrange
        dados_novos = {"artista_id": 999}
        # Act
        resultado, status = AlbumService.editar_album( album_padrao, dados_novos, usuario_id=usuario_padrao)
        # Assert
        assert status == 400
        assert "Não é permitido alterar o artista" in resultado["error"]

def test_editar_album_sem_permissao(app, album_padrao, usuario_invasor):
    """Impede que outro usuário edite o álbum."""
    with app.app_context():
        # Arrange
        dados_novos = { "titulo": "Alterado pelo invasor"}
        # Act
        resultado, status = AlbumService.editar_album(album_padrao, dados_novos, usuario_id=usuario_invasor)
        # Assert
        assert status == 403
        assert "não tem permissão" in resultado["error"]

        album = db.session.get(Album, album_padrao)
        assert album.titulo == "Fancy You"

def test_deletar_album_sucesso(app, usuario_padrao, album_padrao):
    """Verifica a exclusão do álbum pelo proprietário."""
    with app.app_context():
        # Arrange
        album_id = album_padrao
        # Act
        resultado, status = AlbumService.deletar_album(album_id, usuario_id=usuario_padrao)
        # Assert
        assert status == 200
        assert "deletado com sucesso" in resultado["message"]

        db.session.expire_all()
        album = db.session.get(Album, album_id)
        assert album is None

def test_deletar_album_sem_permissao(app, album_padrao, usuario_invasor):
    """Impede que outro usuário exclua o álbum."""
    with app.app_context():
        # Arrange
        album_id = album_padrao
        # Act
        resultado, status = AlbumService.deletar_album(album_id, usuario_id=usuario_invasor)
        # Assert
        assert status == 403
        assert "não tem permissão" in resultado["error"]

        album = db.session.get(Album, album_id)
        assert album is not None
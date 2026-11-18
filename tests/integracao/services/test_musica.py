import pytest
from app.extensions import db
from app.models.usuario import Usuario
from app.models.artista import Artista
from app.models.album import Album
from app.models.musica import Musica
from app.services.musica import MusicaService

@pytest.fixture
def usuario_padrao(app):
    with app.app_context():
        usuario = Usuario(
            user="Camila", email="camila@exemplo.com", password="123456")

        db.session.add(usuario)
        db.session.commit()
        return usuario.id

@pytest.fixture
def usuario_secundario(app):
    with app.app_context():
        usuario = Usuario(
            user="OutroUsuario", email="outro@exemplo.com", password="123456")

        db.session.add(usuario)
        db.session.commit()
        return usuario.id

@pytest.fixture
def artista_padrao(app, usuario_padrao):
    with app.app_context():
        artista = Artista(
            nome="TWICE",
            genero="K-POP",
            pais="Coreia do Sul",
            usuario_id=usuario_padrao
        )

        db.session.add(artista)
        db.session.commit()
        return artista.id

@pytest.fixture
def album_padrao(app, usuario_padrao, artista_padrao):
    with app.app_context():
        album = Album(
            titulo="Feel Special",
            ano=2019,
            artista_id=artista_padrao,
            usuario_id=usuario_padrao
        )

        db.session.add(album)
        db.session.commit()
        return album.id

@pytest.fixture
def musica_padrao(app, usuario_padrao, album_padrao):
    with app.app_context():
        musica = Musica(
            titulo="Feel Special",
            duracao="03:27",
            album_id=album_padrao,
            usuario_id=usuario_padrao
        )

        db.session.add(musica)
        db.session.commit()
        return musica.id

def test_criar_musica_com_album_id(app, usuario_padrao, album_padrao):
    """Verifica a criação de uma música utilizando o ID do álbum."""
    with app.app_context():
        # Arrange
        dados = {"titulo": "Rainbow", "duracao": "03:30", "album_id": album_padrao}
        # Act
        resultado, status = MusicaService.criar_musica(dados, usuario_id=usuario_padrao)
        # Assert
        assert status == 201
        assert resultado.titulo == dados["titulo"]
        assert resultado.album_id == album_padrao
        assert resultado.usuario_id == usuario_padrao

        musica = db.session.get(Musica, resultado.id)

        assert musica is not None
        assert musica.duracao == dados["duracao"]

def test_criar_musica_com_nome_album(app, usuario_padrao, album_padrao):
    """Verifica a criação de uma música buscando o álbum pelo nome."""
    with app.app_context():
        # Arrange
        dados = {"titulo": "GET LOUD", "duracao": "03:07", "album": "Feel Special"}
        # Act
        resultado, status = MusicaService.criar_musica(dados, usuario_id=usuario_padrao)
        # Assert
        assert status == 201
        assert resultado.titulo == dados["titulo"]
        assert resultado.album_id == album_padrao

def test_criar_musica_album_id_inexistente(app, usuario_padrao):
    """Impede a criação de uma música em um álbum inexistente."""
    with app.app_context():
        # Arrange
        dados = {"titulo": "Love Foolish", "duracao": "03:12", "album_id": 9999}
        # Act
        resultado, status = MusicaService.criar_musica(dados, usuario_id=usuario_padrao)
        # Assert
        assert status == 404
        assert "não encontrado" in resultado["error"]

def test_criar_musica_duplicada(app, usuario_padrao, album_padrao, musica_padrao):
    """Impede músicas com o mesmo título no mesmo álbum."""
    with app.app_context():
        # Arrange
        dados = {"titulo": "Feel Special", "duracao": "03:27", "album_id": album_padrao}
        # Act
        resultado, status = MusicaService.criar_musica(dados, usuario_id=usuario_padrao)
        # Assert
        assert status == 400
        assert "já existe neste álbum" in resultado["error"]

        quantidade = Musica.query.filter_by( titulo=dados["titulo"], album_id=album_padrao, usuario_id=usuario_padrao).count()
        assert quantidade == 1

def test_editar_musica_sucesso(app, usuario_padrao, musica_padrao):
    """Verifica a atualização do título e da duração."""
    with app.app_context():
        # Arrange
        dados = { "titulo": "Feel Special (Remix)", "duracao": "04:15"}
        # Act
        resultado, status = MusicaService.editar_musica(musica_padrao, dados, usuario_id=usuario_padrao)
        # Assert
        assert status == 200
        assert resultado.titulo == dados["titulo"]
        assert resultado.duracao == dados["duracao"]

        db.session.expire_all()
        musica = db.session.get(Musica, musica_padrao)

        assert musica is not None
        assert musica.titulo == dados["titulo"]
        assert musica.duracao == dados["duracao"]

def test_editar_musica_titulo_duplicado(app, usuario_padrao, album_padrao, musica_padrao):
    """Impede renomear uma música para um título já existente no álbum."""
    with app.app_context():
        # Arrange
        segunda_musica = Musica(
            titulo="GET LOUD",
            duracao="03:07",
            album_id=album_padrao,
            usuario_id=usuario_padrao
        )

        db.session.add(segunda_musica)
        db.session.commit()
        segunda_musica_id = segunda_musica.id

        # Act
        resultado, status = MusicaService.editar_musica(segunda_musica_id, {"titulo": "Feel Special"}, usuario_id=usuario_padrao)
        # Assert
        assert status == 400
        assert "já existe neste álbum" in resultado["error"]
        musica = db.session.get(Musica, segunda_musica_id)

        assert musica is not None
        assert musica.titulo == "GET LOUD"

def test_editar_musica_bloqueia_alterar_album(app, usuario_padrao, musica_padrao):
    """Impede alterar o álbum ao qual a música pertence."""
    with app.app_context():
        # Arrange
        dados = {"album_id": 999}
        # Act
        resultado, status = MusicaService.editar_musica(musica_padrao, dados, usuario_id=usuario_padrao)
        # Assert
        assert status == 400
        assert "Não é permitido alterar o álbum" in resultado["error"]


def test_editar_musica_sem_permissao(app, musica_padrao, usuario_secundario):
    """Impede que outro usuário edite a música."""
    with app.app_context():
        # Arrange
        dados = {"titulo": "Título Alterado"}
        # Act
        resultado, status = MusicaService.editar_musica(musica_padrao, dados, usuario_id=usuario_secundario)
        # Assert
        assert status == 403
        assert "não tem permissão" in resultado["error"]

        db.session.expire_all()
        musica = db.session.get(Musica, musica_padrao)

        assert musica is not None
        assert musica.titulo == "Feel Special"

def test_deletar_musica_sucesso(app, usuario_padrao, musica_padrao):
    """Verifica a exclusão da música pelo proprietário."""
    with app.app_context():
        # Act
        resultado, status = MusicaService.deletar_musica(musica_padrao, usuario_id=usuario_padrao)
        # Assert
        assert status == 200
        assert "deletada com sucesso" in resultado["message"]

        db.session.expire_all()
        assert db.session.get(Musica, musica_padrao) is None

def test_deletar_musica_sem_permissao(app, musica_padrao, usuario_secundario):
    """Impede que outro usuário exclua a música."""
    with app.app_context():
        # Act
        resultado, status = MusicaService.deletar_musica(musica_padrao, usuario_id=usuario_secundario)
        # Assert
        assert status == 403
        assert "não tem permissão" in resultado["error"]
        assert db.session.get(Musica, musica_padrao) is not None
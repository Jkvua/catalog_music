import pytest
from datetime import date
from app.extensions import db
from app.models.usuario import Usuario
from app.models.artista import Artista
from app.models.album import Album
from app.models.musica import Musica
from app.models.avaliacao import Avaliacao
from app.services.avaliacoes import AvaliacaoService

@pytest.fixture
def usuario_padrao(app):
    with app.app_context():
        usuario = Usuario(
            user="Camila",
            email="camila@example.com",
            password="123456"
        )

        db.session.add(usuario)
        db.session.commit()
        return usuario.id

@pytest.fixture
def usuario_secundario(app):
    with app.app_context():
        usuario = Usuario(
            user="Carol",
            email="carol@example.com",
            password="123456"
        )

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
def avaliacao_padrao(app, usuario_padrao, album_padrao):
    with app.app_context():
        avaliacao = Avaliacao(
            usuario_id=usuario_padrao,
            album_id=album_padrao,
            nota=5,
            comentario="Simplesmente perfeito!",
            data_escuta=date(2026, 10, 10)
        )

        db.session.add(avaliacao)
        db.session.commit()
        return avaliacao.id

def test_criar_avaliacao_sucesso(app, usuario_padrao, album_padrao):
    """Verifica a criação de uma avaliação para um álbum existente."""
    with app.app_context():
        # Arrange
        dados = {
            "nota": 4,
            "comentario": "Que perfeito, nunca escutei nada igual",
            "data_escuta": "2026-10-11",
            "album_id": album_padrao
        }
        # Act
        resultado, status = AvaliacaoService.criar_avaliacao(dados, usuario_id=usuario_padrao)
        # Assert
        assert status == 201
        assert resultado.nota == dados["nota"]
        assert resultado.comentario == dados["comentario"]

        avaliacao = db.session.get(Avaliacao, resultado.id)

        assert avaliacao is not None
        assert avaliacao.album_id == album_padrao
        assert avaliacao.usuario_id == usuario_padrao

def test_criar_avaliacao_album_inexistente(app, usuario_padrao):
    """Impede a criação de avaliação para um álbum inexistente."""
    with app.app_context():
        # Arrange
        dados = {
            "nota": 5,
            "comentario": "Bom",
            "data_escuta": "2026-10-11",
            "album_id": 9999
        }
        # Act
        resultado, status = AvaliacaoService.criar_avaliacao(dados, usuario_id=usuario_padrao)
        # Assert
        assert status == 404
        assert "não encontrado" in resultado["error"]

def test_criar_avaliacao_duplicada(
    app, usuario_padrao, album_padrao, avaliacao_padrao):
    """Impede duas avaliações do mesmo usuário para o mesmo álbum."""
    with app.app_context():
        # Arrange
        dados = {
            "nota": 3,
            "comentario": "Outra vez",
            "data_escuta": "2026-10-11",
            "album_id": album_padrao
        }
        # Act
        resultado, status = AvaliacaoService.criar_avaliacao(dados, usuario_id=usuario_padrao)
        # Assert
        assert status == 400
        assert "Já existe avaliação" in resultado["error"]

        quantidade = Avaliacao.query.filter_by(usuario_id=usuario_padrao, album_id=album_padrao).count()

        assert quantidade == 1

def test_criar_avaliacao_com_novo_album_e_artista_aninhado(app, usuario_padrao):
    """Verifica a criação conjunta de artista, álbum, música e avaliação."""
    with app.app_context():
        # Arrange
        dados = {
            "nota": 5,
            "comentario": "Obra prima!",
            "data_escuta": "2026-10-11",
            "album": {
                "titulo": "Album Aninhado Novo",
                "ano": 2022,
                "artista": {
                    "nome": "Artista Novo Inédito",
                    "genero": "Pop",
                    "pais": "Coreia do Sul"
                },
                "musicas": [
                    {
                        "titulo": "Musica Nova 1",
                        "duracao": "03:00"
                    }
                ]
            }
        }
        # Act
        resultado, status = AvaliacaoService.criar_avaliacao(dados, usuario_id=usuario_padrao)

        # Assert
        assert status == 201
        assert resultado.nota == 5
        artista = Artista.query.filter_by( nome="Artista Novo Inédito", usuario_id=usuario_padrao).first()

        assert artista is not None
        album = Album.query.filter_by(titulo="Album Aninhado Novo", artista_id=artista.id, usuario_id=usuario_padrao).first()

        assert album is not None
        musica = Musica.query.filter_by(titulo="Musica Nova 1", album_id=album.id).first()

        assert musica is not None
        assert musica.duracao == "03:00"

        avaliacao = db.session.get(Avaliacao, resultado.id)

        assert avaliacao is not None
        assert avaliacao.album_id == album.id

def test_editar_avaliacao_sem_permissao(
    app, avaliacao_padrao, usuario_secundario):
    """Impede que outro usuário edite a avaliação."""
    with app.app_context():
        # Arrange
        dados = {"nota": 1, "comentario": "Alterado sem permissão"}
        # Act
        resultado, status = AvaliacaoService.editar_avaliacao(avaliacao_padrao, dados, usuario_id=usuario_secundario)
        # Assert
        assert status == 403
        assert "não tem permissão" in resultado["error"]

        db.session.expire_all()
        avaliacao = db.session.get(Avaliacao, avaliacao_padrao)

        assert avaliacao is not None
        assert avaliacao.nota == 5
        assert avaliacao.comentario == "Simplesmente perfeito!"

def test_editar_avaliacao_com_album_e_musicas(app, usuario_padrao, avaliacao_padrao, album_padrao):
    """Verifica a edição da avaliação e de seus dados relacionados."""
    with app.app_context():
        # Arrange
        dados = {
            "nota": 4,
            "comentario": "Editado com sucesso",
            "data_escuta": "2026-10-12",
            "album": {
                "titulo": "Feel Special Editado",
                "ano": 2019,
                "musicas": [
                    {
                        "titulo": "Feel Special Remasterizada",
                        "duracao": "03:30"
                    }
                ]
            }
        }
        # Act
        resultado, status = AvaliacaoService.editar_avaliacao(avaliacao_padrao, dados, usuario_id=usuario_padrao)
        # Assert
        assert status == 200
        assert resultado.nota == dados["nota"]

        db.session.expire_all()
        avaliacao = db.session.get(Avaliacao, avaliacao_padrao)

        assert avaliacao is not None
        assert avaliacao.nota == dados["nota"]
        assert avaliacao.comentario == dados["comentario"]
        assert avaliacao.data_escuta == date(2026, 10, 12)

        album = db.session.get(Album, album_padrao)
        assert album is not None
        assert album.titulo == "Feel Special Editado"

        musica = Musica.query.filter_by(titulo="Feel Special Remasterizada", album_id=album_padrao).first()
        assert musica is not None
        assert musica.duracao == "03:30"

def test_deletar_avaliacao_sucesso(app, usuario_padrao, avaliacao_padrao):
    """Verifica a exclusão de uma avaliação pelo proprietário."""
    with app.app_context():
        # Arrange
        avaliacao_id = avaliacao_padrao
        # Act
        resultado, status = AvaliacaoService.delete_avaliacao(avaliacao_id, usuario_id=usuario_padrao)
        # Assert
        assert status == 200
        assert resultado["id"] == avaliacao_id
        assert "album" in resultado

        db.session.expire_all()
        avaliacao = db.session.get(Avaliacao, avaliacao_id)
        assert avaliacao is None
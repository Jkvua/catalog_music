import pytest
from unittest.mock import  patch
from app.services.musica import MusicaService
from app.models.musica import Musica
from app.models.album import Album
from app.models.artista import Artista
from app.models.usuario import Usuario
from app.extensions import db

@pytest.fixture
def usuario_padrao(app):
    """Usuario base para teste de service de musica"""
    with app.app_context():
        usuario = Usuario(id=1, user="Camila", email="camila@exemplo.com", password="123456")
        db.session.add(usuario)
        db.session.commit()
        yield usuario

@pytest.fixture
def artista_padrao(app, usuario_padrao):
    """artista base"""
    with app.app_context():
        artista = Artista(id=1, nome="TWICE", genero="K-POP", pais="Coreia do Sul", usuario_id=usuario_padrao.id)
        db.session.add(artista)
        db.session.commit()
        yield artista

@pytest.fixture
def album_padrao(app, usuario_padrao, artista_padrao):
    """album padrao"""
    with app.app_context():
        album = Album(titulo="Feel Special", ano=2019, artista_id=artista_padrao.id, usuario_id=usuario_padrao.id)
        db.session.add(album)
        db.session.commit()
        yield album

@pytest.fixture
def musica_padrao(app, usuario_padrao, album_padrao):
    with app.app_context():
        musica = Musica(titulo="Feel Special", duracao="03:27", album_id=album_padrao.id, usuario_id=usuario_padrao.id)
        db.session.add(musica)
        db.session.commit()
        yield musica

@patch('app.services.musica.get_jwt_identity')
def test_criar_musica_sucesso(mock_jwt, app, usuario_padrao, album_padrao, artista_padrao):
    """Testa a criacao de uma musica enviando os dados corretos"""
    mock_jwt.return_value = usuario_padrao.id

    with app.app_context():
        dados = {
            "titulo": "Rainbow",
            "duracao": "03:30",
            "album_id": album_padrao.id,
            "artista_id": artista_padrao.id
        }

        resultado, status = MusicaService.criar_musica(dados)
        assert status == 201
        assert resultado.titulo == "Rainbow"
        assert resultado.duracao == "03:30"

@patch('app.services.musica.get_jwt_identity')
def test_criar_musica_duracao_invalida(mock_jwt, app, usuario_padrao, album_padrao, artista_padrao):
    """Testa se a regra de negocio barra uma duracao invalida"""
    mock_jwt.return_value = usuario_padrao.id

    with app.app_context():
        dados = {
            "titulo": "Tempos Modernos",
            "duracao": "3:78",
            "album_id": album_padrao.id,
            "artista_id": artista_padrao.id
        }

        resultado, status = MusicaService.criar_musica(dados)
        assert status == 400
        assert "inválido, use MM:SS" in resultado["error"]

@patch('app.services.musica.get_jwt_identity')
def test_editar_musica_sucesso(mock_jwt, app, usuario_padrao, musica_padrao):
    """Testa a edicao de uma musica enviando os dados corretos"""
    mock_jwt.return_value = usuario_padrao.id

    with app.app_context():
        dados_novos = {"titulo": "Feel Special (Remix)", "duracao": "04:15"}
        resultado, status = MusicaService.editar_musica(musica_padrao.id, dados_novos)

        assert status == 200
        assert resultado.titulo == "Feel Special (Remix)"
        assert resultado.duracao == "04:15"  

@patch('app.services.musica.get_jwt_identity')
def test_editar_musica_sem_permissao(mock_jwt, app, musica_padrao):
    """Testa se a regra de negocio barra edições não autorizadas"""
    mock_jwt.return_value = musica_padrao.usuario_id

    with app.app_context():
        usuario_invasor = Usuario(id=2, user="Weverton", email="weverton@gmail.com", password="123456")
        db.session.add(usuario_invasor)
        db.session.commit()

        mock_jwt.return_value = usuario_invasor.id
        dados_novos = {"titulo": "Flash (Minha mente)"}

        resultado, status = MusicaService.editar_musica(musica_padrao.id, dados_novos)

        assert status == 403
        assert "não tem permissão" in resultado["error"]

@patch('app.services.musica.get_jwt_identity')
def test_deletar_musica_sucesso(mock_jwt, app, usuario_padrao, musica_padrao):
    """Testa a exclusão de uma música com sucesso"""
    mock_jwt.return_value = usuario_padrao.id

    with app.app_context():
        resultado, status = MusicaService.deletar_musica(musica_padrao.id)

        assert status == 200
        assert "deletada com sucesso" in resultado["message"]
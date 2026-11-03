import pytest
from unittest.mock import patch
from app.services.album import AlbumService
from app.models.album import Album
from app.models.artista import Artista
from app.models.usuario import Usuario
from app.extensions import db

@pytest.fixture
def usuario_padrao(app):
    """usuario base para todos os testes"""
    with app.app_context():
        usuario = Usuario(id=1, user="Camila", email="camila@exemple.com", password="123456")
        db.session.add(usuario)
        db.session.commit()
        yield usuario

@pytest.fixture
def artista_padrao(app, usuario_padrao):
    """artista base para vincular ao usuario padrao"""
    with app.app_context():
        artista = Artista(id=1, nome="TWICE", genero="K-POP", pais="Coreia do Sul", usuario_id=usuario_padrao.id)
        db.session.add(artista)
        db.session.commit()
        yield artista

@pytest.fixture
def album_padrao(app, usuario_padrao, artista_padrao):
    """album base para vincular a artista e usuario"""
    with app.app_context():
        album = Album(titulo="Fancy You", ano=2019, artista_id=artista_padrao.id, usuario_id=usuario_padrao.id)
        db.session.add(album)
        db.session.commit()
        yield album

@patch('app.services.album.get_jwt_identity')
def test_criar_album_com_artista_id(mock_jwt, app, usuario_padrao, artista_padrao):
    """Criacao de album passando o ID numerico do artista"""
    mock_jwt.return_value = usuario_padrao.id

    with app.app_context():
        dados = {"titulo": "Formula of Love", "ano": 2021, "artista_id": artista_padrao.id}
        resultado, status = AlbumService.criar_album(dados)

        assert status == 201
        assert resultado.titulo == "Formula of Love"
        assert resultado.artista_id == artista_padrao.id

@patch('app.services.album.get_jwt_identity')
def test_criar_album_com_nome_artista(mock_jwt, app, usuario_padrao, artista_padrao):
    """Criacao de album passando 'nome' do artista"""
    mock_jwt.return_value = usuario_padrao.id

    with app.app_context():
        dados = {"titulo": "Feel Special", "ano": 2019, "artista": "TWICE"}
        resultado, status = AlbumService.criar_album(dados)

        assert status == 201
        assert resultado.artista_id == artista_padrao.id

@patch('app.services.album.get_jwt_identity')
def test_criar_album_invalido(mock_jwt, app, usuario_padrao, artista_padrao):
    """criacao de album com data de lancamento invalido"""
    mock_jwt.return_value = usuario_padrao.id

    with app.app_context():
        dados = {"titulo": "Album velho", "ano": 1800, "artista_id": artista_padrao.id}
        resultado, status = AlbumService.criar_album(dados)

        assert status == 400
        assert "entre 1900 e 2100" in resultado["error"]

@patch('app.services.album.get_jwt_identity')
def test_editar_album_bloqueia_editar_artista(mock_jwt, app, usuario_padrao, album_padrao):
    """testa bloquio que impede que um album troque de dono/artista"""
    mock_jwt.return_value = usuario_padrao.id

    with app.app_context():
        dados_novos = {"artista_id":999}
        resultado, status = AlbumService.editar_album(album_padrao.id, dados_novos)

        assert status == 400
        assert "Não é permitido alterar o artista" in resultado["error"]

@patch('app.services.album.get_jwt_identity')
def test_editar_album_sem_permicao(mock_jwt, app, album_padrao):
    """Testar se o sistema bloqueia edição feita por outros usuários"""
    with app.app_context():
        usuario_invasor = Usuario(id=2, user="joaozinho", email="joaozinho@exemplo.com", password="123456")
        db.session.add(usuario_invasor)
        db.session.commit()
        
        mock_jwt.return_value = usuario_invasor.id
        dados_novos = {"titulo": "Cacos de vidro"}

        resultado, status = AlbumService.editar_album(album_padrao.id, dados_novos)

        assert status == 403
        assert "não tem permissão" in resultado["error"]
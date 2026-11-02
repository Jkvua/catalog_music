import pytest
from unittest.mock import patch
from datetime import date
from app.services.avaliacoes import AvaliacaoService
from app.models.avaliacao import Avaliacao
from app.models.album import Album
from app.models.artista import Artista
from app.models.usuario import Usuario
from app.extensions import db

@pytest.fixture
def usuario_padrao(app):
    with app.app_context():
        usuario = Usuario(id=1, user="Camila", email="camila@exemple.com", password="123456")
        db.session.add(usuario)
        db.session.commit()
        yield usuario

@pytest.fixture
def artista_padrao(app, usuario_padrao):
    with app.app_context():
        artista = Artista(id=1, nome="TWICE", genero="K-POP", pais="Coreia do Sul", usuario_id=usuario_padrao.id)
        db.session.add(artista)
        db.session.commit()
        yield artista

@pytest.fixture
def album_padrao(app, usuario_padrao, artista_padrao):
    with app.app_context():
        album = Album(titulo="Feel Special", ano="2019", artista_id=artista_padrao.id, usuario_id=usuario_padrao.id)
        db.session.add(album)
        db.session.commit()
        yield album

@pytest.fixture
def avaliacao_padrao(app, usuario_padrao, album_padrao):
    with app.app_context():
        avaliacao = Avaliacao(usuario_id=usuario_padrao.id, album_id=album_padrao.id, nota=5, comentario="Simplismente perfeito!", data_escuta=date(2026, 10, 10))
        db.session.add(avaliacao)
        db.session.commit()
        yield avaliacao

@patch('app.services.avaliacoes.get_jwt_identity')
def test_criar_avaliacao_sucesso(mock_jwt, app, usuario_padrao, album_padrao):
    """Testar a criacao de uma avaliacao informando o ID de um album que existe"""
    mock_jwt.return_value = usuario_padrao.id

    with app.app_context():
        dados = {
            "nota": 4,
            "comentario": "Que perfeito, nunca escutei nada igual",
            "data_escuta": "2026-10-11",
            "album_id": album_padrao.id
        }

        resultado, status = AvaliacaoService.criar_avaliacao(dados)

        assert status == 201
        assert resultado.nota == 4
        assert resultado.comentario == "Que perfeito, nunca escutei nada igual"

@patch('app.services.avaliacoes.get_jwt_identity')
def test_criar_avaliacao_nota_invalida(mock_jwt, app, usuario_padrao, album_padrao):
    """Garante que uma nota invalida/maior que 5 seja validada"""
    mock_jwt.return_value = usuario_padrao.id

    with app.app_context():
        dados = {
            "nota": 10,
            "comentario": "O melhor que já escutei",
            "data_escuta": "2026-10-15",
            "album_id": album_padrao.id
        }

        resultado, status = AvaliacaoService.criar_avaliacao(dados)

        assert status == 400
        assert "entre 1 e 5" in resultado["error"]

@patch('app.services.avaliacoes.get_jwt_identity')
def test_editar_avalicao_sucesso(mock_jwt, app, usuario_padrao, avaliacao_padrao):
    """Testar edicao de uma avaliacao"""
    mock_jwt.return_value = usuario_padrao.id

    with app.app_context():
        dados = {"nota": 3, "comentario": "Pensando bem, não é tão bom assim!"}
        resultado, status = AvaliacaoService.editar_avaliacao(avaliacao_padrao.id, dados)

        assert status == 200
        assert resultado.nota == 3
        assert resultado.comentario == "Pensando bem, não é tão bom assim!"

@patch('app.services.avaliacoes.get_jwt_identity')
def test_editar_avaliacao_sem_permicao(mock_jwt, app, avaliacao_padrao):
    """Testa bloqueio de tentativa de editar avaliacao sem permicao"""
    with app.app_context():
        invasor = Usuario(id=2, user="Invasor", email="invasor@exemple.com", password="123456")
        db.session.add(invasor)
        db.session.commit()

        mock_jwt.return_value = invasor.id
        dados = {"nota": 1, "comentario": "Hackeado!"}

        resultado, status = AvaliacaoService.editar_avaliacao(avaliacao_padrao.id, dados)

        assert status == 403
        assert "não tem permissão" in resultado["error"]

@patch('app.services.avaliacoes.get_jwt_identity')
def test_deletar_avalicao_sucesso(mock_jwt, app, usuario_padrao, avaliacao_padrao):
    """Testa se o dono da avalicao consegue deleta-lá"""
    mock_jwt.return_value = usuario_padrao.id

    with app.app_context():
        resultado, status = AvaliacaoService.delete_avaliacao(avaliacao_padrao.id)

        assert status == 200
        assert resultado["id"] == avaliacao_padrao.id
        assert "album" in resultado
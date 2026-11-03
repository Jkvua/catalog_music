import pytest
from unittest.mock import patch
from app.services.artista import ArtistaService
from app.models.artista import Artista
from app.models.usuario import Usuario
from app.extensions import db

@pytest.fixture
def usuario_padrao(app):
    """criando usuario base"""
    with app.app_context():
        usuario = Usuario(id=1, user="Camila", email="camila@exemple.com", password="123456")
        db.session.add(usuario)
        db.session.commit()
        
        yield usuario

# usamos o path "sequestrar" o get_jwt_identity (fazemos um mock(simulacao))
@patch('app.services.artista.get_jwt_identity')
def test_criar_artista_sucesso(mock_jwt, app, usuario_padrao):
    """testando caminho de sucesso"""
    mock_jwt.return_value = usuario_padrao.id   #usamos o usuario base

    with app.app_context():
        dados = {"nome": "TWICE", "genero": "K-POP", "pais":"Coreia do Sul"}
        resultado, status = ArtistaService.criar_artista(dados)

        assert status == 201
        assert resultado.nome == "TWICE"
        assert resultado.usuario_id == usuario_padrao.id

@patch('app.services.artista.get_jwt_identity')
def test_criar_artista_duplicado(mock_jwt, app, usuario_padrao):
    """Testar a criacao de artista duplicado"""
    mock_jwt.return_value = usuario_padrao.id

    with app.app_context():
        dados = {"nome": "NewJeans", "genero": "K-POP", "pais": "Coreia do Sul"}

        ArtistaService.criar_artista(dados) #criando pela primeira vez
        resultado, status = ArtistaService.criar_artista(dados) # tentando duplicar

        assert status == 400
        assert "já existe no catálogo" in resultado["error"]

@patch('app.services.artista.get_jwt_identity')
def test_editar_artista_sem_permissao(mock_jwt, app, usuario_padrao):
    """Testar edicao de usuario outro usuario sem permissao"""
    with app.app_context():
        usuario2 = Usuario(id=2, user="Carol", email="carol@exemple.com", password="123456")
        db.session.add(usuario2)
        db.session.commit()

        mock_jwt.return_value = usuario_padrao.id
        dados = {"nome":"Sissi", "genero": "MPB", "pais": "Brasil"} # usuario 1 loga e cria o artista
        artista, _ = ArtistaService.criar_artista(dados)

        mock_jwt.return_value = usuario2.id
        dados_novos = {"nome": "Sissi Editada"}

        resultado, status = ArtistaService.editar_artista(artista.id, dados_novos)

        assert status == 403
        assert "não tem permissão" in resultado["error"] 
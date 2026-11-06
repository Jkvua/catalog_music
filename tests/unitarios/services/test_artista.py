import pytest
from app.services.artista import ArtistaService
from app.models.artista import Artista
from app.models.usuario import Usuario
from app.extensions import db

@pytest.fixture
def usuario_padrao(app):
    """Criando usuario base"""
    with app.app_context():
        usuario = Usuario(id=1, user="Camila", email="camila@exemple.com", password="123456")
        db.session.add(usuario)
        db.session.commit()
        yield usuario

@pytest.fixture
def artista_padrao(app, usuario_padrao):
    """Criando artista base vinculada ao usuario padrao"""
    with app.app_context():
        artista = Artista(nome="TWICE Base", genero="K-POP", pais="Coreia do Sul", usuario_id=usuario_padrao.id)
        db.session.add(artista)
        db.session.commit()
        yield artista

def test_criar_artista_sucesso(app, usuario_padrao):
    """Testando caminho de sucesso"""
    with app.app_context():
        dados = {"nome": "TWICE", "genero": "K-POP", "pais": "Coreia do Sul"}
        resultado, status = ArtistaService.criar_artista(dados, usuario_id=usuario_padrao.id)

        assert status == 201
        assert resultado.nome == "TWICE"
        assert resultado.usuario_id == usuario_padrao.id

def test_criar_artista_duplicado(app, usuario_padrao):
    """Testar a criacao de artista duplicado"""
    with app.app_context():
        dados = {"nome": "NewJeans", "genero": "K-POP", "pais": "Coreia do Sul"}

        ArtistaService.criar_artista(dados, usuario_id=usuario_padrao.id)
        resultado, status = ArtistaService.criar_artista(dados, usuario_id=usuario_padrao.id)

        assert status == 400
        assert "já existe no catálogo" in resultado["error"]

@pytest.mark.parametrize("payload, erro_esperado", [
    ({"nome": "", "genero": "Pop", "pais": "Brasil"}, "nome do artista é obrigatório"),
    ({"nome": "TWICE", "genero": "", "pais": "Coreia do Sul"}, "gênero musical do artista é obrigatório"),
    ({"nome": "TWICE", "genero": "K-POP", "pais": ""}, "nacionalidade/país do artista é obrigatória"),
])
def test_criar_artista_campos_invalidos(app, usuario_padrao, payload, erro_esperado):
    """Cobre as validações de nome, gênero e país obrigatórios no criar_artista"""
    with app.app_context():
        resultado, status = ArtistaService.criar_artista(payload, usuario_id=usuario_padrao.id)

        assert status == 400
        assert erro_esperado in resultado["error"]

def test_editar_artista_sem_permissao(app, artista_padrao):
    """Testar edicao de outro usuario sem permissao"""
    with app.app_context():
        usuario2 = Usuario(id=2, user="Carol", email="carol@exemple.com", password="123456")
        db.session.add(usuario2)
        db.session.commit()

        # Passa o ID do invasor diretamente por argumento
        resultado, status = ArtistaService.editar_artista(artista_padrao.id, {"nome": "Sissi Editada"}, usuario_id=usuario2.id)

        assert status == 403
        assert "não tem permissão" in resultado["error"]

def test_editar_artista_nome_vazio(app, usuario_padrao, artista_padrao):
    """Cobre 'novo_nome e len(novo_nome.strip()) < 1'"""
    with app.app_context():
        resultado, status = ArtistaService.editar_artista(artista_padrao.id, {"nome": "   "}, usuario_id=usuario_padrao.id)

        assert status == 400
        assert "nome do artista deve conter pelo menos 1 caractere" in resultado["error"]

def test_editar_artista_nome_duplicado(app, usuario_padrao):
    """Cobre conflito ao alterar nome para outro artista que já existe no catálogo"""
    with app.app_context():
        artista1 = Artista(nome="NewJeans", genero="K-POP", pais="Coreia do Sul", usuario_id=usuario_padrao.id)
        artista2 = Artista(nome="IVE", genero="K-POP", pais="Coreia do Sul", usuario_id=usuario_padrao.id)
        db.session.add_all([artista1, artista2])
        db.session.commit()

        resultado, status = ArtistaService.editar_artista(artista2.id, {"nome": "NewJeans"}, usuario_id=usuario_padrao.id)

        assert status == 400
        assert "já existe no catálogo" in resultado["error"]

@pytest.mark.parametrize("payload, erro_esperado", [
    ({"genero": ""}, "gênero musical do artista é obrigatório"),
    ({"pais": ""}, "nacionalidade/país do artista é obrigatória"),
])
def test_editar_artista_genero_e_pais_invalidos(app, usuario_padrao, artista_padrao, payload, erro_esperado):
    """Cobre envios de gênero ou país vazios na edição"""
    with app.app_context():
        resultado, status = ArtistaService.editar_artista(artista_padrao.id, payload, usuario_id=usuario_padrao.id)

        assert status == 400
        assert erro_esperado in resultado["error"]

def test_editar_artista_sucesso(app, usuario_padrao, artista_padrao):
    """Cobre o caminho feliz de edição de gênero e país (Status 200)"""
    with app.app_context():
        novos_dados = {"nome": "TWICE Official", "genero": "Pop", "pais": "Japão"}
        resultado, status = ArtistaService.editar_artista(artista_padrao.id, novos_dados, usuario_id=usuario_padrao.id)

        assert status == 200
        assert resultado.nome == "TWICE Official"
        assert resultado.genero == "Pop"
        assert resultado.pais == "Japão"

def test_deletar_artista_sem_permissao(app, artista_padrao):
    """Cobre retorno 403 ao tentar deletar artista de outro usuário no Service"""
    with app.app_context():
        usuario_invasor = Usuario(id=99, user="invasor", email="invasor@exemplo.com", password="123")
        db.session.add(usuario_invasor)
        db.session.commit()

        # Passa o ID do invasor diretamente por argumento
        resultado, status = ArtistaService.deletar_artista(artista_padrao.id, usuario_id=usuario_invasor.id)

        assert status == 403
        assert "não tem permissão para deletar este artista" in resultado["error"]
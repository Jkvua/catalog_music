import pytest
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

def test_criar_album_com_artista_id(app, usuario_padrao, artista_padrao):
    """Criacao de album passando o ID numerico do artista"""
    with app.app_context():
        dados = {"titulo": "Formula of Love", "ano": 2021, "artista_id": artista_padrao.id}
        resultado, status = AlbumService.criar_album(dados, usuario_id=usuario_padrao.id)

        assert status == 201
        assert resultado.titulo == "Formula of Love"
        assert resultado.artista_id == artista_padrao.id

def test_criar_album_com_nome_artista(app, usuario_padrao, artista_padrao):
    """Criacao de album passando 'nome' do artista"""
    with app.app_context():
        dados = {"titulo": "Feel Special", "ano": 2019, "artista": "TWICE"}
        resultado, status = AlbumService.criar_album(dados, usuario_id=usuario_padrao.id)

        assert status == 201
        assert resultado.artista_id == artista_padrao.id

def test_criar_album_invalido(app, usuario_padrao, artista_padrao):
    """criacao de album com data de lancamento invalido"""
    with app.app_context():
        dados = {"titulo": "Album velho", "ano": 1800, "artista_id": artista_padrao.id}
        resultado, status = AlbumService.criar_album(dados, usuario_id=usuario_padrao.id)

        assert status == 400
        assert "entre 1900 e 2100" in resultado["error"]

def test_editar_album_bloqueia_editar_artista(app, usuario_padrao, album_padrao):
    """testa bloquio que impede que um album troque de dono/artista"""
    with app.app_context():
        dados_novos = {"artista_id": 999}
        resultado, status = AlbumService.editar_album(album_padrao.id, dados_novos, usuario_id=usuario_padrao.id)

        assert status == 400
        assert "Não é permitido alterar o artista" in resultado["error"]

def test_editar_album_sem_permicao(app, album_padrao):
    """Testar se o sistema bloqueia edição feita por outros usuários"""
    with app.app_context():
        usuario_invasor = Usuario(id=2, user="joaozinho", email="joaozinho@exemplo.com", password="123456")
        db.session.add(usuario_invasor)
        db.session.commit()
        
        dados_novos = {"titulo": "Cacos de vidro"}
        # Passa o ID do invasor diretamente na chamada do service!
        resultado, status = AlbumService.editar_album(album_padrao.id, dados_novos, usuario_id=usuario_invasor.id)

        assert status == 403
        assert "não tem permissão" in resultado["error"]

def test_criar_album_titulo_vazio(app, usuario_padrao, artista_padrao):
    """Garante que de erro se o titulo for vazio"""
    with app.app_context():
        resultado, status = AlbumService.criar_album({"titulo": "", "ano": 2023, "artista_id": artista_padrao.id}, usuario_id=usuario_padrao.id)
        assert status == 400
        assert "O nome do álbum é obrigatório" in resultado["error"]

def test_criar_album_artista_inexistente(app, usuario_padrao):
    """Garante erro se o artista_id nao existir no banco"""
    with app.app_context():
        resultado, status = AlbumService.criar_album({"titulo": "Album Teste", "ano": 2023, "artista_id": 9999}, usuario_id=usuario_padrao.id)
        assert status == 404
        assert "não encontrado" in resultado["error"]

def test_criar_album_sem_artista_informado(app, usuario_padrao):
    """Garante erro se nao passar nem ID nem Nome do artista"""
    with app.app_context():
        resultado, status = AlbumService.criar_album({"titulo": "Album Teste", "ano": 2023}, usuario_id=usuario_padrao.id)
        assert status == 400
        assert "informar o nome do artista ou o ID" in resultado["error"]

def test_criar_album_duplicado(app, usuario_padrao, album_padrao):
    """Garante erro se tentar cadastrar o mesmo album para o mesmo artista"""
    with app.app_context():
        dados = {"titulo": album_padrao.titulo, "ano": 2023, "artista_id": album_padrao.artista_id}
        resultado, status = AlbumService.criar_album(dados, usuario_id=usuario_padrao.id)
        assert status == 400
        assert "já existe para esse artista" in resultado["error"]

def test_deletar_album_sem_permissao(app, album_padrao):
    """Garante erro se outro usuario tentar deletar o album"""
    with app.app_context():
        usuario_invasor = Usuario(id=99, user="invasor", email="invasor@exemplo.com", password="123")
        db.session.add(usuario_invasor)
        db.session.commit()
        
        # Passa o ID do invasor diretamente
        resultado, status = AlbumService.deletar_album(album_padrao.id, usuario_id=usuario_invasor.id)

        assert status == 403
        assert "não tem permissão" in resultado["error"]

def test_criar_album_com_nome_artista_inexistente(app, usuario_padrao):
    """Cobre o 'elif artista_nome:' quando o artista não existe (Status 404)"""
    with app.app_context():
        dados = {"titulo": "Album Fantasma", "ano": 2022, "artista": "Artista Que Nao Existe"}
        resultado, status = AlbumService.criar_album(dados, usuario_id=usuario_padrao.id)

        assert status == 404
        assert "não encontrado" in resultado["error"]

def test_criar_album_sem_campo_ano(app, usuario_padrao, artista_padrao):
    """Cobre o 'if not ano:' quando o campo ano é omitido (Status 400)"""
    with app.app_context():
        dados = {"titulo": "Album Sem Ano", "artista_id": artista_padrao.id}
        resultado, status = AlbumService.criar_album(dados, usuario_id=usuario_padrao.id)

        assert status == 400
        assert "ano de lançamento do álbum é obrigatório" in resultado["error"]

def test_criar_album_ano_texto_invalido(app, usuario_padrao, artista_padrao):
    """Cobre o 'except (ValueError, AttributeError):' do ano inválido (Status 400)"""
    with app.app_context():
        dados = {"titulo": "Album Teste", "ano": "texto_invalido", "artista_id": artista_padrao.id}
        resultado, status = AlbumService.criar_album(dados, usuario_id=usuario_padrao.id)

        assert status == 400
        assert "deve ser um número inteiro" in resultado["error"]

def test_criar_album_sem_artista_id_nem_nome(app, usuario_padrao):
    """Cobre o bloco 'else:' quando não é passado artista_id nem artista (Status 400)"""
    with app.app_context():
        dados = {"titulo": "Album Solto", "ano": 2020}
        resultado, status = AlbumService.criar_album(dados, usuario_id=usuario_padrao.id)

        assert status == 400
        assert "informar o nome do artista ou o ID" in resultado["error"]

def test_editar_album_sucesso(app, usuario_padrao, album_padrao):
    """Cobre a edição com sucesso de título e ano (Status 200)"""
    with app.app_context():
        dados_novos = {"titulo": "Fancy You Deluxe", "ano": 2020}
        resultado, status = AlbumService.editar_album(album_padrao.id, dados_novos, usuario_id=usuario_padrao.id)

        assert status == 200
        assert resultado.titulo == "Fancy You Deluxe"
        assert resultado.ano == 2020

def test_editar_album_titulo_apenas_espacos(app, usuario_padrao, album_padrao):
    """Cobre o 'if novo_titulo and len(novo_titulo.strip()) < 1:' (Status 400)"""
    with app.app_context():
        dados_novos = {"titulo": "    "}
        resultado, status = AlbumService.editar_album(album_padrao.id, dados_novos, usuario_id=usuario_padrao.id)

        assert status == 400
        assert "pelo menos 1 caractere" in resultado["error"]

def test_editar_album_tentativa_alterar_artista_nome(app, usuario_padrao, album_padrao):
    """Cobre a verificação de 'artista_nome em dados' na edição (Status 400)"""
    with app.app_context():
        dados_novos = {"artista_nome": "Outro Artista"}
        resultado, status = AlbumService.editar_album(album_padrao.id, dados_novos, usuario_id=usuario_padrao.id)

        assert status == 400
        assert "Não é permitido alterar o artista" in resultado["error"]

def test_editar_album_ano_vazio(app, usuario_padrao, album_padrao):
    """Cobre o 'if 'ano' in dados and not dados['ano']:' (Status 400)"""
    with app.app_context():
        dados_novos = {"ano": None}
        resultado, status = AlbumService.editar_album(album_padrao.id, dados_novos, usuario_id=usuario_padrao.id)

        assert status == 400
        assert "ano de lançamento do álbum é obrigatório" in resultado["error"]

def test_editar_album_ano_invalido_e_limite(app, usuario_padrao, album_padrao):
    """Cobre a validação de formato e limites de ano na edição (Status 400)"""
    with app.app_context():
        res1, st1 = AlbumService.editar_album(album_padrao.id, {"ano": "invalido"}, usuario_id=usuario_padrao.id)
        assert st1 == 400
        assert "deve ser um número inteiro" in res1["error"]

        res2, st2 = AlbumService.editar_album(album_padrao.id, {"ano": 1850}, usuario_id=usuario_padrao.id)
        assert st2 == 400
        assert "entre 1900 e 2100" in res2["error"]

def test_deletar_album_sucesso(app, usuario_padrao, album_padrao):
    """Cobre a deleção de álbum bem-sucedida pelo dono (Status 200)"""
    with app.app_context():
        resultado, status = AlbumService.deletar_album(album_padrao.id, usuario_id=usuario_padrao.id)

        assert status == 200
        assert "deletado com sucesso" in resultado["message"]
import pytest
from app.services.musica import MusicaService
from app.models.musica import Musica
from app.models.album import Album
from app.models.artista import Artista
from app.models.usuario import Usuario
from app.extensions import db

# -----------------------------------------------------------------------------
# FIXTURES BASE ENCADEADAS
# -----------------------------------------------------------------------------

@pytest.fixture
def usuario_padrao(app):
    """Usuário base para os testes de serviço de música (ID=1)"""
    with app.app_context():
        usuario = Usuario(id=1, user="Camila", email="camila@exemplo.com", password="123456")
        db.session.add(usuario)
        db.session.commit()
        yield usuario

@pytest.fixture
def artista_padrao(app, usuario_padrao):
    """Artista base para vincular ao usuário padrão"""
    with app.app_context():
        artista = Artista(id=1, nome="TWICE", genero="K-POP", pais="Coreia do Sul", usuario_id=usuario_padrao.id)
        db.session.add(artista)
        db.session.commit()
        yield artista

@pytest.fixture
def album_padrao(app, usuario_padrao, artista_padrao):
    """Álbum base para vincular a artista e usuário"""
    with app.app_context():
        album = Album(titulo="Feel Special", ano=2019, artista_id=artista_padrao.id, usuario_id=usuario_padrao.id)
        db.session.add(album)
        db.session.commit()
        yield album

@pytest.fixture
def musica_padrao(app, usuario_padrao, album_padrao):
    """Música base salva no banco"""
    with app.app_context():
        musica = Musica(titulo="Feel Special", duracao="03:27", album_id=album_padrao.id, usuario_id=usuario_padrao.id)
        db.session.add(musica)
        db.session.commit()
        yield musica

# -----------------------------------------------------------------------------
# TESTES DE CRIAÇÃO DE MÚSICA (HAPPY PATHS E VALIDAÇÕES)
# -----------------------------------------------------------------------------

def test_criar_musica_sucesso_com_ids(app, usuario_padrao, album_padrao, artista_padrao):
    """Criar música com sucesso informando album_id e artista_id"""
    with app.app_context():
        dados = {
            "titulo": "Rainbow",
            "duracao": "03:30",
            "album_id": album_padrao.id,
            "artista_id": artista_padrao.id
        }
        resultado, status = MusicaService.criar_musica(dados, usuario_id=usuario_padrao.id)
        assert status == 201
        assert resultado.titulo == "Rainbow"
        assert resultado.duracao == "03:30"

def test_criar_musica_sucesso_com_nomes(app, usuario_padrao, album_padrao, artista_padrao):
    """Criar música com sucesso informando nomes textuais de álbum e artista"""
    with app.app_context():
        dados = {
            "titulo": "GET LOUD",
            "duracao": "03:07",
            "album": album_padrao.titulo,
            "artista": artista_padrao.nome
        }
        resultado, status = MusicaService.criar_musica(dados, usuario_id=usuario_padrao.id)
        assert status == 201
        assert resultado.album_id == album_padrao.id

@pytest.mark.parametrize("payload, erro_esperado, status_esperado", [
    ({"titulo": "", "duracao": "03:30", "album_id": 1, "artista_id": 1}, "título da música é obrigatório", 400),
    ({"titulo": "Trick It", "duracao": None, "album_id": 1, "artista_id": 1}, "duração da música é obrigatória", 400),
    ({"titulo": "Trick It", "duracao": "invalido", "album_id": 1, "artista_id": 1}, "formato inválido, use MM:SS", 400),
    ({"titulo": "Trick It", "duracao": "03:75", "album_id": 1, "artista_id": 1}, "Formato de duração da música inválido", 400), # <--- Ajustado para F maiúsculo
    ({"titulo": "Trick It", "duracao": "03:30", "artista_id": 1}, "informar o nome do album ou o ID", 400),
    ({"titulo": "Trick It", "duracao": "03:30", "album_id": 9999}, "não encontrado", 404), # <--- Ajustado para esperar 404 pois o álbum 9999 não existe
])
def test_criar_musica_validacoes_campos(app, usuario_padrao, payload, erro_esperado, status_esperado):
    with app.app_context():
        resultado, status = MusicaService.criar_musica(payload, usuario_id=usuario_padrao.id)
        assert status == status_esperado
        assert erro_esperado.lower() in resultado["error"].lower()

def test_criar_musica_album_id_nao_encontrado(app, usuario_padrao, artista_padrao):
    """Retorna 404 quando o album_id informado não existe"""
    with app.app_context():
        dados = {"titulo": "Love Foolish", "duracao": "03:12", "album_id": 9999, "artista_id": artista_padrao.id}
        resultado, status = MusicaService.criar_musica(dados, usuario_id=usuario_padrao.id)
        assert status == 404
        assert "não encontrado" in resultado["error"]

def test_criar_musica_album_nome_nao_encontrado(app, usuario_padrao, artista_padrao):
    """Retorna 404 quando o nome do álbum informado não existe"""
    with app.app_context():
        dados = {"titulo": "Love Foolish", "duracao": "03:12", "album": "Álbum Fantasma", "artista_id": artista_padrao.id}
        resultado, status = MusicaService.criar_musica(dados, usuario_id=usuario_padrao.id)
        assert status == 404
        assert "não encontrado" in resultado["error"]

def test_criar_musica_artista_id_nao_encontrado(app, usuario_padrao, album_padrao):
    """Retorna 404 quando o artista_id informado não existe"""
    with app.app_context():
        dados = {"titulo": "21:29", "duracao": "03:49", "album_id": album_padrao.id, "artista_id": 9999}
        resultado, status = MusicaService.criar_musica(dados, usuario_id=usuario_padrao.id)
        assert status == 404
        assert "não encontrado" in resultado["error"]

def test_criar_musica_artista_nome_nao_encontrado(app, usuario_padrao, album_padrao):
    """Retorna 404 quando o nome do artista informado não existe"""
    with app.app_context():
        dados = {"titulo": "21:29", "duracao": "03:49", "album_id": album_padrao.id, "artista": "Artista Fantasma"}
        resultado, status = MusicaService.criar_musica(dados, usuario_id=usuario_padrao.id)
        assert status == 404
        assert "não encontrado" in resultado["error"]

def test_criar_musica_duplicada(app, usuario_padrao, musica_padrao):
    """Garante erro 400 ao tentar cadastrar a mesma música duas vezes no mesmo álbum"""
    with app.app_context():
        dados = {
            "titulo": musica_padrao.titulo,
            "duracao": "03:27",
            "album_id": musica_padrao.album_id,
            "artista_id": musica_padrao.album.artista_id
        }
        resultado, status = MusicaService.criar_musica(dados, usuario_id=usuario_padrao.id)
        assert status == 400
        assert "ja existe para esse artista ou já existe nesse album" in resultado["error"]

# -----------------------------------------------------------------------------
# TESTES DE EDIÇÃO DE MÚSICA
# -----------------------------------------------------------------------------

def test_editar_musica_sucesso(app, usuario_padrao, musica_padrao):
    """Edição com sucesso de título e duração"""
    with app.app_context():
        dados_novos = {"titulo": "Feel Special (Remix)", "duracao": "04:15"}
        resultado, status = MusicaService.editar_musica(musica_padrao.id, dados_novos, usuario_id=usuario_padrao.id)

        assert status == 200
        assert resultado.titulo == "Feel Special (Remix)"
        assert resultado.duracao == "04:15"

def test_editar_musica_titulo_vazio(app, usuario_padrao, musica_padrao):
    """Garante erro 400 se o título for apenas espaços"""
    with app.app_context():
        resultado, status = MusicaService.editar_musica(musica_padrao.id, {"titulo": "   "}, usuario_id=usuario_padrao.id)
        assert status == 400
        assert "pelo menos 1 caractere" in resultado["error"]

def test_editar_musica_titulo_duplicado(app, usuario_padrao, album_padrao):
    """Garante erro 400 ao alterar o título para uma música já existente no mesmo álbum"""
    with app.app_context():
        m1 = Musica(titulo="Música A", duracao="03:00", album_id=album_padrao.id, usuario_id=usuario_padrao.id)
        m2 = Musica(titulo="Música B", duracao="03:00", album_id=album_padrao.id, usuario_id=usuario_padrao.id)
        db.session.add_all([m1, m2])
        db.session.commit()

        resultado, status = MusicaService.editar_musica(m2.id, {"titulo": "Música A"}, usuario_id=usuario_padrao.id)
        assert status == 400
        assert "já existe para esse artista neste álbum" in resultado["error"]

@pytest.mark.parametrize("duracao_invalida, erro_esperado", [
    ("texto_invalido", "em um formato inválido, use MM:SS"),
    ("03:80", "Formato de duração da música inválido, use MM:SS"),
])
def test_editar_musica_duracao_invalida(app, usuario_padrao, musica_padrao, duracao_invalida, erro_esperado):
    """Cobre edições com formatos de duração incorretos"""
    with app.app_context():
        resultado, status = MusicaService.editar_musica(musica_padrao.id, {"duracao": duracao_invalida}, usuario_id=usuario_padrao.id)
        assert status == 400
        assert erro_esperado in resultado["error"]

def test_editar_musica_bloqueia_alterar_album_id(app, usuario_padrao, musica_padrao):
    """Garante erro 400 ao tentar trocar a música de álbum na edição"""
    with app.app_context():
        resultado, status = MusicaService.editar_musica(musica_padrao.id, {"album_id": 999}, usuario_id=usuario_padrao.id)
        assert status == 400
        assert "Não é permitido alterar o álbum" in resultado["error"]

def test_editar_musica_sem_permissao(app, musica_padrao):
    """Garante erro 403 ao tentar editar música de outro usuário (Dono=1, Invasor=2)"""
    with app.app_context():
        usuario_invasor = Usuario(id=2, user="Weverton", email="weverton@gmail.com", password="123456")
        db.session.add(usuario_invasor)
        db.session.commit()

        # Passa o ID do invasor diretamente por argumento
        resultado, status = MusicaService.editar_musica(musica_padrao.id, {"titulo": "Invasão"}, usuario_id=usuario_invasor.id)

        assert status == 403
        assert "não tem permissão" in resultado["error"]

# -----------------------------------------------------------------------------
# TESTES DE DELEÇÃO DE MÚSICA
# -----------------------------------------------------------------------------

def test_deletar_musica_sucesso(app, usuario_padrao, musica_padrao):
    """Deleção de música com sucesso pelo proprietário"""
    with app.app_context():
        resultado, status = MusicaService.deletar_musica(musica_padrao.id, usuario_id=usuario_padrao.id)
        assert status == 200
        assert "deletada com sucesso" in resultado["message"]

def test_deletar_musica_sem_permissao(app, musica_padrao):
    """Garante erro 403 ao tentar deletar música de outro usuário (Dono=1, Invasor=99)"""
    with app.app_context():
        usuario_invasor = Usuario(id=99, user="invasor", email="invasor@exemplo.com", password="123")
        db.session.add(usuario_invasor)
        db.session.commit()

        # Passa o ID do invasor diretamente por argumento
        resultado, status = MusicaService.deletar_musica(musica_padrao.id, usuario_id=usuario_invasor.id)

        assert status == 403
        assert "não tem permissão para deletar esta música" in resultado["error"]
import pytest
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
        album = Album(titulo="Feel Special", ano=2019, artista_id=artista_padrao.id, usuario_id=usuario_padrao.id)
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

def test_criar_avaliacao_sucesso(app, usuario_padrao, album_padrao):
    """Testar a criacao de uma avaliacao informando o ID de um album que existe"""
    with app.app_context():
        dados = {
            "nota": 4,
            "comentario": "Que perfeito, nunca escutei nada igual",
            "data_escuta": "2026-10-11",
            "album_id": album_padrao.id
        }
        resultado, status = AvaliacaoService.criar_avaliacao(dados, usuario_id=usuario_padrao.id)

        assert status == 201
        assert resultado.nota == 4
        assert resultado.comentario == "Que perfeito, nunca escutei nada igual"

def test_criar_avaliacao_nota_invalida(app, usuario_padrao, album_padrao):
    """Garante que uma nota invalida/maior que 5 seja validada"""
    with app.app_context():
        dados = {
            "nota": 10,
            "comentario": "O melhor que já escutei",
            "data_escuta": "2026-10-15",
            "album_id": album_padrao.id
        }
        resultado, status = AvaliacaoService.criar_avaliacao(dados, usuario_id=usuario_padrao.id)

        assert status == 400
        assert "entre 1 e 5" in resultado["error"]

def test_editar_avalicao_sucesso(app, usuario_padrao, avaliacao_padrao):
    """Testar edicao de uma avaliacao"""
    with app.app_context():
        dados = {"nota": 3, "comentario": "Pensando bem, não é tão bom assim!"}
        resultado, status = AvaliacaoService.editar_avaliacao(avaliacao_padrao.id, dados, usuario_id=usuario_padrao.id)

        assert status == 200
        assert resultado.nota == 3
        assert resultado.comentario == "Pensando bem, não é tão bom assim!"

def test_editar_avaliacao_sem_permicao(app, avaliacao_padrao):
    """Testa bloqueio de tentativa de editar avaliacao sem permicao"""
    with app.app_context():
        invasor = Usuario(id=2, user="Invasor", email="invasor@exemple.com", password="123456")
        db.session.add(invasor)
        db.session.commit()

        dados = {"nota": 1, "comentario": "Hackeado!"}
        resultado, status = AvaliacaoService.editar_avaliacao(avaliacao_padrao.id, dados, usuario_id=invasor.id)

        assert status == 403
        assert "não tem permissão" in resultado["error"]

def test_deletar_avalicao_sucesso(app, usuario_padrao, avaliacao_padrao):
    """Testa se o dono da avalicao consegue deleta-lá"""
    with app.app_context():
        resultado, status = AvaliacaoService.delete_avaliacao(avaliacao_padrao.id, usuario_id=usuario_padrao.id)

        assert status == 200
        assert resultado["id"] == avaliacao_padrao.id
        assert "album" in resultado

def test_criar_avaliacao_nota_abaixo_minimo(app, usuario_padrao, album_padrao):
    """Cobre nota menor que 1 (Erro 400)"""
    with app.app_context():
        dados = {"nota": 0, "comentario": "Ruim", "data_escuta": "2026-10-11", "album_id": album_padrao.id}
        resultado, status = AvaliacaoService.criar_avaliacao(dados, usuario_id=usuario_padrao.id)
        assert status == 400
        assert "entre 1 e 5" in resultado["error"]

def test_criar_avaliacao_album_inexistente(app, usuario_padrao):
    """Cobre erro 404 ao avaliar um álbum que não existe"""
    with app.app_context():
        dados = {"nota": 5, "comentario": "Bom", "data_escuta": "2026-10-11", "album_id": 9999}
        resultado, status = AvaliacaoService.criar_avaliacao(dados, usuario_id=usuario_padrao.id)
        assert status == 404
        assert "não encontrado" in resultado["error"]

# --- NOVOS TESTES PARA COBRIR AS LINHAS VERMELHAS (ALTA COBERTURA) ---

def test_criar_avaliacao_erros_validacao(app, usuario_padrao, album_padrao):
    """Cobre comentário vazio, data ausente e formato de data inválido"""
    with app.app_context():
        # 1. Comentário vazio
        dados = {"nota": 5, "comentario": "", "data_escuta": "2026-10-11", "album_id": album_padrao.id}
        res, status = AvaliacaoService.criar_avaliacao(dados, usuario_id=usuario_padrao.id)
        assert status == 400
        assert "comentário" in res["error"]

        # 2. Data ausente
        dados = {"nota": 5, "comentario": "Bom", "album_id": album_padrao.id}
        res, status = AvaliacaoService.criar_avaliacao(dados, usuario_id=usuario_padrao.id)
        assert status == 400
        assert "data" in res["error"]

        # 3. Formato de data inválido
        dados = {"nota": 5, "comentario": "Bom", "data_escuta": "11/10/2026", "album_id": album_padrao.id}
        res, status = AvaliacaoService.criar_avaliacao(dados, usuario_id=usuario_padrao.id)
        assert status == 400
        assert "Formato de data inválido" in res["error"]

def test_criar_avaliacao_com_novo_album_e_artista_aninhado(app, usuario_padrao):
    """Cobre o bloco 'elif album_data:' criando artista, álbum e músicas juntos na avaliação"""
    with app.app_context():
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
                    {"titulo": "Musica Nova 1", "duracao": "03:00"}
                ]
            }
        }
        resultado, status = AvaliacaoService.criar_avaliacao(dados, usuario_id=usuario_padrao.id)
        assert status == 201
        assert resultado.nota == 5

def test_criar_avaliacao_duplicada(app, usuario_padrao, avaliacao_padrao, album_padrao):
    """Cobre o bloqueio quando já existe avaliação do usuário para o álbum"""
    with app.app_context():
        dados = {
            "nota": 3,
            "comentario": "Outra vez",
            "data_escuta": "2026-10-11",
            "album_id": album_padrao.id
        }
        resultado, status = AvaliacaoService.criar_avaliacao(dados, usuario_id=usuario_padrao.id)
        assert status == 400
        assert "Já existe avaliação" in resultado["error"]

def test_editar_avaliacao_com_album_e_musicas(app, usuario_padrao, avaliacao_padrao):
    """Cobre a edição de nota, comentário, data e atualização/criação/deleção de músicas do álbum"""
    with app.app_context():
        dados = {
            "nota": 4,
            "comentario": "Editado com sucesso",
            "data_escuta": "2026-10-12",
            "album": {
                "titulo": "Feel Special Editado",
                "ano": 2019,
                "musicas": [
                    {"titulo": "Feel Special Remasterizada", "duracao": "03:30"}
                ]
            }
        }
        resultado, status = AvaliacaoService.editar_avaliacao(avaliacao_padrao.id, dados, usuario_id=usuario_padrao.id)
        assert status == 200
        assert resultado.nota == 4
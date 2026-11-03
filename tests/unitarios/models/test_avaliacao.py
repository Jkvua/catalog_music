import pytest
from datetime import date
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models.avaliacao import Avaliacao
from app.models.album import Album
from app.models.artista import Artista
from app.models.usuario import Usuario

def test_instanciar_avaliacao():
    nota_esperada = 4.0
    comentario_esperado = "Ótimo álbum!"
    data_escuta_esperada = date(2026, 6, 1)
    album_id_esperado = 1
    usuario_id_esperado = 2

    avaliacao = Avaliacao(
        nota=nota_esperada,
        comentario=comentario_esperado,
        data_escuta=data_escuta_esperada,
        album_id=album_id_esperado,
        usuario_id=usuario_id_esperado
    )

    assert avaliacao.nota == nota_esperada
    assert avaliacao.comentario == comentario_esperado
    assert avaliacao.data_escuta == data_escuta_esperada
    assert avaliacao.album_id == album_id_esperado
    assert avaliacao.usuario_id == usuario_id_esperado
    assert avaliacao.id is None

def test_salvamento_correto_avaliacao(app): 
    usuario = Usuario(user="usuario teste", email="teste@teste.com", password="senha123")
    artista = Artista(nome="TWICW", genero="K-POP", pais="Coreia do Sul")

    db.session.add_all([usuario, artista])
    db.session.commit()

    album = Album(titulo="Twicetagram", ano=2017, artista_id=artista.id)
    db.session.add(album)
    db.session.commit()

    avaliacao = Avaliacao(
        nota=5.0,
        comentario="Extraordinário!",
        data_escuta=date(2026, 6, 1),
        album_id=album.id,
        usuario_id=usuario.id
    )

    db.session.add(avaliacao)
    db.session.commit()

    assert avaliacao.id is not None
    assert avaliacao.id > 0

def test_avaliacao_duplicada_falha(app):
    usuario = Usuario(user="fuscao", email="fuscao@fuscao.com", password="senha123")
    artista = Artista(nome="tyler the creator", genero="hip hop", pais="EUA")
    db.session.add_all([usuario, artista])
    db.session.commit()

    album = Album(titulo="IGOR", ano=2019, artista_id=artista.id)
    db.session.add(album)
    db.session.commit()

    avaliacao_original = Avaliacao(
        nota = 4.0,
        comentario = "Brilhante esse cara",
        album_id = album.id,
        usuario_id = usuario.id
    )

    db.session.add(avaliacao_original)
    db.session.commit()

    avaliacao_duplicada = Avaliacao(
        nota = 3.5,
        comentario = "Gostei, mas não tanto",
        album_id = album.id,
        usuario_id = usuario.id
    )

    db.session.add(avaliacao_duplicada)

    with pytest.raises(IntegrityError):
        db.session.commit()

def test_salvamento_incorreto_avaliacao(app):
    usuario = Usuario(user="usuario teste", email="invalido@invalido.com", password="senha123")
    artista = Artista(nome="BLACKPINK", genero="K-POP", pais="Coreia do Sul")
    db.session.add_all([usuario, artista])
    db.session.commit()

    album = Album(titulo="The Album", ano=2020, artista_id=artista.id)
    db.session.add(album)
    db.session.commit()

    avaliacao_invalida = Avaliacao(
        comentario="Um album bem mais ou menos",
        album_id=album.id,
        usuario_id=usuario.id
    )

    db.session.add(avaliacao_invalida)

    with pytest.raises(IntegrityError):
        db.session.commit()
import pytest
from datetime import date
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.album import Album
from app.models.artista import Artista
from app.models.avaliacao import Avaliacao
from app.models.usuario import Usuario


def test_salvamento_correto_avaliacao(app):
    usuario = Usuario(
        user="usuario teste",
        email="teste@teste.com",
        password="senha123"
    )

    db.session.add(usuario)
    db.session.commit()

    artista = Artista(
        nome="TWICW",
        genero="K-POP",
        pais="Coreia do Sul",
        usuario_id=usuario.id
    )

    db.session.add(artista)
    db.session.commit()

    album = Album(
        titulo="Twicetagram",
        ano=2017,
        artista_id=artista.id,
        usuario_id=usuario.id
    )

    db.session.add(album)
    db.session.commit()

    avaliacao = Avaliacao(
        nota=5,
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
    usuario = Usuario(
        user="fuscao",
        email="fuscao@fuscao.com",
        password="senha123"
    )

    db.session.add(usuario)
    db.session.commit()

    artista = Artista(
        nome="tyler the creator",
        genero="hip hop",
        pais="EUA",
        usuario_id=usuario.id
    )

    db.session.add(artista)
    db.session.commit()

    album = Album(
        titulo="IGOR",
        ano=2019,
        artista_id=artista.id,
        usuario_id=usuario.id
    )

    db.session.add(album)
    db.session.commit()

    avaliacao_original = Avaliacao(
        nota=4,
        comentario="Brilhante esse cara",
        album_id=album.id,
        usuario_id=usuario.id
    )

    db.session.add(avaliacao_original)
    db.session.commit()

    avaliacao_duplicada = Avaliacao(
        nota=3,
        comentario="Gostei, mas não tanto",
        album_id=album.id,
        usuario_id=usuario.id
    )

    db.session.add(avaliacao_duplicada)

    with pytest.raises(IntegrityError):
        db.session.commit()

    db.session.rollback()


def test_salvamento_incorreto_avaliacao(app):
    usuario = Usuario(
        user="usuario teste",
        email="invalido@invalido.com",
        password="senha123"
    )

    db.session.add(usuario)
    db.session.commit()

    artista = Artista(
        nome="BLACKPINK",
        genero="K-POP",
        pais="Coreia do Sul",
        usuario_id=usuario.id
    )

    db.session.add(artista)
    db.session.commit()

    album = Album(
        titulo="The Album",
        ano=2020,
        artista_id=artista.id,
        usuario_id=usuario.id
    )

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

    db.session.rollback()
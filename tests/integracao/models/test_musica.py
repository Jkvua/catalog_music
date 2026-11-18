import pytest
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models.usuario import Usuario
from app.models.musica import Musica
from app.models.album import Album
from app.models.artista import Artista


def test_salvamento_correto_musica(app):
    usuario = Usuario(
        user="usuario_teste_1",
        email="usuario1@teste.com",
        password="senha123"
    )
    db.session.add(usuario)
    db.session.commit()

    artista = Artista(nome="tyler the creator", usuario_id=usuario.id)
    db.session.add(artista)
    db.session.commit()

    album = Album(
        titulo="Chromakopia",
        ano=2024,
        artista_id=artista.id,
        usuario_id=usuario.id
    )
    db.session.add(album)
    db.session.commit()

    musica = Musica(
        titulo="Noid",
        duracao="04:44",
        album_id=album.id,
        usuario_id=usuario.id
    )
    db.session.add(musica)
    db.session.commit()

    assert musica.id is not None
    assert musica.id > 0


def test_exclusao_album_deletar_musicas(app):
    usuario = Usuario(
        user="usuario_teste_2",
        email="usuario2@teste.com",
        password="senha123"
    )
    db.session.add(usuario)
    db.session.commit()

    artista = Artista(nome="TWICE", usuario_id=usuario.id)
    db.session.add(artista)
    db.session.commit()

    album = Album(
        titulo="Formula of Love",
        ano=2021,
        artista_id=artista.id,
        usuario_id=usuario.id
    )
    db.session.add(album)
    db.session.commit()

    musica = Musica(
        titulo="SCIENTIST",
        duracao="03:14",
        album_id=album.id,
        usuario_id=usuario.id
    )
    db.session.add(musica)
    db.session.commit()

    musica_id = musica.id

    db.session.delete(album)
    db.session.commit()

    musica_banco = db.session.get(Musica, musica_id)
    assert musica_banco is None


def test_salvamento_incorreto_musica(app):
    usuario = Usuario(
        user="usuario_teste_3",
        email="usuario3@teste.com",
        password="senha123"
    )
    db.session.add(usuario)
    db.session.commit()

    artista = Artista(nome="Red Velvet", usuario_id=usuario.id)
    db.session.add(artista)
    db.session.commit()

    album = Album(
        titulo="The Red",
        ano=2015,
        artista_id=artista.id,
        usuario_id=usuario.id
    )
    db.session.add(album)
    db.session.commit()

    musica_invalida = Musica(
        duracao="03:23",
        album_id=album.id,
        usuario_id=usuario.id
    )
    db.session.add(musica_invalida)

    with pytest.raises(IntegrityError):
        db.session.commit()

    db.session.rollback()
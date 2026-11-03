import pytest
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.models.musica import Musica
from app.models.album import Album
from app.models.artista import Artista

def test_instanciar_musica():
    titulo_esperado = "Noid"
    duracao_esperada = "04:44"
    album_id_esperado = 1
    usuario_id_esperado = 2

    musica = Musica(
        titulo=titulo_esperado,
        duracao=duracao_esperada,
        album_id=album_id_esperado,
        usuario_id=usuario_id_esperado
    )

    assert musica.titulo == titulo_esperado
    assert musica.duracao == duracao_esperada
    assert musica.album_id == album_id_esperado
    assert musica.usuario_id == usuario_id_esperado
    assert musica.id is None

def test_salvamento_correto_musica(app):
    artista = Artista(nome="tyler the creator")
    db.session.add(artista)
    db.session.commit()

    album = Album(titulo="Chromakopia", ano=2024, artista_id=artista.id)
    db.session.add(album)
    db.session.commit()

    musica = Musica(titulo="Noid", duracao="04:44", album_id=album.id)
    db.session.add(musica)
    db.session.commit()

    assert musica.id is not None
    assert musica.id > 0

def test_exclusao_album_deletar_musicas(app):
    artista = Artista(nome="TWICE")
    db.session.add(artista)
    db.session.commit()

    album = Album(titulo="Formula of Love", ano=2021, artista_id=artista.id)
    db.session.add(album)
    db.session.commit()

    musica = Musica(titulo="SCIENTIST", duracao="03:14", album_id=album.id)
    db.session.add_all([musica])
    db.session.commit()

    musica_id = musica.id

    db.session.delete(album)
    db.session.commit()

    musica_banco = db.session.get(Musica, musica_id)
    assert musica_banco is None

def test_salvamento_incorreto_musica(app):
    artista = Artista(nome="Red Velvet")
    db.session.add(artista)
    db.session.commit()

    album = Album(titulo="The Red", ano=2015, artista_id=artista.id)
    db.session.add(album)
    db.session.commit()

    musica_invalida = Musica(duracao="03:23", album_id=album.id)
    db.session.add(musica_invalida)

    with pytest.raises(IntegrityError):
        db.session.commit()

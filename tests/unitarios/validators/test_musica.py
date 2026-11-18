import pytest
from app.validators.musica import MusicaValidator

@pytest.mark.parametrize("titulo, esperado", [
    ("Noid", True),
    ("SCIENTIST", True),
    ("A", True),
    ("A" * 150, True),
    ("  Noid  ", True),
    ("", False),
    ("   ", False),
    ("A" * 151, False),
    (None, False),
    (123, False),
    (True, False),
])
def test_validar_titulo(titulo, esperado):
    assert MusicaValidator.validar_titulo(titulo) is esperado


@pytest.mark.parametrize("duracao, esperado", [
    ("04:44", True),
    ("03:14", True),
    ("00:01", True),
    ("99:59", True),
    (" 04:44 ", True),
    ("00:00", False),
    ("03:60", False),
    ("03:75", False),
    ("3:45", False),
    ("100:00", False),
    ("03:5", False),
    ("abc", False),
    ("", False),
    ("   ", False),
    (None, False),
    (123, False),
    (True, False),
])
def test_validar_duracao(duracao, esperado):
    assert MusicaValidator.validar_duracao(duracao) is esperado


@pytest.mark.parametrize("album_id, esperado", [
    (1, True),
    (10, True),
    (999, True),
    (0, False),
    (-1, False),
    (None, False),
    ("1", False),
    (1.5, False),
    (True, False),
    (False, False),
])
def test_validar_album_id(album_id, esperado):
    assert MusicaValidator.validar_album_id(album_id) is esperado


@pytest.mark.parametrize("album_nome, esperado", [
    ("Chromakopia", True),
    ("Formula of Love", True),
    ("A", True),
    ("A" * 150, True),
    ("", False),
    ("   ", False),
    ("A" * 151, False),
    (None, False),
    (123, False),
    (True, False),
])
def test_validar_album_nome(album_nome, esperado):
    assert MusicaValidator.validar_album_nome(album_nome) is esperado
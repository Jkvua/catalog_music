import re

from app.validators.album import AlbumValidator


class MusicaValidator:

    @staticmethod
    def validar_titulo(titulo):
        return (
            isinstance(titulo, str)
            and 1 <= len(titulo.strip()) <= 150
        )

    @staticmethod
    def validar_duracao(duracao):
        if not isinstance(duracao, str):
            return False

        duracao = duracao.strip()

        if not re.fullmatch(r"[0-9]{2}:[0-5][0-9]", duracao):
            return False

        minutos, segundos = map(int, duracao.split(":"))

        return minutos > 0 or segundos > 0

    @staticmethod
    def validar_album_id(album_id):
        return (
            type(album_id) is int
            and album_id > 0
        )

    @staticmethod
    def validar_album_nome(album_nome):
        return AlbumValidator.validar_titulo(album_nome)
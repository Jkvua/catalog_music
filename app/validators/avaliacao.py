import re
from datetime import datetime


class AvaliacaoValidator:

    @staticmethod
    def validar_nota(nota):
        return type(nota) is int and 1 <= nota <= 5

    @staticmethod
    def validar_comentario(comentario):
        return (
            isinstance(comentario, str)
            and 1 <= len(comentario.strip()) <= 500
        )

    @staticmethod
    def validar_data_escuta(data):
        if not isinstance(data, str):
            return False

        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", data):
            return False

        try:
            datetime.strptime(data, "%Y-%m-%d")
            return True
        except ValueError:
            return False

    @staticmethod
    def validar_album_id(album_id):
        return (
            type(album_id) is int
            and album_id > 0
        )
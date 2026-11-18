class AlbumValidator:

    @staticmethod
    def validar_titulo(titulo):
        return (
            isinstance(titulo, str)
            and 1 <= len(titulo.strip()) <= 150
        )

    @staticmethod
    def validar_ano(ano):
        if type(ano) is int:
            return 1900 <= ano <= 2100

        if isinstance(ano, str):
            ano = ano.strip()

            if not ano.isdecimal():
                return False

            return 1900 <= int(ano) <= 2100

        return False

    @staticmethod
    def validar_artista_id(artista_id):
        return (
            type(artista_id) is int
            and artista_id > 0
        )
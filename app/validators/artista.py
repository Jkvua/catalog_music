class ArtistaValidator:

    @staticmethod
    def validar_nome(nome):
        return (
            isinstance(nome, str)
            and 1 <= len(nome.strip()) <= 100
        )

    @staticmethod
    def validar_genero(genero):
        return (
            isinstance(genero, str)
            and 1 <= len(genero.strip()) <= 50
        )

    @staticmethod
    def validar_pais(pais):
        return (
            isinstance(pais, str)
            and 1 <= len(pais.strip()) <= 50
        )
from app.models.album import Album
from app.models.artista import Artista
from app.validators.album import AlbumValidator
from app.validators.artista import ArtistaValidator
from app.extensions import db
from sqlalchemy.exc import IntegrityError


class AlbumService:
    @staticmethod
    def criar_album(dados, usuario_id, commit=True):
        if not isinstance(dados, dict):
            return {
                "error": "Os dados do álbum devem ser enviados em um objeto JSON válido"}, 400

        titulo = dados.get('titulo')
        artista_id = dados.get('artista_id')
        artista_nome = dados.get('artista')
        ano = dados.get('ano')

        if not AlbumValidator.validar_titulo(titulo):
            return {
                "error": "O título do álbum é obrigatório e deve conter entre 1 e 150 caracteres"}, 400

        if ano is None or ano == "":
            return {
                "error": "O ano de lançamento do álbum é obrigatório"}, 400

        if not AlbumValidator.validar_ano(ano):
            return {
                "error": "O ano de lançamento deve ser um número inteiro entre 1900 e 2100"}, 400

        titulo = titulo.strip()
        ano = int(ano)

        if artista_id is not None:
            if not AlbumValidator.validar_artista_id(artista_id):
                return {
                    "error": "O ID do artista deve ser um número inteiro positivo"}, 400

            artista = Artista.query.filter_by(id=artista_id, usuario_id=usuario_id).first()

            if not artista:
                return {
                    "error": f"Artista com id {artista_id} não encontrado no seu catálogo"}, 404
        elif artista_nome is not None:
            if not ArtistaValidator.validar_nome(artista_nome):
                return {
                    "error": "O nome do artista deve conter entre 1 e 100 caracteres"}, 400

            artista_nome = artista_nome.strip()
            artista = Artista.query.filter_by(nome=artista_nome, usuario_id=usuario_id).first()

            if not artista:
                return {
                    "error": f"Artista '{artista_nome}' não encontrado no seu catálogo"}, 404
        else:
            return {
                "error": "É necessário informar o nome ou o ID do artista"}, 400

        existente = Album.query.filter_by(titulo=titulo, artista_id=artista.id, usuario_id=usuario_id).first()

        if existente:
            return {"error": f"O álbum '{titulo}' já existe para esse artista"}, 400

        novo_album = Album(usuario_id=usuario_id, titulo=titulo, artista_id=artista.id, ano=ano)

        try:
            db.session.add(novo_album)
            if commit:
                db.session.commit()
            else:
                db.session.flush()
        except IntegrityError:
            db.session.rollback()
            return {
                "error": "Não foi possível cadastrar o álbum devido a um conflito de integridade dos dados"}, 409

        return novo_album, 201

    @staticmethod
    def editar_album(id, dados, usuario_id, commit=True):
        album = db.get_or_404(Album, id)
        if album.usuario_id != usuario_id:
            return {
                "error": "Você não tem permissão para editar este álbum"}, 403
        if not isinstance(dados, dict):
            return {
                "error": "Os dados do álbum devem ser enviados em um objeto JSON válido"}, 400
        if (
            'artista_id' in dados
            or 'artista_nome' in dados
            or 'artista' in dados):

            return {
                "error": "Não é permitido alterar o artista de um álbum já existente"}, 400

        if 'titulo' in dados:
            novo_titulo = dados['titulo']
            if not AlbumValidator.validar_titulo(novo_titulo):
                return {
                    "error": "O título do álbum deve conter entre 1 e 150 caracteres"}, 400
            novo_titulo = novo_titulo.strip()

            if novo_titulo != album.titulo:
                existente = Album.query.filter_by(titulo=novo_titulo, artista_id=album.artista_id, usuario_id=usuario_id).first()

                if existente and existente.id != album.id:
                    return {
                        "error": f"O álbum '{novo_titulo}' já existe para esse artista"}, 400

                album.titulo = novo_titulo

        if 'ano' in dados:
            ano = dados['ano']
            if ano is None or ano == "":
                return {
                    "error": "O ano de lançamento do álbum é obrigatório"}, 400
            if not AlbumValidator.validar_ano(ano):
                return {
                    "error": "O ano de lançamento deve ser um número inteiro entre 1900 e 2100"}, 400
            album.ano = int(ano)

        try:
            if commit:
                db.session.commit()
            else:
                db.session.flush()
        except IntegrityError:
            db.session.rollback()
            return {
                "error": "Não foi possível atualizar o álbum devido a um conflito de integridade dos dados"}, 409

        return album, 200

    @staticmethod
    def deletar_album(id, usuario_id):
        album = db.get_or_404(Album, id)
        if album.usuario_id != usuario_id:
            return {
                "error": "Você não tem permissão para deletar este álbum"}, 403

        titulo_album = album.titulo

        try:
            db.session.delete(album)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {
                "error": "Não foi possível excluir o álbum devido a uma restrição de integridade dos dados"}, 409

        return {
            "message": f"Álbum '{titulo_album}' deletado com sucesso"}, 200
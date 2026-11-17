from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.musica import Musica
from app.models.album import Album
from app.validators.musica import MusicaValidator


class MusicaService:

    @staticmethod
    def criar_musica(dados, usuario_id, commit=True):

        if not isinstance(dados, dict):
            return {
                "error": "Os dados da música devem ser enviados em um objeto JSON válido"
            }, 400

        titulo = dados.get("titulo")
        duracao = dados.get("duracao")
        album_id = dados.get("album_id")
        album_nome = dados.get("album")

        if not MusicaValidator.validar_titulo(titulo):
            return {
                "error": "O título da música é obrigatório e deve conter entre 1 e 150 caracteres"
            }, 400

        if not MusicaValidator.validar_duracao(duracao):
            return {
                "error": "A duração da música é obrigatória e deve estar no formato MM:SS"
            }, 400

        titulo = titulo.strip()
        duracao = duracao.strip()

        if album_id is not None:

            if not MusicaValidator.validar_album_id(album_id):
                return {
                    "error": "O ID do álbum deve ser um número inteiro positivo"
                }, 400

            album = Album.query.filter_by(
                id=album_id,
                usuario_id=usuario_id
            ).first()

            if not album:
                return {
                    "error": f"Álbum com ID {album_id} não encontrado no seu catálogo"
                }, 404

        elif album_nome is not None:

            if not MusicaValidator.validar_album_nome(album_nome):
                return {
                    "error": "O nome do álbum deve conter entre 1 e 150 caracteres"
                }, 400

            album_nome = album_nome.strip()

            album = Album.query.filter_by(
                titulo=album_nome,
                usuario_id=usuario_id
            ).first()

            if not album:
                return {
                    "error": f"Álbum '{album_nome}' não encontrado no seu catálogo"
                }, 404

        else:
            return {
                "error": "É necessário informar o nome ou o ID do álbum"
            }, 400

        existente = Musica.query.filter_by(
            titulo=titulo,
            album_id=album.id
        ).first()

        if existente:
            return {
                "error": f"A música '{titulo}' já existe neste álbum"
            }, 400

        nova_musica = Musica(
            usuario_id=usuario_id,
            titulo=titulo,
            duracao=duracao,
            album_id=album.id
        )

        try:
            db.session.add(nova_musica)
            if commit:
                db.session.commit()
            else:
                db.session.flush()

        except IntegrityError:
            db.session.rollback()
            return {
                "error": "Não foi possível cadastrar a música devido a um conflito de integridade dos dados"
            }, 409

        return nova_musica, 201

    @staticmethod
    def editar_musica(id, dados, usuario_id, commit=True):

        musica = db.get_or_404(Musica, id)

        if musica.usuario_id != usuario_id:
            return {
                "error": "Você não tem permissão para editar esta música"
            }, 403

        if not isinstance(dados, dict):
            return {
                "error": "Os dados da música devem ser enviados em um objeto JSON válido"
            }, 400

        if "album_id" in dados or "album" in dados:
            return {
                "error": "Não é permitido alterar o álbum de uma música já existente"
            }, 400

        if "titulo" in dados:

            novo_titulo = dados["titulo"]

            if not MusicaValidator.validar_titulo(novo_titulo):
                return {
                    "error": "O título da música deve conter entre 1 e 150 caracteres"
                }, 400

            novo_titulo = novo_titulo.strip()

            if novo_titulo != musica.titulo:

                existente = Musica.query.filter_by(
                    titulo=novo_titulo,
                    album_id=musica.album_id
                ).first()

                if existente and existente.id != musica.id:
                    return {
                        "error": f"A música '{novo_titulo}' já existe neste álbum"
                    }, 400

                musica.titulo = novo_titulo

        if "duracao" in dados:

            nova_duracao = dados["duracao"]

            if not MusicaValidator.validar_duracao(nova_duracao):
                return {
                    "error": "A duração da música deve estar no formato MM:SS"
                }, 400

            musica.duracao = nova_duracao.strip()

        try:
            if commit:
                db.session.commit()
            else:
                db.session.flush()
        except IntegrityError:
            db.session.rollback()
            return {
                "error": "Não foi possível atualizar a música devido a um conflito de integridade dos dados"
            }, 409

        return musica, 200

    @staticmethod
    def deletar_musica(id, usuario_id, commit=True):

        musica = db.get_or_404(Musica, id)

        if musica.usuario_id != usuario_id:
            return {
                "error": "Você não tem permissão para deletar esta música"
            }, 403

        titulo_musica = musica.titulo

        try:
            db.session.delete(musica)
            if commit:
                db.session.commit()
            else:
                db.session.flush()

        except IntegrityError:
            db.session.rollback()
            return {
                "error": "Não foi possível excluir a música devido a uma restrição de integridade dos dados"
            }, 409

        return {
            "message": f"Música {titulo_musica} foi deletada com sucesso"
        }, 200
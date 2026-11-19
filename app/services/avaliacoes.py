from datetime import datetime

from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models.album import Album
from app.models.artista import Artista
from app.models.avaliacao import Avaliacao
from app.models.usuario import Usuario
from app.services.album import AlbumService
from app.services.artista import ArtistaService
from app.services.musica import MusicaService
from app.validators.avaliacao import AvaliacaoValidator


class FalhaOperacao(Exception):
    def __init__(self, resultado, status):
        self.resultado = resultado
        self.status = status


class AvaliacaoService:
    @staticmethod
    def _executar(operacao, *args):
        resultado, status = operacao(*args, commit=False)
        if status not in (200, 201):
            raise FalhaOperacao(resultado, status)
        return resultado

    @staticmethod
    def _validar(dados, criacao=False):
        if not isinstance(dados, dict):
            return {"error": "Os dados devem ser um objeto JSON"}, 400
        regras = {
            "nota": (AvaliacaoValidator.validar_nota, "A nota deve ser um número inteiro entre 1 e 5"),
            "comentario": (AvaliacaoValidator.validar_comentario, "O comentário deve ter entre 1 e 500 caracteres"),
            "data_escuta": (AvaliacaoValidator.validar_data_escuta, "Formato de data inválido, use YYYY-MM-DD"),
        }
        for campo, (validar, mensagem) in regras.items():
            if (criacao or campo in dados) and not validar(dados.get(campo)):
                return {"error": mensagem}, 400
        return None

    @staticmethod
    def _atualizar(avaliacao, dados):
        if "nota" in dados:
            avaliacao.nota = dados["nota"]
        if "comentario" in dados:
            avaliacao.comentario = dados["comentario"].strip()
        if "data_escuta" in dados:
            avaliacao.data_escuta = datetime.strptime(
                dados["data_escuta"], "%Y-%m-%d"
            ).date()

    @staticmethod
    def _transacao(operacao):
        try:
            resultado = operacao()
            db.session.commit()
            return resultado
        except FalhaOperacao as erro:
            db.session.rollback()
            return erro.resultado, erro.status
        except IntegrityError:
            db.session.rollback()
            return {"error": "Conflito de integridade dos dados"}, 409
        except Exception:
            db.session.rollback()
            raise

    @staticmethod
    def _obter_album(dados, usuario_id):
        if "album_id" in dados:
            album_id = dados["album_id"]
            if not AvaliacaoValidator.validar_album_id(album_id):
                raise FalhaOperacao({"error": "ID do álbum inválido"}, 400)
            album = Album.query.filter_by(id=album_id, usuario_id=usuario_id).first()
            if album is None:
                raise FalhaOperacao({"error": "Álbum não encontrado"}, 404)
            return album
        album_data = dados.get("album")
        if not isinstance(album_data, dict):
            raise FalhaOperacao({"error": "É necessário informar o álbum"}, 400)
        artista_data = album_data.get("artista")
        if not isinstance(artista_data, dict):
            raise FalhaOperacao({"error": "O álbum precisa possuir um artista"}, 400)
        nome = artista_data.get("nome")
        artista = None
        if isinstance(nome, str) and nome.strip():
            artista = Artista.query.filter_by(
                nome=nome.strip(), usuario_id=usuario_id
            ).first()
        if artista is None:
            artista = AvaliacaoService._executar(
                ArtistaService.criar_artista,
                {"nome": nome, "genero": artista_data.get("genero", "Não informado"),
                 "pais": artista_data.get("pais", "Não informado")},
                usuario_id,
            )
        album = AvaliacaoService._executar(
            AlbumService.criar_album,
            {"titulo": album_data.get("titulo"), "ano": album_data.get("ano"),
             "artista_id": artista.id},
            usuario_id,
        )
        musicas = album_data.get("musicas", [])
        if not isinstance(musicas, list) or any(
            not isinstance(m, dict) for m in musicas
        ):
            raise FalhaOperacao({"error": "Músicas deve ser uma lista de objetos"}, 400)
        for musica in musicas:
            AvaliacaoService._executar(
                MusicaService.criar_musica,
                {**musica, "album_id": album.id}, usuario_id,
            )
        return album

    @staticmethod
    def criar_avaliacao(dados, usuario_id):
        erro = AvaliacaoService._validar(dados, criacao=True)
        if erro:
            return erro
        if db.session.get(Usuario, usuario_id) is None:
            return {"error": "Usuário não encontrado"}, 404
        def criar():
            album = AvaliacaoService._obter_album(dados, usuario_id)
            existente = Avaliacao.query.filter_by(
                usuario_id=usuario_id, album_id=album.id
            ).first()
            if existente:
                raise FalhaOperacao({"error": "Já existe avaliação para esse álbum"}, 400)
            avaliacao = Avaliacao(usuario_id=usuario_id, album_id=album.id)
            AvaliacaoService._atualizar(avaliacao, dados)
            db.session.add(avaliacao)
            return avaliacao, 201
        return AvaliacaoService._transacao(criar)

    @staticmethod
    def _editar_musicas(album, musicas, usuario_id):
        if not isinstance(musicas, list) or any(
            not isinstance(m, dict) for m in musicas
        ):
            raise FalhaOperacao({"error": "Músicas deve ser uma lista de objetos"}, 400)
        ids = [m["id"] for m in musicas if m.get("id") is not None]
        if any(type(i) is not int or i <= 0 for i in ids) or len(ids) != len(set(ids)):
            raise FalhaOperacao({"error": "IDs de músicas inválidos ou repetidos"}, 400)
        atuais = {musica.id: musica for musica in album.musicas}
        if any(
            i not in atuais or atuais[i].usuario_id != usuario_id for i in ids
        ):
            raise FalhaOperacao({"error": "Música não pertence a este álbum"}, 403)
        for musica_id in set(atuais) - set(ids):
            AvaliacaoService._executar(
                MusicaService.deletar_musica, musica_id, usuario_id
            )
        for musica in musicas:
            if musica.get("id") is not None:
                campos = {
                    k: musica[k] for k in ("titulo", "duracao") if k in musica
                }
                AvaliacaoService._executar(
                    MusicaService.editar_musica, musica["id"], campos, usuario_id
                )
            else:
                AvaliacaoService._executar(
                    MusicaService.criar_musica,
                    {**musica, "album_id": album.id}, usuario_id,
                )

    @staticmethod
    def editar_avaliacao(id, dados, usuario_id):
        avaliacao = db.get_or_404(Avaliacao, id)
        if avaliacao.usuario_id != usuario_id:
            return {"error": "Você não tem permissão para editar esta avaliação"}, 403
        erro = AvaliacaoService._validar(dados)
        if erro:
            return erro
        if "album_id" in dados:
            return {"error": "Não é permitido trocar o álbum"}, 400

        def editar():
            if "album" in dados:
                album_data = dados["album"]
                if not isinstance(album_data, dict):
                    raise FalhaOperacao({"error": "Álbum deve ser um objeto"}, 400)
                if any(k in album_data for k in ("artista", "artista_id", "artista_nome")):
                    raise FalhaOperacao({"error": "Não é permitido trocar o artista"}, 400)
                album = avaliacao.album
                if album.usuario_id != usuario_id:
                    raise FalhaOperacao({"error": "Álbum não pertence ao usuário"}, 403)
                campos = {
                    k: album_data[k] for k in ("titulo", "ano") if k in album_data
                }
                if campos:
                    AvaliacaoService._executar(
                        AlbumService.editar_album, album.id, campos, usuario_id
                    )

                    db.session.commit()

                if "musicas" in album_data:
                    AvaliacaoService._editar_musicas(
                        album, album_data["musicas"], usuario_id
                    )
                    
            AvaliacaoService._atualizar(avaliacao, dados)
            return avaliacao, 200

        return AvaliacaoService._transacao(editar)

    @staticmethod
    def delete_avaliacao(id, usuario_id):
        avaliacao = db.get_or_404(Avaliacao, id)
        if avaliacao.usuario_id != usuario_id:
            return {"error": "Você não tem permissão para excluir esta avaliação"}, 403

        def excluir():
            resultado = {"id": avaliacao.id, "album": avaliacao.album.titulo}
            db.session.delete(avaliacao)
            return resultado, 200

        return AvaliacaoService._transacao(excluir)
from app.models.avaliacao import Avaliacao
from app.models.album import Album
from app.models.usuario import Usuario
from app.models.artista import Artista
from app.services.album import AlbumService
from app.services.artista import ArtistaService
from app.services.musica import MusicaService
from app.extensions import db
from datetime import datetime
from flask_jwt_extended import get_jwt_identity


class AvaliacaoService:
    @staticmethod
    def criar_avaliacao(dados):
        usuario_id = int(get_jwt_identity())
        nota = dados.get('nota')
        comentario = dados.get('comentario')
        data_escuta_str = dados.get('data_escuta')
        album_id = dados.get('album_id')
        album_data = dados.get('album')
       
        print("\n========== NOVA AVALIAÇÃO ==========")
        print("Dados recebidos:")
        print(dados)
        
        if nota is None or nota < 1 or nota > 5:
            return {"error": f"A nota da avaliação é obrigatória e deve ser um número entre 1 e 5"}, 400
        
        if not comentario:
            return {"error": f"O comentário da avaliação é obrigatório"}, 400

        data_escuta = None
        if data_escuta_str:
            try:
                data_escuta = datetime.strptime(data_escuta_str, "%Y-%m-%d").date()
            except ValueError:
                return {"error": "Formato de data inválido, use YYYY-MM-DD"}, 400
        else:
            return {"error": f"A data em que o álbum foi escutado é obrigatória"}, 400

        album = None

        if album_id:
            print(f"Artista recebido: {artista_nome}")
            album = Album.query.get(album_id)
            if not album:
                return {
                    "error": "Álbum não encontrado"
                }, 404
        elif album_data:
            artista_data = album_data.get("artista")
            
            if not artista_data:
                return {
                    "error": "O álbum precisa possuir um artista"
                }, 400
            
            artista_nome = artista_data.get("nome")
            
            artista = Artista.query.filter_by(
                    nome=artista_nome.strip()
            ).first()

            if not artista:
                artista, status = ArtistaService.criar_artista({
                    "nome": artista_nome,
                    "genero": artista_data.get("genero", "Não informado"),
                    "pais": artista_data.get("pais", "Não informado")
                })
                print("Status criação artista:", status)
                if status != 201:
                    return artista, status

            print("Artista não existe. Criando...")
            print("Criando álbum...")
            print(album_data)
            album, status = AlbumService.criar_album({

                "titulo": album_data.get("titulo"),
                "ano": album_data.get("ano"),
                "artista_id": artista.id

            })
            if status != 201:
                return album, status


            for musica in album_data.get("musicas", []):
                musica["album_id"] = album.id
                musica["artista_id"] = artista.id

                print("Criando música:")
                print(musica)

                resultado, status = MusicaService.criar_musica(musica)

                print("Status música:", status)

                if status != 201:
                    return resultado, status

        else:
            return {
                "error": "É necessário informar o álbum"
            },400
        
        usuario = None
        if usuario_id:
            usuario = Usuario.query.get(usuario_id)
            if not usuario:
                return {"error": f"O usuário {usuario_id} não foi encontrado"}, 404
        print("Verificando avaliação existente...")
        existente = Avaliacao.query.filter_by(usuario_id=usuario.id, album_id=album.id).first()
        if existente:
            return {"error": f"Já existe avaliação para esse álbum"}, 400
        
        print("Criando avaliação...")
        nova_avaliacao = Avaliacao(
            usuario_id=usuario.id,
            nota=nota, 
            comentario=comentario.strip(), 
            data_escuta=data_escuta,
            album_id=album.id
            
            )
        
        db.session.add(nova_avaliacao)
        db.session.commit()

        print("Avaliação criada com sucesso!")
        print("===============================\n")

        return nova_avaliacao, 201
    
    @staticmethod
    def editar_avaliacao(id, dados):
        usuario_id = int(get_jwt_identity())
        avaliacao = Avaliacao.query.get_or_404(id)

        if avaliacao.usuario_id != usuario_id:
            return {"error": "Você não tem permissão para editar esta avaliação"}, 403

        # ------------------------
        # Avaliação
        # ------------------------

        if "nota" in dados:
            nota = int(dados["nota"])

            if nota < 1 or nota > 5:
                return {"error": "A nota da avaliação deve ser entre 1 e 5"}, 400

            avaliacao.nota = nota

        if "comentario" in dados:
            comentario = dados["comentario"]

            if not comentario:
                return {"error": "O comentário é obrigatório"}, 400

            avaliacao.comentario = comentario.strip()

        if "data_escuta" in dados:
            try:
                avaliacao.data_escuta = datetime.strptime(
                    dados["data_escuta"],
                    "%Y-%m-%d"
                ).date()

            except ValueError:
                return {"error": "Formato de data inválido"}, 400

        # ------------------------
        # Álbum
        # ------------------------

        if "album" in dados:

            album = avaliacao.album
            album_data = dados["album"]

            if album_data.get("titulo") != album.titulo:
                album.titulo = album_data["titulo"].strip()

            if album_data.get("ano") != album.ano:
                album.ano = album_data["ano"]

            # ------------------------
            # Músicas
            # ------------------------

            if "musicas" in album_data:

                musica_data = album_data["musicas"]

                ids_enviados = [
                    m["id"]
                    for m in musica_data
                    if m.get("id", 0) > 0
                ]

                for musica in album.musicas:
                    if musica.id not in ids_enviados:
                        MusicaService.deletar_musica(musica.id)

                print("Músicas recebidas para edição:")
                for m in musica_data:
                    print(m)
                    if m.get("id", 0) > 0:

                        musica, status = MusicaService.editar_musica(
                            m["id"],
                            m
                        )

                        if status != 200:
                            return musica, status

                    else:

                        m["album_id"] = album.id
                        m["artista_id"] = album.artista_id

                        musica, status = MusicaService.criar_musica(m)

                        if status != 201:
                            return musica, status

        db.session.commit()

        return avaliacao, 200
    
    @staticmethod
    def delete_avaliacao(id):
        usuario_id = int(get_jwt_identity())
        avaliacao = Avaliacao.query.get_or_404(id)

        if avaliacao.usuario_id != usuario_id:
            return {"error": "Você não tem permissão para deletar esta avaliação"}, 403
    
        titulo_album = avaliacao.album.titulo
        id_avaliacao = avaliacao.id

        db.session.delete(avaliacao)
        db.session.commit()

        return {
            "id": id_avaliacao,
            "album": titulo_album
        }, 200
        
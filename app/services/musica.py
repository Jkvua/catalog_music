from app.models.musica import Musica
from app.models.album import Album
from app.models.artista import Artista
from app.extensions import db

class MusicaService:
    @staticmethod
    def criar_musica(dados):
        titulo = dados.get('titulo')
        duracao = dados.get('duracao')
        album_id = dados.get('album_id')
        artista_id = dados.get('artista_id')

        if not titulo or len(titulo.strip()) < 1:
            return {"error": "O título da música é obrigatório e deve conter pelo menos 1 caractere"}, 400
        if not duracao:
            return {"error": "A duração da música é obrigatória (formato MM:SS)"}, 400
        if not album_id:
            return {"error": "É obrigatório informar o álbum"}, 400

        try:
            minutos, segundos = duracao.split(':')
            minutos = int(minutos)
            segundos = int(segundos)

            if minutos < 0 or segundos < 0 or segundos >= 60:
                return {"error": "Formato de duração da música inválido, use MM:SS"}, 400
        except (ValueError, AttributeError):
            return {"error": "A duração da música está em um formato inválido, use MM:SS"}, 400
        
        album = Album.query.get(album_id)   
        if not album:
            return {"error": f"Álbum com ID {album_id} não encontrado"}, 404

        artista = Artista.query.get(artista_id)
        if not artista:
            return {"error": f"Artista com ID {artista_id} não encontrado"}, 404
        if not artista_id:
            return {"error": "É obrigatório informar o artista"}, 400

        nova_musica = Musica(
            titulo=titulo.strip(),
            duracao=duracao,
            album_id=album_id,
            artista_id=artista_id
        )

        db.session.add(nova_musica)
        db.session.commit()

        return nova_musica, 201
    
    @staticmethod
    def editar_musica(id, dados):
        musica = Musica.query.get_or_404(id)

        novo_titulo = dados.get('titulo')
        if novo_titulo and len(novo_titulo.strip()) < 1:
            return {"error": "O título da música deve conter pelo menos 1 caractere"}, 400
        
        if novo_titulo and novo_titulo != musica.titulo:
            existente = Musica.query.filter_by(titulo=novo_titulo, artista_id=musica.artista_id, album_id=musica.album_id).first()
            if existente and existente.id != id:
                return {"error": f"A Música {novo_titulo} já existe para esse artista neste álbum"}, 400
            musica.titulo = novo_titulo
        
        if 'duracao' in dados:
            nova_duracao = dados['duracao']
            try:
                minutos, segundos = nova_duracao.split(':')
                minutos = int(minutos)
                segundos = int(segundos)

                if minutos < 0 or segundos < 0 or segundos >= 60:
                    return {"error": "Formato de duração da música inválido, use MM:SS"}, 400
                musica.duracao = nova_duracao.strip()
            except (ValueError, AttributeError):
                return {"error": "A duração da música está em um formato inválido, use MM:SS"}, 400
        
        if 'album_id' in dados:
            return {"error": "Não é permitido alterar o álbum de uma música já existente"}, 400

        if 'artista_id' in dados:
            return {"error": "Não é permitido alterar o artista de uma música já existente"}, 400

        db.session.commit()
        return musica, 200

    @staticmethod
    def deletar_musica(id):
        musica = Musica.query.get_or_404(id)
        db.session.delete(musica)
        db.session.commit()
        return {"message": f"Música {musica.titulo} foi deletada com sucesso"}, 200
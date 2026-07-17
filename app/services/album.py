from app.models.album import Album
from app.models.artista import Artista
from app.extensions import db
from flask_jwt_extended import get_jwt_identity

class AlbumService:
    @staticmethod
    def criar_album(dados):
        usuario_id = int(get_jwt_identity())
        titulo = dados.get('titulo')
        artista_id = dados.get('artista_id')
        ano = dados.get('ano')
        artista_nome = dados.get('artista')
        
        if not titulo or len(titulo.strip()) < 1:
            return {"error": "O nome do álbum é obrigatório e deve conter pelo menos 1 caractere"}, 400
        if not ano:
            return {"error": "O ano de lançamento do álbum é obrigatório"}, 400
        
        try:
            ano = int(ano)
            if ano < 1900 or ano > 2100:
                return {"error": "O ano de lançamento deve ser entre 1900 e 2100"}, 400
        except (ValueError, AttributeError):
            return {"error": "O ano de lançamento deve ser um número inteiro"}, 400
        
        artista = None
        if artista_id:
            artista = Artista.query.get(artista_id)
            if not artista:
                return {"Error": f"Artista com id {artista_id} não encontrado"}, 404
        elif artista_nome:
            artista = Artista.query.filter_by(nome=artista_nome.strip()).first()
            if not artista:
                return {"error": f"Artista '{artista_nome}' não encontrado"}, 404
        else:
            return {"Error": f"É necessario informar o nome do artista ou o ID do artista"}, 400
                
        existente = Album.query.filter_by(titulo=titulo, artista_id=artista.id).first()
        if existente:
            return {"error": f"O Álbum {titulo} já existe para esse artista"}, 400
        
        novo_album = Album(
            usuario_id=usuario_id,
            titulo=titulo.strip(),
            artista_id=artista.id,
            ano=ano
        )

        db.session.add(novo_album)
        db.session.commit()
        db.session.refresh(novo_album)

        return novo_album, 201
    
    @staticmethod
    def editar_album(id, dados):
        usuario_id = int(get_jwt_identity())
        album = Album.query.get_or_404(id)

        if int(album.usuario_id) != usuario_id:
            return {"error": "Você não tem permissão para editar este álbum"}, 403

        novo_titulo = dados.get('titulo')
        if novo_titulo and len(novo_titulo.strip()) < 1:
            return {"error": "O titulo do álbum deve conter pelo menos 1 caractere"}, 400
        
        if novo_titulo and novo_titulo != album.titulo:
            existente = Album.query.filter_by(titulo=novo_titulo, artista_id=album.artista_id).first()
            if existente and existente.id != id:
                return {"error": f"O Álbum {novo_titulo} já existe para esse artista"}, 400
            album.titulo = novo_titulo
        
        if 'artista_id' in dados or 'artista_nome' in dados:
            return {"error": "Não é permitido alterar o artista de um álbum já existente"}, 400
        
        if 'ano' in dados and not dados['ano']:
            return {"error": "O ano de lançamento do álbum é obrigatório"}, 400
        if 'ano' in dados:
            try:
                ano = int(dados['ano'])
                if ano < 1900 or ano > 2100:
                    return {"Error": f"O ano de lançamento deve ser entre 1900 e 2100"}, 400
                album.ano = ano
            except ValueError:
                return {"Error": f"O ano de lançamento deve ser um número inteiro"}, 400

        db.session.commit()
        
        return album, 200
    
    @staticmethod
    def deletar_album(id):
        usuario_id = int(get_jwt_identity())
        album = Album.query.get_or_404(id)

        if int(album.usuario_id) != usuario_id:
            return {"error": "Você não tem permissão para deletar este álbum"}, 403

        db.session.delete(album)
        db.session.commit()
        return {"message": f"Álbum {album.titulo} deletado com sucesso"}, 200
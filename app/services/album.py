from app.models.album import Album
from app.models.artista import Artista
from app.extensions import db

class AlbumService:
    @staticmethod
    def criar_album(dados):
        titulo = dados.get('nome')
        artista_id = dados.get('artista_id')
        ano_lancamento = dados.get('ano_lancamento')
        
        if not titulo or len(titulo.strip()) < 1:
            return {"error": "O nome do álbum é obrigatório e deve conter pelo menos 1 caractere"}, 400
        if not artista_id:
            return {"error": "É obrigatório informar o artista"}, 400
        
        artista = Artista.query.get(artista_id)
        if not artista:
            return {"error": f"Artista com ID {artista_id} não encontrado"}, 404
       
        if not ano_lancamento:
            return {"error": "O ano de lançamento do álbum é obrigatório"}, 400

        try:
            ano_lancamento = int(ano_lancamento)
            if ano_lancamento < 1900 or ano_lancamento > 2100:
                return {"error": "O ano de lançamento deve ser entre 1900 e 2100"}, 400
        except (ValueError, TypeError):
            return {"error": "O ano de lançamento deve ser um número inteiro"}, 400
        
        existente = Album.query.filter_by(titulo=titulo, artista_id=artista_id).first()
        if existente:
            return {"error": f"O Álbum {titulo} já existe para esse artista"}, 400
        
        novo_album = Album(
            titulo=titulo.strip(),
            artista_id=artista_id.strip(),
            ano_lancamento=ano_lancamento.strip()
        )

        db.session.add(novo_album)
        db.session.commit()

        return novo_album, 201
    
    @staticmethod
    def editar_album(id, dados):
        album = Album.query.get_or_404(id)

        novo_nome = dados.get('nome')
        if novo_nome and len(novo_nome.strip()) < 1:
            return {"error": "O nome do álbum deve conter pelo menos 1 caractere"}, 400
        
        if novo_nome and novo_nome != album.nome:
            existente = Album.query.filter_by(nome=novo_nome, artista_id=album.artista_id).first()
            if existente and existente.id != id:
                return {"error": f"O Álbum {novo_nome} já existe para esse artista"}, 400
            album.nome = novo_nome
        
        if 'artista_id' in dados:
            return {"error": "Não é permitido alterar o artista de um álbum já existente"}, 400
        
        if 'ano_lancamento' in dados and not dados['ano_lancamento']:
            return {"error": "O ano de lançamento do álbum é obrigatório"}, 400
        album.ano_lancamento = dados.get('ano_lancamento', album.ano_lancamento)

        db.session.commit()
        
        return album, 200
    
    @staticmethod
    def deletar_album(id):
        album = Album.query.get_or_404(id)
        db.session.delete(album)
        db.session.commit()
        return {"message": f"Álbum {album.nome} deletado com sucesso"}, 200
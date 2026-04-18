from app.models.avaliacao import Avaliacao
from app.models.album import Album
from app.models.usuario import Usuario
from app.extensions import db

class AvaliacaoService:
    @staticmethod
    def criar_avaliacao(dados):
        nota = dados.get('nota')
        comentario = dados.get('comentario')
        usuario_id = dados.get('usuario_id')
        album_id = dados.get('album_id')
        
        if nota is None or nota < 1 or nota > 5:
            return {"error": "A nota da avaliação é obrigatória e deve ser um número entre 1 e 5"}, 400
        
        if not comentario:
            return {"error": "O comentário da avaliação é obrigatório"}, 400

        album = Album.query.get(album_id)
        if not album:
            return {"error": f"O álbum {album.titulo} não foi encontrado"}, 404
        
        usuario = Usuario.query.get(usuario_id)
        if not usuario:
            return {"error": f"O usuário {usuario.user} não foi encontrado"}, 404
        
        avaliacao = Avaliacao(
            nota=nota, 
            comentario=comentario.strip(), 
            usuario_id=usuario_id, 
            album_id=album_id)
        
        db.session.add(avaliacao)
        db.session.commit()

        return avaliacao, 201
    
    @staticmethod
    def editar_avaliacao(id, dados):
        avaliacao = Avaliacao.query.get_or_404(id)

        if not avaliacao:
            return {"error": f"A avaliação não foi encontrada"}, 404

        nova_nota = dados.get('nota')
        if nova_nota is not None and (nova_nota < 1 or nova_nota > 5):
            return {"error": "A nota da avaliação deve ser um número entre 1 e 5"}, 400
        
        if "comentario" in dados:
            novo_comentario = dados.get('comentario')
            if not novo_comentario:
                return {"error": "O comentário da avaliação é obrigatório"}, 400

        
        db.session.commit()
        return avaliacao, 200
    
    @staticmethod
    def delete_avaliacao(id):
        avaliacao = Avaliacao.query.get_or_404(id)
    
        db.session.delete(avaliacao)
        db.session.commit()
        return avaliacao, 200
        
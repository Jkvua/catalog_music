from app.models.avaliacao import Avaliacao
from app.models.album import Album
from app.models.usuario import Usuario
from app.extensions import db
from datetime import datetime

class AvaliacaoService:
    @staticmethod
    def criar_avaliacao(dados):
        nota = dados.get('nota')
        comentario = dados.get('comentario')
        usuario_id = dados.get('usuario_id')
        data_escuta_str = dados.get('data_escuta')
        usuario_email = dados.get('usuario_email')
        album_id = dados.get('album_id')
        album_nome = dados.get('album')
        
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
            album = Album.query.get(album_id)
            if not album:
                return {"error": f"Album com {album_id} não encontrado"}, 404
        if album_nome:
            album = Album.query.filter_by(titulo=album_nome.strip()).first()
            if not album:
                return {"error": f"Album {album_nome} não encontrado"}, 404
        else:
            return {"error": f"É necessario informar o nome do álbum ou o ID do álbum"}
        
        usuario = None
        if usuario_id:
            usuario = Usuario.query.get(usuario_id)
            if not usuario:
                return {"error": f"O usuário {usuario_id} não foi encontrado"}, 404
        if usuario_email:
            usuario = Usuario.query.filter_by(email=usuario_email.strip()).first()
            if not usuario:
                return {"error": f"O usuário com o email {usuario_email} não foi encontrado"}, 404
        else:
            return {f"error": f"É necessário informar o ID do usuário ou o email do usuário"}, 400
        
        existente = Avaliacao.query.filter_by(usuario_id=usuario.id, album_id=album.id).first()
        if existente:
            return {"error": f"Já existe avaliação para esse álbum"}, 400
        
        nova_avaliacao = Avaliacao(
            nota=nota, 
            comentario=comentario.strip(), 
            data_escuta=data_escuta,
            usuario_id=usuario.id, 
            album_id=album.id
            
            )
        
        db.session.add(nova_avaliacao)
        db.session.commit()

        return nova_avaliacao, 201
    
    @staticmethod
    def editar_avaliacao(id, dados):
        avaliacao = Avaliacao.query.get_or_404(id)

        nova_nota = dados.get('nota')
        if nova_nota is not None and (nova_nota < 1 or nova_nota > 5):
            return {"error": "A nota da avaliação deve ser um número entre 1 e 5"}, 400
        avaliacao.nota = nova_nota.strip()
        
        if "comentario" in dados:
            novo_comentario = dados.get('comentario')
            if not novo_comentario:
                return {"error": "O comentário da avaliação é obrigatório"}, 400
            avaliacao.comentario = novo_comentario.strip()

        if "data_escuta" in dados:
            data_escuta_str = dados.get("data_escuta")
            if data_escuta_str:
                try:
                    avaliacao.data_escuta = datetime.strptime(data_escuta_str, "%Y-%m-%d").date()
                except ValueError:
                    return {"error": "Formato de data inválido, use YYYY-MM-DD"}, 400
            else:
                return {"error": f"A data em que o álbum foi escutado é obrigatória"}, 400

        
        db.session.commit()
        return avaliacao, 200
    
    @staticmethod
    def delete_avaliacao(id):
        avaliacao = Avaliacao.query.get_or_404(id)
    
        db.session.delete(avaliacao)
        db.session.commit()
        return avaliacao, 200
        
from app.models.artista import Artista
from app.models.album import Album
from app.extensions import db

class ArtistaService:
    @staticmethod
    def criar_artista(dados):
        nome = dados.get('nome')
        genero = dados.get('genero')
        pais = dados.get('pais')
        
        if not nome or len(nome.strip()) < 1:
            return {"error": "O nome do artista é obrigatório e deve conter pelo menos 1 caractere"}, 400
        if not genero:
            return {"error": "O gênero musical do artista é obrigatório"}, 400
        if not pais:
            return {"error": "A nacionalidade/país do artista é obrigatória"}, 400
        
        existente = Artista.query.filter_by(nome=nome).first()
        if existente:
            return{"error": f"O Artista {nome} já existe no catálogo"}, 400
        
        novo_artista = Artista(
            nome=nome.strip(), 
            genero=genero.strip(),
            pais=pais.strip()
        )

        db.session.add(novo_artista)
        db.session.commit()

        return novo_artista, 201
    
    @staticmethod
    def editar_artista(id, dados):
        artista = Artista.query.get_or_404(id)

        novo_nome = dados.get('nome')
        if novo_nome and len(novo_nome.strip()) < 1:
            return {"error": "O nome do artista deve conter pelo menos 1 caractere"}, 400
        
        if novo_nome and novo_nome != artista.nome:
            existente = Artista.query.filter_by(nome=novo_nome).first()
            if existente and existente.id != id:
                return {"error": f"O Artista {novo_nome} já existe no catálogo"}, 400
            artista.nome = novo_nome
        
        if 'genero' in dados and not dados['genero']:
            return {"error": "O gênero musical do artista é obrigatório"}, 400
        artista.genero = dados.get('genero', artista.genero)
        
        if 'pais' in dados and not dados['pais']:
            return {"error": "A nacionalidade/país do artista é obrigatória"}, 400
        artista.pais = dados.get('pais', artista.pais)

        db.session.commit()
        
        return artista, 200
    
    @staticmethod
    def deletar_artista(id):
        artista = Artista.query.get_or_404(id)
        db.session.delete(artista)
        db.session.commit()

        return {"mensagem": f"O artista '{artista.nome}' e todos os dados vinculados foram deletados com sucesso"}, 200
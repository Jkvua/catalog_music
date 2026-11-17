from app.models.artista import Artista
from sqlalchemy.exc import IntegrityError
from app.extensions import db
from app.validators.artista import ArtistaValidator


class ArtistaService:

    @staticmethod
    def criar_artista(dados, usuario_id, commit=True):
        if not isinstance(dados, dict):
            return {
                "error": "Os dados do artista devem ser enviados em um objeto JSON válido"
            }, 400

        nome = dados.get('nome')
        genero = dados.get('genero')
        pais = dados.get('pais')

        if not ArtistaValidator.validar_nome(nome):
            return {
                "error": "O nome do artista é obrigatório e deve conter pelo menos 1 caractere"
            }, 400

        if not ArtistaValidator.validar_genero(genero):
            return {"error": "O gênero musical do artista é obrigatório"}, 400

        if not ArtistaValidator.validar_pais(pais):
            return {"error": "A nacionalidade/país do artista é obrigatória"}, 400

        nome = nome.strip()
        genero = genero.strip()
        pais = pais.strip()

        existente = Artista.query.filter_by(
            nome=nome,
            usuario_id=usuario_id
        ).first()

        if existente:
            return {"error": f"O Artista {nome} já existe no catálogo"}, 400

        novo_artista = Artista(
            nome=nome,
            usuario_id=usuario_id,
            genero=genero,
            pais=pais
        )

        try:
            db.session.add(novo_artista)
            if commit:
                db.session.commit()
            else:
                db.session.flush()
        except IntegrityError:
            db.session.rollback()
            return {
                "error": "Não foi possível cadastrar o artista devido a um conflito de integridade dos dados"
            }, 409

        return novo_artista, 201

    @staticmethod
    def editar_artista(id, dados, usuario_id):
        artista = db.get_or_404(Artista, id)

        if artista.usuario_id != usuario_id:
            return {
                "error": "Você não tem permissão para editar este artista"
            }, 403

        if not isinstance(dados, dict):
            return {
                "error": "Os dados do artista devem ser enviados em um objeto JSON válido"
            }, 400

        if 'nome' in dados and not ArtistaValidator.validar_nome(dados['nome']):
            return {
                "error": "O nome do artista deve conter pelo menos 1 caractere"
            }, 400

        if 'genero' in dados and not ArtistaValidator.validar_genero(dados['genero']):
            return {"error": "O gênero musical do artista é obrigatório"}, 400

        if 'pais' in dados and not ArtistaValidator.validar_pais(dados['pais']):
            return {"error": "A nacionalidade/país do artista é obrigatória"}, 400

        novo_nome = dados.get('nome', artista.nome).strip()
        novo_genero = dados.get('genero', artista.genero)
        novo_pais = dados.get('pais', artista.pais)

        if novo_nome != artista.nome:
            existente = Artista.query.filter_by(
                nome=novo_nome,
                usuario_id=usuario_id
            ).first()

            if existente and existente.id != artista.id:
                return {
                    "error": f"O Artista {novo_nome} já existe no catálogo"
                }, 400

        artista.nome = novo_nome
        artista.genero = novo_genero.strip() if isinstance(novo_genero, str) else novo_genero
        artista.pais = novo_pais.strip() if isinstance(novo_pais, str) else novo_pais

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {
                "error": "Não foi possível atualizar o artista devido a um conflito de integridade dos dados"
            }, 409

        return artista, 200

    @staticmethod
    def deletar_artista(id, usuario_id):
        artista = db.get_or_404(Artista, id)

        if artista.usuario_id != usuario_id:
            return {
                "error": "Você não tem permissão para deletar este artista"
            }, 403

        nome_artista = artista.nome

        try:
            db.session.delete(artista)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {
                "error": "Não foi possível excluir o artista devido a uma restrição de integridade dos dados"
            }, 409

        return {
            "mensagem": f"O artista '{nome_artista}' e todos os dados vinculados foram deletados com sucesso"
        }, 200
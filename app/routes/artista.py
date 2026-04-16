from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.artista import Artista
from app.schemas.artista import artista_schema, artistas_schema

artista_bp = Blueprint('artista', __name__, url_prefix='/artistas')

@artista_bp.route('/', methods=['GET'])
def get_artistas():
    todos_artistas = Artista.query.all()
    return jsonify(artistas_schema.dump(todos_artistas))

@artista_bp.route('/<int:id>', methods=['GET'])
def get_artista_id(id):
    artista = Artista.query.get_or_404(id)
    return jsonify(artista_schema.dump(artista))

@artista_bp.route('/', methods=['POST'])
def create_artista():
    json_data = request.get_json()

    try:
        novo_artista = artista_schema.load(json_data)

        db.session.add(novo_artista)
        db.session.commit()

        return artista_schema.dump(novo_artista), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@artista_bp.route('/<int:id>', methods=['PUT'])
def edit_artista(id):
    artista = Artista.query.get_or_404(id)

    data = request.get_json()
    artista.nome = data.get('nome', artista.nome)
    artista.pais = data.get('pais', artista.pais)
    artista.genero = data.get('genero', artista.genero)
    
    artista.albuns = data.get('albuns', artista.albuns)
    
    db.session.commit()

    return jsonify({
        "artista": artista_schema.dump(artista),
        "message": "Os dados do artista foram atualizados com sucesso"
    })

@artista_bp.route('/<int:id>', methods=['DELETE'])
def delete_artista(id):
    artista = Artista.query.get_or_404(id)
    nome_artista = artista.nome

    db.session.delete(artista)
    db.session.commit()

    return jsonify({
        "message": f"O artista '{nome_artista}' foi deletado com sucesso"
    })



    
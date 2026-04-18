from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.artista import Artista
from app.services.artista import ArtistaService
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
    dados = request.get_json()

    resultado, status = ArtistaService.criar_artista(dados)
    if status == 400:
        return jsonify(resultado), 400
    
    return artista_schema.dump(resultado), 201  
    
@artista_bp.route('/<int:id>', methods=['PUT'])
def edit_artista(id):
    data = request.get_json(id)
    
    resultado, status = ArtistaService.criar_artista(id, data)
    if status == 400:
        return jsonify(resultado), 400

    return jsonify({
        "artista": artista_schema.dump(resultado),
        "message": "Os dados do artista foram atualizados com sucesso"
    }), status

@artista_bp.route('/<int:id>', methods=['DELETE'])
def delete_artista(id):
    resultado, status = ArtistaService.deletar_artista(id)

    return jsonify({
        "message": f"O artista {resultado.nome} foi deletado com sucesso"
    }), status


    
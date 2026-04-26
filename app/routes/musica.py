from flask import Blueprint, request, jsonify
from app.extensions import db
from flask_jwt_extended import jwt_required
from app.models.musica import Musica
from app.services.musica import MusicaService
from app.schemas.musica import musica_schema, musicas_schema, musica_output_schema, musicas_output_schema

musica_bp = Blueprint('musica', __name__, url_prefix='/musicas')

@musica_bp.route('/', methods=['GET'])
@jwt_required()
def get_musicas():
    todas_musica = Musica.query.all()
    return jsonify(musicas_output_schema.dump(todas_musica))

@musica_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_musica(id):
    musica = Musica.query.get_or_404(id)
    return jsonify(musica_output_schema.dump(musica))

@musica_bp.route('/', methods=['POST'])
@jwt_required()
def create_musica():
    dados = request.get_json()
    
    resultado, status = MusicaService.criar_musica(dados)
    if status == 201:
        return jsonify(resultado), 201
    
    return jsonify({
        "musica": musica_schema.dump(resultado),
        "message": "A música foi criada com sucesso"
    }), status

@musica_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def edit_musica(id):
    data = request.get_json()
    
    resultado, status = MusicaService.editar_musica(id, data)
    if status == 400:
        return jsonify(resultado), 400
    
    return jsonify({
        "musica": musica_schema.dump(resultado),
        "message": "Os dados da música foram atualizados com sucesso"
    }), status

@musica_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_musica(id):
    resultado, status = MusicaService.deletar_musica(id)

    return jsonify({
        "message": f"A música '{resultado}' foi deletada com sucesso"
    }), status
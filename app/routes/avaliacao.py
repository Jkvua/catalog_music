from flask import Blueprint, request, jsonify
from app.extensions import db
from flask_jwt_extended import jwt_required
from app.models.avaliacao import Avaliacao
from app.services.avaliacoes import AvaliacaoService
from app.schemas.avaliacao import avaliacao_schema, avaliacoes_schema

avaliacao_bp = Blueprint('avaliacao', __name__, url_prefix='/avaliacoes')

@avaliacao_bp.route('/', methods=['GET'])
@jwt_required()
def get_avaliacoes():
    todas_avaliacao = Avaliacao.query.all()
    return jsonify(avaliacoes_schema.dump(todas_avaliacao))

@avaliacao_bp.route('/<int:id>', methods=['GET'])
@jwt_required()
def get_avaliacao(id):
    avaliacao_id = Avaliacao.query.get_or_404(id)
    return jsonify(avaliacao_schema.dump(avaliacao_id))

@avaliacao_bp.route('/', methods=['POST'])
@jwt_required()
def create_avaliacao():
    data = request.get_json()
    
    resultado, status = AvaliacaoService.criar_avaliacao(data)
    if status == 400:
        return jsonify(resultado), status
    
    return jsonify({
        "avaliacao": avaliacao_schema.dump(resultado),
        "message": "A avaliação foi criada com sucesso"
    }), status

@avaliacao_bp.route('/<int:id>', methods=['PUT'])
@jwt_required()
def edit_avaliacao(id):
    data = request.get_json(id)
    
    resultado, status = AvaliacaoService.editar_avaliacao(id, data)
    if status == 400:
        return jsonify(resultado), status
    
    return jsonify({
        "avaliacao": avaliacao_schema.dump(resultado),
        "message": "Os dados da avaliação foram atualizados com sucesso"
    }), status
    
@avaliacao_bp.route('/<int:id>', methods=['DELETE'])
@jwt_required()
def delete_avaliacao(id):
    avaliacao, status = AvaliacaoService.delete_avaliacao(id)

    return jsonify({
        "message": f"A avaliação {avaliacao.id} sobre o álbum {avaliacao.album.titulo}'foi deletada com sucesso"
    }), status
    
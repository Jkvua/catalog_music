from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.avaliacao import Avaliacao
from app.schemas.avaliacao import avaliacao_schema, avaliacoes_schema

avaliacao_bp = Blueprint('avaliacao', __name__, url_prefix='/avaliacoes')

@avaliacao_bp.route('/', methods=['GET'])
def get_avaliacoes():
    todas_avaliacao = Avaliacao.query.all()
    return jsonify(avaliacoes_schema.dump(todas_avaliacao))

@avaliacao_bp.route('/<int:id>', methods=['GET'])
def get_avaliacao(id):
    avaliacao_id = Avaliacao.query.get_or_404(id)
    return jsonify(avaliacao_schema.dump(avaliacao_id))

@avaliacao_bp.route('/', methods=['POST'])
def create_avaliacao():
    json_data = request.get_json()
    try:
        nova_avaliacao = avaliacao_schema.load(json_data)

        db.session.add(nova_avaliacao)
        db.session.commit()

        return jsonify(avaliacao_schema.dump(nova_avaliacao)), 201
    
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    
@avaliacao_bp.route('/<int:id>', methods=['PUT'])
def edit_avaliacao(id):
    avaliacao = Avaliacao.query.get_or_404(id)

    data = request.get_json()
    avaliacao.nota = data.get('nota', avaliacao.nota)
    avaliacao.comentario = data.get('comentario', avaliacao.comentario)
    avaliacao.data_escuta = data.get('data_escuta', avaliacao.data_escuta)

    db.session.commit()
    return jsonify({
        "avaliacao": avaliacao_schema.dump(avaliacao),
        "message": "A avaliação foi atualizada com sucesso"
    })    
    
@avaliacao_bp.route('/<int:id>', methods=['DELETE'])
def delete_avaliacao(id):
    avaliacao = Avaliacao.query.get_or_404(id)
    nota_avaliacao = avaliacao.nota
    
    nome_album = avaliacao.album.titulo if avaliacao.album else "Desconecido"

    db.session.delete(avaliacao)
    db.session.commit()

    return jsonify({
        "message": f"A avaliação com nota '{nota_avaliacao}' do álbum '{nome_album}' foi deletada com sucesso"
    })
    
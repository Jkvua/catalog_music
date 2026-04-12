from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.avaliacao import Avaliacao

avaliacao_bp = Blueprint('avaliacao', __name__, url_prefix='/avaliacoes')

@avaliacao_bp.route('/', methods=['GET'])
def get_avaliacoes():
    avaliacao = Avaliacao.query.all()
    return jsonify([{"id": avaliacao.id, "nota": avaliacao.nota} for avaliacao in avaliacao])

@avaliacao_bp.route('/', methods=['POST'])
def create_avaliacao():
    data = request.get_json()
    nova = Avaliacao(nota=data["nota"],
                   comentario=data.get["comentario"],
                   data_escuta=data.get["data_escuta"],
                   
        )
    
    db.session.add(nova)
    db.session.commit()

    return jsonify({
        "id": nova.id, 
        "nota": nova.nota,
        "comentario": nova.comentario,
        "data_escuta": nova.data_escuta
    }), 201
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.artista import Artista

artista_bp = Blueprint('artista', __name__, url_prefix='/artistas')

@artista_bp.route('/', methods=['GET'])
def get_artistas():
    artistas = Artista.query.all()
    return jsonify([{"id": artista.id, "nome": artista.nome} for artista in artistas])

@artista_bp.route('/', methods=['POST'])
def create_artista():
    data = request.get_json()
    novo = Artista(nome=data["nome"],
                   genero=data.get["genero"],
                   pais=data.get["pais"] 
        )
    
    db.session.add(novo)
    db.session.commit()

    return jsonify({
        "id": novo.id, 
        "nome": novo.nome,
        "genero": novo.genero,
        "pais": novo.pais
    }), 201
    
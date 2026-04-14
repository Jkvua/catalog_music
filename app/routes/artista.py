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
    
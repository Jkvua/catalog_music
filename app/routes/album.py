from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.album import Album

album_bp = Blueprint('album', __name__, url_prefix='/albuns')

@album_bp.route('/', methods=['GET'])
def get_albuns():
    albuns = Album.query.all()
    return jsonify([{"id": album.id, "titulo": album.titulo, "ano": album.ano} for album in albuns])

@album_bp.route('/', methods=['POST'])
def create_album():
    data = request.get_json()
    novo = Album(titulo=data["titulo"],
                 artista_id=data["artista_id"],
                 ano=data.get("ano")
        )
    
    db.session.add(novo)
    db.session.commit()

    return jsonify({
        "id": novo.id, 
        "titulo": novo.titulo,
        "artista_id": novo.artista_id,
        "ano": novo.ano
    }), 201
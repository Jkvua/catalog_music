from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.musica import Musica

musica_bp = Blueprint('musica', __name__, url_prefix='/musicas')

@musica_bp.route('/', methods=['GET'])
def get_musicas():
    musica = Musica.query.all()
    return jsonify([{"id": musica.id, "titulo": musica.titulo} for musica in musica])

def create_musica():
    data = request.get_json()
    nova = Musica(titulo=data["titulo"],
                   duracao=data.get("duracao"),
                   genero=data.get("genero"),
                   artista_id=data.get("artista_id"),
                   album_id=data.get("album_id")
        )
    
    db.session.add(nova)
    db.session.commit()

    return jsonify({
        "id": nova.id, 
        "titulo": nova.titulo,
        "duracao": nova.duracao,
        "genero": nova.genero,
        "artista_id": nova.artista_id,
        "album_id": nova.album_id
    }), 201
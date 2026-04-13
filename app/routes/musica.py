from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.musica import Musica
from app.schemas.musica import musica_schema, musicas_schema

musica_bp = Blueprint('musica', __name__, url_prefix='/musicas')

@musica_bp.route('/', methods=['GET'])
def get_musicas():
    todas_musica = Musica.query.all()
    return jsonify(musicas_schema.dump(todas_musica))

def create_musica():
    json_data = request.get_json()
    try:
        nova_musica = musica_schema.load(json_data)
    
        db.session.add(nova_musica)
        db.session.commit()

        return musica_schema.dump(nova_musica), 201
    
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
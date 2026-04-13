from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.album import Album
from app.schemas.album import album_schema, albums_schema

album_bp = Blueprint('album', __name__, url_prefix='/albuns')

@album_bp.route('/', methods=['GET'])
def get_albuns():
    todos_albuns = Album.query.all()
    return jsonify(albums_schema.dump(todos_albuns))

@album_bp.route('/', methods=['POST'])
def create_album():
    json_data = request.get_json()
    try:
        novo_album = album_schema.load(json_data)
    
        db.session.add(novo_album)
        db.session.commit()

        return album_schema.dump(novo_album), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
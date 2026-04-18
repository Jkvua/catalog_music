from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.album import Album
from app.services.album import AlbumService
from app.schemas.album import album_schema, albums_schema


album_bp = Blueprint('album', __name__, url_prefix='/albuns')

@album_bp.route('/', methods=['GET'])
def get_albuns():
    todos_albuns = Album.query.all()
    return jsonify(albums_schema.dump(todos_albuns))

@album_bp.route('/<int:id>', methods=['GET'])
def get_album_id(id):
    album = Album.query.get_or_404(id)
    return jsonify(album_schema.dump(album))

@album_bp.route('/', methods=['POST'])
def create_album():
    dados = request.get_json()
    resultado, status = AlbumService.criar_album(dados)
    
    if status != 400:
        return jsonify(resultado), status
    
    return jsonify({
        "album": album_schema.dump(resultado),
        "message": "O álbum foi criado com sucesso"
    }), status

@album_bp.route('/<int:id>', methods=['PUT'])
def edit_album(id):
    dados = request.get_json()
    resultado, status = AlbumService.editar_album(id, dados)
    
    if status != 400:
        return jsonify(resultado), status
    
    return jsonify({
        "album": album_schema.dump(resultado),
        "message": "O álbum foi atualizado com sucesso"
    }), status

@album_bp.route('/<int:id>', methods=['DELETE'])
def delete_album(id):
    resultado, status = AlbumService.deletar_album(id)
    return jsonify({
        "message": f"O álbum '{resultado.titulo}' foi deletado com sucesso"
    }), status
    
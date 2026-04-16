from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.musica import Musica
from app.schemas.musica import musica_schema, musicas_schema, musica_output_schema, musicas_output_schema

musica_bp = Blueprint('musica', __name__, url_prefix='/musicas')

@musica_bp.route('/', methods=['GET'])
def get_musicas():
    todas_musica = Musica.query.all()
    return jsonify(musicas_output_schema.dump(todas_musica))

@musica_bp.route('/<int:id>', methods=['GET'])
def get_musica(id):
    musica = Musica.query.get_or_404(id)
    return jsonify(musica_output_schema.dump(musica))

@musica_bp.route('/', methods=['POST'])
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

@musica_bp.route('/<int:id>', methods=['PUT'])
def edit_musica(id):
    musica = Musica.query.get_or_404(id)

    data = request.get_json()
    musica.titulo = data.get('titulo', musica.titulo)
    musica.duracao = data.get('duracao', musica.duracao)
    musica.album_id = data.get('album_id', musica.album_id)
    musica.artista_id = data.get('artista_id', musica.artista_id)

    db.session.commit()
    return jsonify({
        "musica": musica_schema.dump(musica),
        "artista": musica.artista.nome if musica.artista else "Artista não encontrado",
        "message": "Os dados da música foram atualizados com sucesso"
    })

@musica_bp.route('/<int:id>', methods=['DELETE'])
def delete_musica(id):
    musica = Musica.query.get_or_404(id)
    titulo_musica = musica.titulo

    db.session.delete(musica)
    db.session.commit()

    return jsonify({
        "message": f"A música '{titulo_musica}' foi deletada com sucesso"
    })
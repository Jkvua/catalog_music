import os
import pytest
import requests
import time
from sqlalchemy import create_engine, text

BASE_URL = os.getenv("API_URL", "http://localhost:5000")
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

def registro_existe(conn, tabela, registro_id):
    tabelas_permitidas = {"artistas", "albuns", "musica", "avaliacao"}

    if tabela not in tabelas_permitidas:
        raise ValueError(f"Tabela não permitida: {tabela}")

    quantidade = conn.execute(text(f"SELECT COUNT(*) FROM {tabela} WHERE id = :id"), {"id": registro_id}).scalar_one()
    return quantidade == 1

def usuario_existe(conn, email):
    quantidade = conn.execute(text("SELECT COUNT(*) FROM usuarios WHERE email = :email"), {"email": email}).scalar_one()
    return quantidade == 1

def test_jornada_completa_usuario():
    """Simula o fluxo completo da jornada do usuário"""
    sufixo = str(int(time.time()))
    email = f"mariadefatima{sufixo}@gmail.com"
    nome_user = f"fatima{sufixo}"

    res_registro = requests.post(f"{BASE_URL}/auth/register", json={"user": nome_user, "email": email, "password": "mariadefatima1917"})
    assert res_registro.status_code == 201, f"Falha no registro: {res_registro.text}"

    res_login = requests.post(f"{BASE_URL}/auth/login", json={"email": email, "password": "mariadefatima1917"})
    assert res_login.status_code == 200, f"Falha no login: {res_login.text}"
    token = res_login.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}"}

    res_artista = requests.post(f"{BASE_URL}/artistas/", json={"nome": f"kali uchis {sufixo}", "genero": "R&B", "pais": "EUA"}, headers=headers)
    assert res_artista.status_code == 201, f"Falha ao cadastrar artista"
    artista_id = res_artista.json()["artista"]["id"]

    res_album = requests.post(f"{BASE_URL}/albuns/", json={"titulo": f"Isolation {sufixo}", "ano": 2018, "artista_id": artista_id}, headers=headers)
    assert res_album.status_code == 201, "Falha ao cadastrar álbum"
    album_id = res_album.json()["album"]["id"]

    musicas_ids = []
    musicas_cadastrar = [
        {"titulo": f"Body Language - Intro {sufixo}", "duracao": "2:16"},
        {"titulo": f"Miami {sufixo}", "duracao": "4:04"},
        {"titulo": f"Just a Stranger {sufixo}", "duracao": "2:58"},
        {"titulo": f"Flight 22 {sufixo}", "duracao": "3:37"},
        {"titulo": f"Your Teeth In My Neck {sufixo}", "duracao": "3:06"},
        {"titulo": f"Tyrant {sufixo}", "duracao": "3:24"},
        {"titulo": f"Dead To Me {sufixo}", "duracao": "3:20"},
        {"titulo": f"Nuestro Planeta {sufixo}", "duracao": "3:23"},
        {"titulo": f"In My Dreams {sufixo}", "duracao": "3:21"},
        {"titulo": f"Gettin' Up {sufixo}", "duracao": "1:53"},
        {"titulo": f"Coming Home (Interlude) {sufixo}", "duracao": "2:40"},
        {"titulo": f"After the Storm {sufixo}", "duracao": "2:16"},
        {"titulo": f"Feel Like a Fool {sufixo}", "duracao": "3:27"},
        {"titulo": f"Killer {sufixo}", "duracao": "2:52"},
        {"titulo": f"Strawberry Sundae {sufixo}", "duracao": "3:10"}
    ]
    for musica in musicas_cadastrar:
        res_musica = requests.post(f"{BASE_URL}/musicas/", json={"titulo": musica["titulo"], "duracao": musica["duracao"], "album_id": album_id, "artista_id": artista_id}, headers=headers)
        assert res_musica.status_code == 201, f"Falha ao cadastrar a {musica['titulo']}: {res_musica.text}"
        musicas_ids.append(res_musica.json()["musica"]["id"])

    res_avaliacao = requests.post(f"{BASE_URL}/avaliacoes/", json={"nota": 5, "comentario": "Que álbum incrivel, tem coisas que só kali uchis sabe fazer", "data_escuta": "2026-11-01", "album_id": album_id}, headers=headers)
    assert res_avaliacao.status_code == 201, f"Falha ao cadastrar avaliação de álbum: {res_avaliacao.text}"
    avaliacao_id = res_avaliacao.json()["avaliacao"]["id"]

    assert TEST_DATABASE_URL, "TEST_DATABASE_URL não configurada"
    engine = create_engine(TEST_DATABASE_URL)

    try:
        with engine.connect() as conn:
            assert usuario_existe(conn, email), "Usuário não encontrado no banco"
            assert registro_existe(conn, "artistas", artista_id), "Artista não encontrado"
            assert registro_existe(conn, "albuns", album_id), "Álbum não encontrado"
            assert registro_existe(conn, "avaliacao", avaliacao_id), "Avaliação não encontrada"
            for musica_id in musicas_ids:
                assert registro_existe(conn, "musica", musica_id), (f"Música {musica_id} não encontrada")

        res_delete = requests.delete(f"{BASE_URL}/usuarios/me", headers=headers)

        assert res_delete.status_code in [200, 204], (f"Falha ao deletar conta: {res_delete.text}")

        with engine.connect() as conn:
            assert not usuario_existe(conn, email), "Usuário não foi excluído"
            assert not registro_existe(conn, "artistas", artista_id), "Artista não foi excluído"
            assert not registro_existe(conn, "albuns", album_id), "Álbum não foi excluído"
            assert not registro_existe(conn, "avaliacao", avaliacao_id), "Avaliação não foi excluída"

            for musica_id in musicas_ids:
                assert not registro_existe(conn, "musica", musica_id), (f"Música {musica_id} não foi excluída")
    finally:
        engine.dispose()

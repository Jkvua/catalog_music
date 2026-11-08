import os
import pytest
import requests
import time

BASE_URL = os.getenv("API_URL", "http://localhost:5000")

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

    res_avaliacao = requests.post(f"{BASE_URL}/avaliacoes/", json={"nota": 5, "comentario": "Que álbum incrivel, tem coisas que só kali uchis sabe fazer", "data_escuta": "2026-11-01", "album_id": album_id}, headers=headers)
    assert res_avaliacao.status_code == 201, f"Falha ao cadastrar avaliação de álbum: {res_avaliacao.text}"

    res_delete = requests.delete(f"{BASE_URL}/usuarios/me", headers=headers)
    assert res_delete.status_code in [200, 204], f"Falha ao deletar conta: {res_delete.text}"

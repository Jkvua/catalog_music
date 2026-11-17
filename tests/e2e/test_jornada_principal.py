import os
from uuid import uuid4

import requests


BASE_URL = os.getenv("API_URL", "http://localhost:5000")


def verificar_criacao(endpoint, registro_id, headers):
    """Verifica se um registro pode ser consultado pela API."""

    resposta = requests.get(
        f"{BASE_URL}/{endpoint}/{registro_id}",
        headers=headers
    )

    assert resposta.status_code == 200, (
        f"Falha ao consultar {endpoint}/{registro_id}: "
        f"{resposta.text}"
    )

    assert resposta.json()["id"] == registro_id


def test_jornada_completa_usuario():
    """Verifica a jornada completa de utilização da aplicação."""

    # Arrange
    sufixo = uuid4().hex[:10]

    email = f"mariadefatima{sufixo}@gmail.com"
    nome_user = f"fatima{sufixo}"
    senha = "mariadefatima1917"

    # ========================================================
    # 1. CADASTRO DO USUÁRIO
    # ========================================================

    res_registro = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "user": nome_user,
            "email": email,
            "password": senha
        }
    )

    assert res_registro.status_code == 201, (
        f"Falha no registro: {res_registro.text}"
    )

    # ========================================================
    # 2. LOGIN
    # ========================================================

    res_login = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": email,
            "password": senha
        }
    )

    assert res_login.status_code == 200, (
        f"Falha no login: {res_login.text}"
    )

    token = res_login.json().get("access_token")
    assert token is not None

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # ========================================================
    # 3. CADASTRO DO ARTISTA
    # ========================================================

    res_artista = requests.post(
        f"{BASE_URL}/artistas/",
        json={
            "nome": f"Kali Uchis {sufixo}",
            "genero": "R&B",
            "pais": "EUA"
        },
        headers=headers
    )

    assert res_artista.status_code == 201, (
        f"Falha ao cadastrar artista: {res_artista.text}"
    )

    artista_id = res_artista.json()["artista"]["id"]

    # ========================================================
    # 4. CADASTRO DO ÁLBUM
    # ========================================================

    res_album = requests.post(
        f"{BASE_URL}/albuns/",
        json={
            "titulo": f"Isolation {sufixo}",
            "ano": 2018,
            "artista_id": artista_id
        },
        headers=headers
    )

    assert res_album.status_code == 201, (
        f"Falha ao cadastrar álbum: {res_album.text}"
    )

    album_id = res_album.json()["album"]["id"]

    # ========================================================
    # 5. CADASTRO DAS MÚSICAS
    # ========================================================

    musicas_cadastrar = [
        {
            "titulo": f"Body Language - Intro {sufixo}",
            "duracao": "02:16"
        },
        {
            "titulo": f"Miami {sufixo}",
            "duracao": "04:04"
        }
    ]

    musicas_ids = []

    for musica in musicas_cadastrar:

        res_musica = requests.post(
            f"{BASE_URL}/musicas/",
            json={
                "titulo": musica["titulo"],
                "duracao": musica["duracao"],
                "album_id": album_id,
                "artista_id": artista_id
            },
            headers=headers
        )

        assert res_musica.status_code == 201, (
            f"Falha ao cadastrar música "
            f"{musica['titulo']}: {res_musica.text}"
        )

        musica_id = res_musica.json()["musica"]["id"]
        musicas_ids.append(musica_id)

    # ========================================================
    # 6. CADASTRO DA AVALIAÇÃO
    # ========================================================

    res_avaliacao = requests.post(
        f"{BASE_URL}/avaliacoes/",
        json={
            "nota": 5,
            "comentario": "Álbum incrível da Kali Uchis",
            "data_escuta": "2026-11-01",
            "album_id": album_id
        },
        headers=headers
    )

    assert res_avaliacao.status_code == 201, (
        f"Falha ao cadastrar avaliação: {res_avaliacao.text}"
    )

    avaliacao_id = res_avaliacao.json()["avaliacao"]["id"]

    # ========================================================
    # 7. CONSULTA DOS DADOS
    # ========================================================

    res_usuario = requests.get(
        f"{BASE_URL}/usuarios/me",
        headers=headers
    )

    assert res_usuario.status_code == 200, (
        f"Falha ao consultar usuário: {res_usuario.text}"
    )

    assert res_usuario.json()["email"] == email

    verificar_criacao("artistas", artista_id, headers)
    verificar_criacao("albuns", album_id, headers)
    verificar_criacao("avaliacoes", avaliacao_id, headers)

    for musica_id in musicas_ids:
        verificar_criacao("musicas", musica_id, headers)

    # ========================================================
    # 8. EXCLUSÃO DA CONTA
    # ========================================================

    res_delete = requests.delete(
        f"{BASE_URL}/usuarios/me",
        headers=headers
    )

    assert res_delete.status_code in [200, 204], (
        f"Falha ao deletar conta: {res_delete.text}"
    )

    # ========================================================
    # 9. LOGIN APÓS EXCLUSÃO
    # ========================================================

    res_login_pos_exclusao = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": email,
            "password": senha
        }
    )

    assert res_login_pos_exclusao.status_code == 401, (
        f"Usuário excluído conseguiu fazer login: "
        f"{res_login_pos_exclusao.text}"
    )
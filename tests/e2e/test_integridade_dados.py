import os
from uuid import uuid4

import requests


BASE_URL = os.getenv("API_URL", "http://localhost:5000")


def test_conflito_email_duplicado():
    """Verifica o bloqueio de cadastro com e-mail duplicado."""

    # Arrange
    sufixo = uuid4().hex[:10]

    email = f"jandira{sufixo}@gmail.com"

    dados_primeiro = {
        "user": f"jandira{sufixo}",
        "email": email,
        "password": "jandira2897"
    }

    dados_segundo = {
        "user": f"jana{sufixo}",
        "email": email,
        "password": "janapereira234"
    }

    # Act
    res_1 = requests.post(
        f"{BASE_URL}/auth/register",
        json=dados_primeiro
    )

    # Assert
    assert res_1.status_code == 201, (
        f"Falha no primeiro cadastro: {res_1.text}"
    )

    # Act
    res_2 = requests.post(
        f"{BASE_URL}/auth/register",
        json=dados_segundo
    )

    # Assert
    assert res_2.status_code == 400, (
        f"Deveria bloquear e-mail duplicado. "
        f"Status: {res_2.status_code}, resposta: {res_2.text}"
    )


def test_chave_estrangeira_invalida():
    """Verifica a rejeição de uma avaliação com álbum inexistente."""

    # Arrange
    sufixo = uuid4().hex[:10]

    email = f"maicon{sufixo}@gmail.com"
    senha = "silvamaicon21"

    dados_usuario = {
        "user": f"maicon{sufixo}",
        "email": email,
        "password": senha
    }

    # Act - Cadastro
    res_registro = requests.post(
        f"{BASE_URL}/auth/register",
        json=dados_usuario
    )

    # Assert
    assert res_registro.status_code == 201, (
        f"Falha no cadastro: {res_registro.text}"
    )

    # Act - Login
    res_login = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": email,
            "password": senha
        }
    )

    # Assert
    assert res_login.status_code == 200, (
        f"Falha no login: {res_login.text}"
    )

    token = res_login.json().get("access_token")
    assert token is not None

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Act - Tentativa de avaliação com álbum inexistente
    res_avaliacao = requests.post(
        f"{BASE_URL}/avaliacoes/",
        json={
            "nota": 5,
            "comentario": "Bom",
            "data_escuta": "2026-10-10",
            "album_id": 999999
        },
        headers=headers
    )

    # Assert
    assert res_avaliacao.status_code == 404, (
        f"Deveria rejeitar álbum inexistente. "
        f"Status: {res_avaliacao.status_code}, "
        f"resposta: {res_avaliacao.text}"
    )
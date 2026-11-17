import os

import requests


BASE_URL = os.getenv("API_URL", "http://localhost:5000")


def test_acesso_sem_token():
    """Verifica o bloqueio de requisições sem autenticação."""

    # Act - Consulta sem token
    res_me = requests.get(
        f"{BASE_URL}/usuarios/me"
    )

    # Assert
    assert res_me.status_code == 401, (
        f"Acesso sem token não foi bloqueado: {res_me.text}"
    )

    # Act - Criação sem token
    res_artista = requests.post(
        f"{BASE_URL}/artistas/",
        json={
            "nome": "Young Miko",
            "genero": "Trap",
            "pais": "Porto Rico"
        }
    )

    # Assert
    assert res_artista.status_code == 401, (
        f"Criação sem token não foi bloqueada: "
        f"{res_artista.text}"
    )


def test_acesso_token_invalido():
    """Verifica o bloqueio de requisições com token inválido."""

    # Arrange
    headers = {
        "Authorization": "Bearer token_completamente_errado"
    }

    # Act
    res_me = requests.get(
        f"{BASE_URL}/usuarios/me",
        headers=headers
    )

    # Assert
    assert res_me.status_code in [401, 422], (
        f"Token inválido não foi bloqueado. "
        f"Status: {res_me.status_code}, "
        f"resposta: {res_me.text}"
    )
import os
from uuid import uuid4

import requests


BASE_URL = os.getenv("API_URL", "http://localhost:5000")


def test_isolamento_entre_usuarios():
    """Verifica que um usuário não pode excluir dados de outro."""

    # Arrange
    sufixo = uuid4().hex[:10]

    email_a = f"fatima{sufixo}@gmail.com"
    senha_a = "fatimab1090"

    email_b = f"bonner{sufixo}@gmail.com"
    senha_b = "willbonner"

    # Act - Cadastro do usuário A
    res_registro_a = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "user": f"fatima{sufixo}",
            "email": email_a,
            "password": senha_a
        }
    )

    # Assert
    assert res_registro_a.status_code == 201, (
        f"Falha ao cadastrar usuário A: {res_registro_a.text}"
    )

    # Act - Login do usuário A
    res_login_a = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": email_a,
            "password": senha_a
        }
    )

    # Assert
    assert res_login_a.status_code == 200, (
        f"Falha no login do usuário A: {res_login_a.text}"
    )

    token_a = res_login_a.json().get("access_token")
    assert token_a is not None

    headers_a = {
        "Authorization": f"Bearer {token_a}"
    }

    # Act - Criação do artista pelo usuário A
    res_artista_a = requests.post(
        f"{BASE_URL}/artistas/",
        json={
            "nome": f"Tim Bernardes {sufixo}",
            "genero": "MPB",
            "pais": "Brasil"
        },
        headers=headers_a
    )

    # Assert
    assert res_artista_a.status_code == 201, (
        f"Falha ao criar artista: {res_artista_a.text}"
    )

    artista_id = res_artista_a.json()["artista"]["id"]

    # Act - Cadastro do usuário B
    res_registro_b = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "user": f"bonner{sufixo}",
            "email": email_b,
            "password": senha_b
        }
    )

    # Assert
    assert res_registro_b.status_code == 201, (
        f"Falha ao cadastrar usuário B: {res_registro_b.text}"
    )

    # Act - Login do usuário B
    res_login_b = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": email_b,
            "password": senha_b
        }
    )

    # Assert
    assert res_login_b.status_code == 200, (
        f"Falha no login do usuário B: {res_login_b.text}"
    )

    token_b = res_login_b.json().get("access_token")
    assert token_b is not None

    headers_b = {
        "Authorization": f"Bearer {token_b}"
    }

    # Act - Usuário B tenta excluir artista do usuário A
    res_delete_b = requests.delete(
        f"{BASE_URL}/artistas/{artista_id}",
        headers=headers_b
    )

    # Assert
    assert res_delete_b.status_code == 403, (
        f"Deveria bloquear exclusão por outro usuário. "
        f"Status: {res_delete_b.status_code}, "
        f"resposta: {res_delete_b.text}"
    )

    # Act - Usuário A consulta o artista
    res_consulta_a = requests.get(
        f"{BASE_URL}/artistas/{artista_id}",
        headers=headers_a
    )

    # Assert
    assert res_consulta_a.status_code == 200, (
        f"O artista não deveria ter sido excluído: "
        f"{res_consulta_a.text}"
    )

    assert res_consulta_a.json()["id"] == artista_id
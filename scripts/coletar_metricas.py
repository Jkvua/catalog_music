import csv
import os
from pathlib import Path

import requests


REPOSITORIO = "Jkvua/catalog_music"
ARQUIVO_SAIDA = Path("resultados/dados_brutos.csv")

API_URL = f"https://api.github.com/repos/{REPOSITORIO}"


def consultar_execucoes():
    """Consulta as execuções recentes do GitHub Actions."""

    token = os.getenv("GITHUB_TOKEN")

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    if token:
        headers["Authorization"] = f"Bearer {token}"

    resposta = requests.get(
        f"{API_URL}/actions/runs",
        headers=headers,
        params={"per_page": 10},
        timeout=30
    )

    resposta.raise_for_status()

    return resposta.json()["workflow_runs"]


def salvar_csv(execucoes):
    """Salva os dados brutos das execuções em CSV."""

    ARQUIVO_SAIDA.parent.mkdir(parents=True, exist_ok=True)

    campos = [
        "run_id",
        "commit_sha",
        "branch",
        "evento",
        "status",
        "conclusao",
        "created_at",
        "run_started_at",
        "updated_at"
    ]

    with ARQUIVO_SAIDA.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.DictWriter(arquivo, fieldnames=campos)

        escritor.writeheader()

        for execucao in execucoes:
            escritor.writerow({
                "run_id": execucao["id"],
                "commit_sha": execucao["head_sha"],
                "branch": execucao["head_branch"],
                "evento": execucao["event"],
                "status": execucao["status"],
                "conclusao": execucao["conclusion"],
                "created_at": execucao["created_at"],
                "run_started_at": execucao.get("run_started_at"),
                "updated_at": execucao["updated_at"]
            })


def main():
    print("Consultando execuções do GitHub Actions...")

    execucoes = consultar_execucoes()

    salvar_csv(execucoes)

    print(f"{len(execucoes)} execuções registradas.")
    print(f"Arquivo gerado: {ARQUIVO_SAIDA}")


if __name__ == "__main__":
    main()
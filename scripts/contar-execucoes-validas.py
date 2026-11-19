import csv
from collections import defaultdict
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
RESULTADOS = RAIZ / "resultados"

META = 5
CENARIOS = ("a", "b", "c")


def ler_csv(caminho):
    with caminho.open(newline="", encoding="utf-8") as arquivo:
        return list(csv.DictReader(arquivo))


def main():
    caminho_validade = RESULTADOS / "validade_execucoes.csv"

    if not caminho_validade.is_file():
        print("Erro: arquivo validade_execucoes.csv não encontrado.")
        return

    registros = ler_csv(caminho_validade)

    contagem = defaultdict(int)
    commits_por_versao = defaultdict(set)

    for registro in registros:
        versao = registro["versao"]
        execucao = registro["execucao"]
        cenario = registro["cenario"]

        caminho_metadados = (
            RESULTADOS / versao / execucao / "metadados.csv"
        )

        if not caminho_metadados.is_file():
            print(f"Aviso: metadados ausentes em {versao}/{execucao}")
            continue

        metadados = ler_csv(caminho_metadados)

        if len(metadados) != 1:
            print(f"Aviso: metadados inválidos em {versao}/{execucao}")
            continue

        commit = metadados[0]["git_commit"]
        commits_por_versao[versao].add(commit)

        if registro["status"] == "valida":
            contagem[(versao, commit, cenario)] += 1

    print(
        "versao,git_commit,cenario,validas,meta,faltantes"
    )

    for versao in sorted(commits_por_versao):
        for commit in sorted(commits_por_versao[versao]):
            for cenario in CENARIOS:
                validas = contagem[(versao, commit, cenario)]
                faltantes = max(0, META - validas)

                print(
                    f"{versao},{commit},{cenario},"
                    f"{validas},{META},{faltantes}"
                )


if __name__ == "__main__":
    main()
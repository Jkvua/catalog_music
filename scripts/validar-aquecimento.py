import csv
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
RESULTADOS = RAIZ_PROJETO / "resultados"

TESTES_ESPERADOS = {
    "unitarios": 221,
    "integracao": 115,
    "e2e": 6,
}


def ler_csv(caminho):
    with caminho.open(newline="", encoding="utf-8") as arquivo:
        return list(csv.DictReader(arquivo))


def main():
    validade = ler_csv(RESULTADOS / "validade_execucoes.csv")
    metricas = ler_csv(RESULTADOS / "metricas_testes.csv")

    # Verifica a validade da execução de aquecimento.
    if len(validade) != 1:
        raise SystemExit("Erro: quantidade inesperada de configurações.")

    registro = validade[0]

    if (
        registro["versao"] != "aquecimento"
        or registro["repeticao"] != "1"
        or registro["cenario"] != "c"
        or registro["status"] != "valida"
        or registro["motivo"] != "execucao_completa"
    ):
        raise SystemExit(f"Erro: aquecimento inválido: {registro}")

    # Verifica a presença das três categorias de testes.
    categorias = {item["categoria"] for item in metricas}

    if len(metricas) != 3 or categorias != set(TESTES_ESPERADOS):
        raise SystemExit("Erro: categorias de testes inconsistentes.")

    # Verifica a aprovação de todos os testes.
    for item in metricas:
        categoria = item["categoria"]
        quantidade_esperada = TESTES_ESPERADOS[categoria]

        if (
            item["versao"] != "aquecimento"
            or item["execucao"] != registro["execucao"]
            or item["repeticao"] != "1"
            or item["cenario"] != "c"
            or int(item["total"]) != quantidade_esperada
            or int(item["aprovados"]) != quantidade_esperada
            or int(item["falhas"]) != 0
            or int(item["erros"]) != 0
            or int(item["ignorados"]) != 0
        ):
            raise SystemExit(f"Erro: resultados inválidos em {categoria}: {item}")

        print(f"{categoria}: {quantidade_esperada} testes aprovados.")

    print("Aquecimento validado com sucesso.")


if __name__ == "__main__":
    main()
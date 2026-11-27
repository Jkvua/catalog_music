import csv
from pathlib import Path
from statistics import mean, stdev
from zipfile import ZipFile


DADOS = Path(__file__).resolve().parent / "dados"

ARQUIVOS = {
    "baseline": DADOS / "resultados-baseline-44572022429.zip",
    "baseline-complementar": (
        DADOS / "resultados-baseline-complementar-45754270884.zip"
    ),
}

REPETICOES = {
    "baseline": 5,
    "baseline-complementar": 6,
}

CATEGORIAS = {
    "a": ("unitarios",),
    "b": ("unitarios", "integracao"),
    "c": ("unitarios", "integracao", "e2e"),
}


def ler_csv(zip_file, nome):
    caminhos = [
        caminho
        for caminho in zip_file.namelist()
        if Path(caminho).name == nome
    ]

    if len(caminhos) != 1:
        raise ValueError(f"Esperado um arquivo {nome}: {caminhos}")

    conteudo = zip_file.read(caminhos[0]).decode("utf-8-sig")
    return list(csv.DictReader(conteudo.splitlines()))


def chave(registro):
    return int(registro["repeticao"]), registro["cenario"]


def chave_categoria(registro):
    return (*chave(registro), registro["categoria"])


def carregar_dados(versao):
    with ZipFile(ARQUIVOS[versao]) as arquivo:
        cenarios = ler_csv(arquivo, "resumo_cenarios.csv")
        categorias = ler_csv(arquivo, "resumo.csv")
        metricas = ler_csv(arquivo, "metricas_testes.csv")
        validade = ler_csv(arquivo, "validade_execucoes.csv")

        ordem = (
            ler_csv(arquivo, "ordem_execucao.csv")
            if versao == "baseline-complementar"
            else []
        )

    esperadas = {
        (repeticao, cenario)
        for repeticao in range(1, REPETICOES[versao] + 1)
        for cenario in CATEGORIAS
    }

    categorias_esperadas = {
        (repeticao, cenario, categoria)
        for repeticao, cenario in esperadas
        for categoria in CATEGORIAS[cenario]
    }

    for registros in (cenarios, categorias, metricas, validade, ordem):
        if any(registro["versao"] != versao for registro in registros):
            raise ValueError(f"Versão inesperada: {versao}")

    for registros, campo_chave, conjunto in (
        (cenarios, chave, esperadas),
        (validade, chave, esperadas),
        (categorias, chave_categoria, categorias_esperadas),
        (metricas, chave_categoria, categorias_esperadas),
    ):
        if (
            len(registros) != len(conjunto)
            or {campo_chave(r) for r in registros} != conjunto
        ):
            raise ValueError(f"Registros incompletos ou duplicados: {versao}")

    if any(
        r["status"] != "valida"
        or r["motivo"] != "execucao_completa"
        for r in validade
    ):
        raise ValueError(f"Execução inválida: {versao}")

    if any(int(r["codigo_limpeza"]) != 0 for r in cenarios):
        raise ValueError(f"Falha na limpeza: {versao}")

    if any(int(r["codigo_saida"]) != 0 for r in categorias):
        raise ValueError(f"Falha nos testes: {versao}")

    totais = {
        chave(r): float(r["tempo_total_segundos"])
        for r in cenarios
    }

    externos = {
        chave_categoria(r): float(r["tempo_segundos"])
        for r in categorias
    }

    internos = {
        chave_categoria(r): float(r["tempo_pytest_segundos"])
        for r in metricas
    }

    posicoes = {
        chave(r): int(r["posicao"])
        for r in ordem
    }

    if ordem:
        if len(ordem) != len(esperadas) or set(posicoes) != esperadas:
            raise ValueError("Registros de posição inconsistentes")

        for repeticao in range(1, REPETICOES[versao] + 1):
            if {
                posicoes[repeticao, cenario]
                for cenario in CATEGORIAS
            } != {1, 2, 3}:
                raise ValueError("Posições inválidas na repetição")

        for cenario in CATEGORIAS:
            for posicao in (1, 2, 3):
                quantidade = sum(
                    p == posicao
                    for (_, c), p in posicoes.items()
                    if c == cenario
                )

                if quantidade != 2:
                    raise ValueError("Ordem não balanceada")

    return totais, externos, internos, posicoes


def estatisticas(valores):
    return (
        mean(valores),
        stdev(valores),
        min(valores),
        max(valores),
        max(valores) - min(valores),
        stdev(valores) / mean(valores) * 100,
    )


def comparar_configuracoes(dados):
    print("\n1. TEMPO TOTAL POR CONFIGURAÇÃO")
    print(
        "Versão | Configuração | Média | DP | "
        "Mínimo | Máximo | Amplitude | CV (%)"
    )

    for versao, (totais, _, _, _) in dados.items():
        for cenario in CATEGORIAS:
            valores = [
                tempo
                for (_, c), tempo in totais.items()
                if c == cenario
            ]

            resultado = " | ".join(
                f"{valor:.3f}" for valor in estatisticas(valores)
            )

            print(f"{versao} | {cenario.upper()} | {resultado}")


def comparar_primeira_execucao(dados):
    print("\n2. PRIMEIRA EXECUÇÃO DA CONFIGURAÇÃO A")
    print("Versão | Primeira | Média das demais | Diferença")

    for versao, (totais, _, _, _) in dados.items():
        primeira = totais[1, "a"]

        demais = mean(
            totais[r, "a"]
            for r in range(2, REPETICOES[versao] + 1)
        )

        print(
            f"{versao} | {primeira:.3f} | "
            f"{demais:.3f} | {primeira - demais:.3f}"
        )


def comparar_posicoes(dados):
    print("\n3. TEMPO TOTAL POR POSIÇÃO - BASELINE COMPLEMENTAR")
    print("Configuração | Posição | Média")

    totais, _, _, posicoes = dados["baseline-complementar"]

    for cenario in CATEGORIAS:
        for posicao in (1, 2, 3):
            valores = [
                totais[chave_execucao]
                for chave_execucao, p in posicoes.items()
                if chave_execucao[1] == cenario and p == posicao
            ]

            print(
                f"{cenario.upper()} | {posicao} | "
                f"{mean(valores):.3f}"
            )


def comparar_tempos_testes(dados):
    print("\n4. TEMPOS EXTERNOS E INTERNOS DOS TESTES")

    for versao, (_, externos, internos, _) in dados.items():
        print(f"\nVersão: {versao}")
        print(
            "Configuração | Categoria | Média externa | "
            "Média Pytest | Diferença média | DP externo | "
            "DP Pytest | DP diferença"
        )

        for cenario, categorias in CATEGORIAS.items():
            for categoria in categorias:
                chaves = [
                    (r, cenario, categoria)
                    for r in range(1, REPETICOES[versao] + 1)
                ]

                ext = [externos[k] for k in chaves]
                pytest = [internos[k] for k in chaves]
                diferencas = [
                    externos[k] - internos[k] for k in chaves
                ]

                print(
                    f"{cenario.upper()} | {categoria} | "
                    f"{mean(ext):.3f} | {mean(pytest):.3f} | "
                    f"{mean(diferencas):.3f} | "
                    f"{stdev(ext):.3f} | {stdev(pytest):.3f} | "
                    f"{stdev(diferencas):.3f}"
                )

        print("\nTestes unitários da configuração A:")
        print("Repetição | Externo | Pytest | Diferença")

        for r in range(1, REPETICOES[versao] + 1):
            k = (r, "a", "unitarios")

            print(
                f"{r} | {externos[k]:.3f} | "
                f"{internos[k]:.3f} | "
                f"{externos[k] - internos[k]:.3f}"
            )


def main():
    dados = {
        versao: carregar_dados(versao)
        for versao in ARQUIVOS
    }

    comparar_configuracoes(dados)
    comparar_primeira_execucao(dados)
    comparar_posicoes(dados)
    comparar_tempos_testes(dados)


if __name__ == "__main__":
    main()
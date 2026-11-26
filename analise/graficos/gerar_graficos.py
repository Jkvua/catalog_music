import csv
import io
import statistics
import zipfile
from pathlib import Path

import matplotlib.pyplot as plt


# Diretórios
DIRETORIO_ATUAL = Path(__file__).resolve().parent
DIRETORIO_DADOS = DIRETORIO_ATUAL.parent / "dados"

# Arquivos originais do experimento
ARQUIVOS = {
    "baseline": "resultados-baseline-44572022429.zip",
    "d1": "resultados-d1-44577470488.zip",
    "d2": "resultados-d2-44582644797.zip",
    "d3": "resultados-d3-44591994504.zip",
    "d4": "resultados-d4-44606770151.zip",
    "d5": "resultados-d5-44617969552.zip",
}

CONFIGURACOES = ["a", "b", "c"]


def carregar_tempos(versao):
    caminho_zip = DIRETORIO_DADOS / ARQUIVOS[versao]

    with zipfile.ZipFile(caminho_zip, "r") as arquivo_zip:
        caminho_csv = next(
            nome
            for nome in arquivo_zip.namelist()
            if nome.endswith("/resumo_cenarios.csv")
        )

        with arquivo_zip.open(caminho_csv) as arquivo:
            conteudo = io.TextIOWrapper(
                arquivo,
                encoding="utf-8"
            )
            registros = list(csv.DictReader(conteudo))

        # Carregar os registros de validade
        with arquivo_zip.open("validade_execucoes.csv") as arquivo:
            conteudo = io.TextIOWrapper(
                arquivo,
                encoding="utf-8"
            )
            registros_validade = list(csv.DictReader(conteudo))

    # Identificar as execuções válidas
    execucoes_validas = set()

    for registro in registros_validade:
        if registro["status"] == "valida":
            chave = (
                registro["versao"],
                int(registro["repeticao"]),
                registro["cenario"],
            )
            execucoes_validas.add(chave)

    return registros, execucoes_validas

def carregar_tempos_niveis(versao):
    caminho_zip = DIRETORIO_DADOS / ARQUIVOS[versao]

    with zipfile.ZipFile(caminho_zip, "r") as arquivo_zip:

        # Localizar o resumo dos tempos por nível
        caminho_csv = next(
            nome
            for nome in arquivo_zip.namelist()
            if nome.endswith("/resumo.csv")
        )

        with arquivo_zip.open(caminho_csv) as arquivo:
            conteudo = io.TextIOWrapper(
                arquivo,
                encoding="utf-8"
            )
            registros = list(csv.DictReader(conteudo))

        # Carregar os registros de validade
        with arquivo_zip.open("validade_execucoes.csv") as arquivo:
            conteudo = io.TextIOWrapper(
                arquivo,
                encoding="utf-8"
            )
            registros_validade = list(csv.DictReader(conteudo))

    execucoes_validas = set()

    for registro in registros_validade:
        if registro["status"] == "valida":
            chave = (
                registro["versao"],
                int(registro["repeticao"]),
                registro["cenario"],
            )
            execucoes_validas.add(chave)

    return registros, execucoes_validas

def calcular_estatisticas():
    resultados = {}

    for versao in ARQUIVOS:
        registros, execucoes_validas = carregar_tempos(versao)

        resultados[versao] = {}

        for configuracao in CONFIGURACOES:
            tempos = []

            for registro in registros:
                chave = (
                    registro["versao"],
                    int(registro["repeticao"]),
                    registro["cenario"],
                )

                if (
                    registro["versao"] == versao
                    and registro["cenario"] == configuracao
                    and chave in execucoes_validas
                ):
                    tempos.append(
                        (
                            int(registro["repeticao"]),
                            float(registro["tempo_total_segundos"]),
                            int(registro["codigo_limpeza"]),
                        )
                    )

            # Validar a quantidade de repetições
            assert len(tempos) == 5, (
                f"Quantidade inesperada de registros: "
                f"{versao} - {configuracao}"
            )

            # Validar as repetições
            assert sorted(rep for rep, _, _ in tempos) == [
                1, 2, 3, 4, 5
            ], (
                f"Repetições ausentes ou duplicadas: "
                f"{versao} - {configuracao}"
            )

            # Validar a limpeza
            assert all(codigo == 0 for _, _, codigo in tempos), (
                f"Erro na limpeza: {versao} - {configuracao}"
            )

            # Calcular as estatísticas
            valores = [tempo for _, tempo, _ in tempos]

            resultados[versao][configuracao] = {
                "media": statistics.mean(valores),
                "desvio_padrao": statistics.stdev(valores),
            }

    return resultados

def calcular_tempos_agregados(resultados):
    versoes_experimentais = ["d1", "d2", "d3", "d4", "d5"]

    assert all(
        versao in resultados
        for versao in versoes_experimentais
    ), "Existem versões experimentais ausentes."

    resultados_agregados = {}

    for configuracao in CONFIGURACOES:
        medias = [
            resultados[versao][configuracao]["media"]
            for versao in versoes_experimentais
        ]

        resultados_agregados[configuracao] = statistics.mean(medias)

    return resultados_agregados

def calcular_tempos_niveis_baseline():
    versao = "baseline"

    registros, execucoes_validas = carregar_tempos_niveis(versao)

    categorias_esperadas = {
        "a": ["unitarios"],
        "b": ["unitarios", "integracao"],
        "c": ["unitarios", "integracao", "e2e"],
    }

    resultados = {}

    for configuracao, categorias in categorias_esperadas.items():
        resultados[configuracao] = {}

        for categoria in categorias:
            tempos = []

            for registro in registros:
                chave = (
                    registro["versao"],
                    int(registro["repeticao"]),
                    registro["cenario"],
                )

                if (
                    registro["versao"] == versao
                    and registro["cenario"] == configuracao
                    and registro["categoria"] == categoria
                    and chave in execucoes_validas
                ):
                    tempos.append(
                        (
                            int(registro["repeticao"]),
                            float(registro["tempo_segundos"]),
                            int(registro["codigo_saida"]),
                        )
                    )

            # Validar a quantidade de registros
            assert len(tempos) == 5, (
                f"Quantidade inesperada: "
                f"{configuracao} - {categoria}"
            )

            # Validar as repetições
            assert sorted(rep for rep, _, _ in tempos) == [
                1, 2, 3, 4, 5
            ], (
                f"Repetições inválidas: "
                f"{configuracao} - {categoria}"
            )

            # Códigos 0 e 1 são esperados
            assert all(codigo in (0, 1) for _, _, codigo in tempos), (
                f"Código de saída inesperado: "
                f"{configuracao} - {categoria}"
            )

            valores = [tempo for _, tempo, _ in tempos]

            resultados[configuracao][categoria] = {
                "media": statistics.mean(valores),
                "desvio_padrao": statistics.stdev(valores),
            }

    return resultados

def gerar_f1(resultados):
    versoes = list(ARQUIVOS.keys())

    medias_a = [
        resultados[versao]["a"]["media"]
        for versao in versoes
    ]

    medias_b = [
        resultados[versao]["b"]["media"]
        for versao in versoes
    ]

    medias_c = [
        resultados[versao]["c"]["media"]
        for versao in versoes
    ]

    posicoes = list(range(len(versoes)))
    largura = 0.25

    fig, ax = plt.subplots(figsize=(11, 6))

    ax.bar(
        [x - largura for x in posicoes],
        medias_a,
        largura,
        label="Configuração A",
    )

    ax.bar(
        posicoes,
        medias_b,
        largura,
        label="Configuração B",
    )

    ax.bar(
        [x + largura for x in posicoes],
        medias_c,
        largura,
        label="Configuração C",
    )

    ax.set_xlabel("Versão experimental")
    ax.set_ylabel("Tempo operacional médio (s)")

    ax.set_xticks(posicoes)
    ax.set_xticklabels(
        [versao.upper() for versao in versoes]
    )

    ax.legend()
    ax.grid(axis="y", linestyle="--", alpha=0.3)
    ax.set_axisbelow(True)

    fig.tight_layout()

    caminho_png = DIRETORIO_ATUAL / "F1_tempo_operacional.png"
    caminho_pdf = DIRETORIO_ATUAL / "F1_tempo_operacional.pdf"

    fig.savefig(caminho_png, dpi=300, bbox_inches="tight")
    fig.savefig(caminho_pdf, bbox_inches="tight")

    plt.close(fig)

    print(f"Gráfico PNG gerado: {caminho_png}")
    print(f"Gráfico PDF gerado: {caminho_pdf}")

def gerar_f2(resultados):
    configuracoes = ["a", "b", "c"]

    categorias = [
        ("unitarios", "Unitários", "#4C78A8"),
        ("integracao", "Integração", "#F58518"),
        ("e2e", "E2E", "#54A24B"),
    ]

    posicoes = range(len(configuracoes))

    fig, ax = plt.subplots(figsize=(9, 6))

    bases = [0.0] * len(configuracoes)

    for categoria, rotulo, cor in categorias:
        valores = [
            resultados[configuracao]
            .get(categoria, {})
            .get("media", 0.0)
            for configuracao in configuracoes
        ]

        ax.bar(
            posicoes,
            valores,
            bottom=bases,
            label=rotulo,
            color=cor,
            width=0.55,
        )

        bases = [
            base + valor
            for base, valor in zip(bases, valores)
        ]

    ax.set_xticks(list(posicoes))
    ax.set_xticklabels(["A", "B", "C"])

    ax.set_xlabel("Configuração experimental")
    ax.set_ylabel("Tempo médio de execução dos testes (s)")

    ax.set_title(
        "Composição do tempo médio por nível de teste — baseline"
    )

    ax.legend(title="Nível de teste")

    ax.grid(
        axis="y",
        linestyle="--",
        alpha=0.3
    )

    ax.set_axisbelow(True)

    # Apresentar o tempo conjunto acima de cada barra
    for posicao, total in enumerate(bases):
        ax.text(
            posicao,
            total + 0.6,
            f"{total:.2f}",
            ha="center",
            va="bottom",
            fontsize=10,
        )

    ax.set_ylim(0, max(bases) * 1.15)

    fig.tight_layout()

    caminho_png = DIRETORIO_ATUAL / "F2_composicao_tempos.png"
    caminho_pdf = DIRETORIO_ATUAL / "F2_composicao_tempos.pdf"

    fig.savefig(caminho_png, dpi=300, bbox_inches="tight")
    fig.savefig(caminho_pdf, bbox_inches="tight")

    plt.close(fig)

    print(f"Gráfico PNG gerado: {caminho_png}")
    print(f"Gráfico PDF gerado: {caminho_pdf}")

def carregar_taxas_deteccao():
    caminho_csv = (
        DIRETORIO_ATUAL.parent
        / "resultados"
        / "resumo_deteccao.csv"
    )

    with caminho_csv.open(
        newline="",
        encoding="utf-8",
    ) as arquivo:
        registros = list(csv.DictReader(arquivo))

    configuracoes_encontradas = [
        registro["configuracao"]
        for registro in registros
    ]

    assert sorted(configuracoes_encontradas) == sorted(
        CONFIGURACOES
    ), "Configurações ausentes, duplicadas ou inesperadas."

    taxas_deteccao = {}

    for registro in registros:
        configuracao = registro["configuracao"]

        introduzidos = int(
            registro["defeitos_introduzidos"]
        )

        detectados = int(
            registro["defeitos_detectados"]
        )

        nao_detectados = int(
            registro["defeitos_nao_detectados"]
        )

        taxa = float(registro["taxa_deteccao"])

        assert introduzidos == len(ARQUIVOS) - 1, (
            "Quantidade inesperada de defeitos."
        )

        assert 0 <= detectados <= introduzidos, (
            "Quantidade inválida de defeitos detectados."
        )

        assert detectados + nao_detectados == introduzidos, (
            "Contagens de defeitos inconsistentes."
        )

        taxa_esperada = detectados / introduzidos * 100

        assert abs(taxa - taxa_esperada) < 1e-9, (
            "Taxa de detecção inconsistente."
        )

        taxas_deteccao[configuracao] = taxa

    return taxas_deteccao

def gerar_f4(tempos_agregados, taxas_deteccao):

    fig, ax = plt.subplots(figsize=(9, 6))

    for configuracao in CONFIGURACOES:
        tempo = tempos_agregados[configuracao]
        taxa = taxas_deteccao[configuracao]

        ax.scatter(
            tempo,
            taxa,
            s=100,
            zorder=3,
        )

        ax.annotate(
            f"Configuração {configuracao.upper()}",
            (tempo, taxa),
            xytext=(0, 12),
            textcoords="offset points",
            ha="center",
            fontsize=10,
        )

    ax.set_xlabel("Tempo total médio por configuração (s)")
    ax.set_ylabel("Taxa de detecção de defeitos (%)")

    ax.set_xlim(0, 50)
    ax.set_ylim(0, 100)

    ax.set_xticks(range(0, 51, 5))
    ax.set_yticks(range(0, 101, 20))

    ax.grid(
        linestyle="--",
        alpha=0.3,
    )

    ax.set_axisbelow(True)

    fig.tight_layout()

    caminho_png = DIRETORIO_ATUAL / "F4_custo_deteccao.png"
    caminho_pdf = DIRETORIO_ATUAL / "F4_custo_deteccao.pdf"

    fig.savefig(caminho_png, dpi=300, bbox_inches="tight")
    fig.savefig(caminho_pdf, bbox_inches="tight")

    plt.close(fig)

    print(f"Gráfico PNG gerado: {caminho_png}")
    print(f"Gráfico PDF gerado: {caminho_pdf}")

if __name__ == "__main__":
    # F1 — Tempo total médio por configuração
    resultados = calcular_estatisticas()
    gerar_f1(resultados)

    # F2 — Composição do tempo por nível
    resultados_niveis = calcular_tempos_niveis_baseline()

    print("\n--- TEMPOS POR NÍVEL: BASELINE ---")

    for configuracao, categorias in resultados_niveis.items():
        print(f"\nConfiguração {configuracao.upper()}")

        for categoria, estatisticas in categorias.items():
            print(
                f"  {categoria}: "
                f"média = {estatisticas['media']:.3f} s | "
                f"DP = {estatisticas['desvio_padrao']:.3f} s"
            )

    gerar_f2(resultados_niveis)

    # F4 — Relação entre custo de execução e detecção
    tempos_agregados = calcular_tempos_agregados(resultados)
    taxas_deteccao = carregar_taxas_deteccao()

    print("\n--- RESULTADOS CONSOLIDADOS PARA O F4 ---")

    for configuracao in CONFIGURACOES:
        tempo = tempos_agregados[configuracao]
        taxa = taxas_deteccao[configuracao]

        print(
            f"Configuração {configuracao.upper()}: "
            f"tempo = {tempo:.3f} s | "
            f"detecção = {taxa:.2f}%"
        )

    gerar_f4(tempos_agregados, taxas_deteccao)
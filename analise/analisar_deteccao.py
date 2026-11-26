import csv
import io
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path


DIRETORIO_DADOS = Path(__file__).resolve().parent / "dados"

VERSOES = ["baseline", "d1", "d2", "d3", "d4", "d5"]

CONFIGURACOES = {
    "a": ["unitarios"],
    "b": ["unitarios", "integracao"],
    "c": ["unitarios", "integracao", "e2e"],
}

QUANTIDADE_TESTES = {
    "unitarios": 221,
    "integracao": 115,
    "e2e": 6,
}

REPETICOES = range(1, 6)


def ler_csv(arquivo_zip, nome):
    with arquivo_zip.open(nome) as arquivo:
        conteudo = io.TextIOWrapper(arquivo, encoding="utf-8-sig")
        return list(csv.DictReader(conteudo))


def chave_execucao(registro):
    return (
        registro["versao"],
        registro["execucao"],
        int(registro["repeticao"]),
        registro["cenario"],
    )


def carregar_dados(versao):
    arquivos = list(
        DIRETORIO_DADOS.glob(f"resultados-{versao}-*.zip")
    )

    if len(arquivos) != 1:
        raise ValueError(
            f"Esperado um arquivo ZIP para {versao}. "
            f"Encontrados: {len(arquivos)}"
        )

    with zipfile.ZipFile(arquivos[0]) as arquivo_zip:
        metricas = ler_csv(arquivo_zip, "metricas_testes.csv")
        validade = ler_csv(arquivo_zip, "validade_execucoes.csv")

    chaves_validade = [chave_execucao(r) for r in validade]

    if len(chaves_validade) != len(set(chaves_validade)):
        raise ValueError(f"{versao}: registros de validade duplicados.")

    execucoes_validas = {
        chave_execucao(registro)
        for registro in validade
        if registro["status"] == "valida"
    }

    metricas_validas = [
        registro
        for registro in metricas
        if chave_execucao(registro) in execucoes_validas
    ]

    return metricas_validas, execucoes_validas


def validar_dados(versao, metricas, execucoes_validas):
    esperadas = {
        (repeticao, cenario)
        for repeticao in REPETICOES
        for cenario in CONFIGURACOES
    }

    encontradas = {
        (repeticao, cenario)
        for v, execucao, repeticao, cenario in execucoes_validas
        if v == versao
    }

    if encontradas != esperadas or len(execucoes_validas) != 15:
        raise ValueError(
            f"{versao}: conjunto de execuções válidas incorreto."
        )

    for chave in execucoes_validas:
        _, _, repeticao, cenario = chave

        registros = [
            registro
            for registro in metricas
            if chave_execucao(registro) == chave
        ]

        categorias = [
            registro["categoria"]
            for registro in registros
        ]

        if sorted(categorias) != sorted(CONFIGURACOES[cenario]):
            raise ValueError(
                f"{versao}, repetição {repeticao}, "
                f"configuração {cenario}: categorias incorretas."
            )

        for registro in registros:
            categoria = registro["categoria"]

            total = int(registro["total"])
            aprovados = int(registro["aprovados"])
            falhas = int(registro["falhas"])
            erros = int(registro["erros"])
            ignorados = int(registro["ignorados"])

            if min(total, aprovados, falhas, erros, ignorados) < 0:
                raise ValueError(f"Contagem negativa: {registro}")

            if total != QUANTIDADE_TESTES[categoria]:
                raise ValueError(
                    f"Quantidade inesperada de testes: {registro}"
                )

            if total != aprovados + falhas + erros + ignorados:
                raise ValueError(
                    f"Contagens inconsistentes: {registro}"
                )

            if erros != 0 or ignorados != 0:
                raise ValueError(
                    f"Execução com erros ou testes ignorados: {registro}"
                )

            if versao == "baseline" and falhas != 0:
                raise ValueError(
                    f"Falha encontrada na baseline: {registro}"
                )


def analisar_deteccao(versao, metricas):
    print("\n" + "=" * 70)
    print(f"VERSÃO: {versao.upper()}")
    print("=" * 70)

    resultado = {}

    for cenario, categorias in CONFIGURACOES.items():
        print(f"\nConfiguração {cenario.upper()}")

        niveis_detectores = []
        repeticoes_com_deteccao = set()

        for categoria in categorias:
            registros = sorted(
                [
                    registro
                    for registro in metricas
                    if registro["cenario"] == cenario
                    and registro["categoria"] == categoria
                ],
                key=lambda registro: int(registro["repeticao"]),
            )

            falhas = [
                int(registro["falhas"])
                for registro in registros
            ]

            repeticoes_com_falhas = sum(
                quantidade > 0
                for quantidade in falhas
            )

            for registro in registros:
                if int(registro["falhas"]) > 0:
                    repeticoes_com_deteccao.add(
                        int(registro["repeticao"])
                    )

            print(f"  Categoria: {categoria}")
            print(f"    Falhas por repetição: {falhas}")
            print(
                f"    Repetições com falhas: "
                f"{repeticoes_com_falhas}/5"
            )

            if repeticoes_com_falhas > 0:
                niveis_detectores.append(categoria)

        detectado = bool(niveis_detectores)

        resultado[cenario] = {
            "detectado": detectado,
            "niveis": niveis_detectores,
            "repeticoes_com_deteccao": len(
                repeticoes_com_deteccao
            ),
        }

        print(f"  Detecção: {'SIM' if detectado else 'NÃO'}")
        print(
            f"  Repetições com detecção: "
            f"{len(repeticoes_com_deteccao)}/5"
        )

    return resultado


def apresentar_resumo(resultados):
    print("\n" + "=" * 70)
    print("MATRIZ DE DETECÇÃO DE DEFEITOS")
    print("=" * 70)

    print(f"{'Versão':<12} {'A':<25} {'B':<25} {'C':<25}")

    for versao in VERSOES:
        valores = []

        for cenario in CONFIGURACOES:
            niveis = resultados[versao][cenario]["niveis"]

            valores.append(
                " + ".join(niveis)
                if niveis
                else "Não detectado"
            )

        print(
            f"{versao.upper():<12} "
            f"{valores[0]:<25} "
            f"{valores[1]:<25} "
            f"{valores[2]:<25}"
        )

    print("\n" + "=" * 70)
    print("TAXA DE DETECÇÃO POR CONFIGURAÇÃO")
    print("=" * 70)

    defeitos = [
        versao
        for versao in VERSOES
        if versao != "baseline"
    ]

    resumo = []

    for cenario in CONFIGURACOES:
        detectados = sum(
            resultados[versao][cenario]["detectado"]
            for versao in defeitos
        )

        nao_detectados = len(defeitos) - detectados
        taxa = detectados / len(defeitos) * 100

        print(f"\nConfiguração {cenario.upper()}")
        print(f"  Defeitos introduzidos: {len(defeitos)}")
        print(f"  Defeitos detectados: {detectados}")
        print(f"  Defeitos não detectados: {nao_detectados}")
        print(f"  Taxa de detecção: {taxa:.2f}%")

        resumo.append({
            "configuracao": cenario,
            "defeitos_introduzidos": len(defeitos),
            "defeitos_detectados": detectados,
            "defeitos_nao_detectados": nao_detectados,
            "taxa_deteccao": taxa,
        })

    return resumo

def identificar_testes_com_falhas(
    versao, metricas, execucoes_validas
):
    arquivo = next(
        DIRETORIO_DADOS.glob(f"resultados-{versao}-*.zip")
    )

    resultados = {}

    with zipfile.ZipFile(arquivo) as arquivo_zip:
        for registro in metricas:
            if chave_execucao(registro) not in execucoes_validas:
                continue

            execucao = registro["execucao"]
            repeticao = int(registro["repeticao"])
            cenario = registro["cenario"]
            categoria = registro["categoria"]

            caminho_xml = (
                f"{versao}/{execucao}/"
                f"repeticao_{repeticao}/"
                f"cenario_{cenario}/{categoria}.xml"
            )

            with arquivo_zip.open(caminho_xml) as xml:
                raiz = ET.parse(xml).getroot()

            quantidade_falhas = 0

            for teste in raiz.iter("testcase"):
                falha = teste.find("failure")

                if falha is None:
                    continue

                quantidade_falhas += 1

                classe = teste.get("classname", "")
                nome = teste.get("name", "")
                mensagem = falha.get("message", "")

                chave = (
                    cenario,
                    categoria,
                    classe,
                    nome,
                )

                if chave not in resultados:
                    resultados[chave] = {
                        "repeticoes": set(),
                        "mensagens": set(),
                    }

                resultados[chave]["repeticoes"].add(
                    repeticao
                )

                resultados[chave]["mensagens"].add(
                    mensagem
                )

            if quantidade_falhas != int(registro["falhas"]):
                raise ValueError(
                    f"Divergência entre XML e CSV: {caminho_xml}"
                )

    print("\n" + "-" * 70)
    print(f"CASOS DE TESTE COM FALHAS — {versao.upper()}")
    print("-" * 70)

    if not resultados:
        print("Nenhum caso de teste apresentou falhas.")
        return

    for chave, dados in sorted(resultados.items()):
        cenario, categoria, classe, nome = chave

        repeticoes = sorted(dados["repeticoes"])

        print(f"\nConfiguração: {cenario.upper()}")
        print(f"Categoria: {categoria}")
        print(f"Teste: {classe}::{nome}")
        print(f"Repetições com falha: {repeticoes}")
        print(f"Consistência: {len(repeticoes)}/5")

        for mensagem in sorted(dados["mensagens"]):
            print(f"Mensagem: {mensagem}")

def exportar_resumo_deteccao(resumo):
    diretorio_resultados = (
        Path(__file__).resolve().parent / "resultados"
    )

    diretorio_resultados.mkdir(
        parents=True,
        exist_ok=True,
    )

    caminho_csv = (
        diretorio_resultados / "resumo_deteccao.csv"
    )

    campos = [
        "configuracao",
        "defeitos_introduzidos",
        "defeitos_detectados",
        "defeitos_nao_detectados",
        "taxa_deteccao",
    ]

    with caminho_csv.open(
        "w",
        newline="",
        encoding="utf-8",
    ) as arquivo:
        escritor = csv.DictWriter(
            arquivo,
            fieldnames=campos,
        )

        escritor.writeheader()
        escritor.writerows(resumo)

    print(f"\nResumo de detecção exportado: {caminho_csv}")

def executar_analises():
    resultados = {}

    for versao in VERSOES:
        metricas, execucoes_validas = carregar_dados(versao)

        validar_dados(
            versao,
            metricas,
            execucoes_validas,
        )

        resultados[versao] = analisar_deteccao(
            versao,
            metricas,
        )

        identificar_testes_com_falhas(
            versao,
            metricas,
            execucoes_validas,
        )

    resumo = apresentar_resumo(resultados)
    exportar_resumo_deteccao(resumo)

if __name__ == "__main__":
    executar_analises()
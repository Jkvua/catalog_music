import csv
import xml.etree.ElementTree as ET
from pathlib import Path

RAIZ_PROJETO = Path(__file__).resolve().parent.parent
RESULTADOS = RAIZ_PROJETO / "resultados"

campos = [
    "versao",
    "execucao",
    "repeticao",
    "cenario",
    "categoria",
    "total",
    "aprovados",
    "falhas",
    "erros",
    "ignorados",
    "tempo_pytest_segundos",
]

registros = []

# Percorre as versões e execuções experimentais
for arquivo_xml in sorted(
    RESULTADOS.glob("*/*/repeticao_*/cenario_*/*.xml")
):
    suite = ET.parse(arquivo_xml).getroot().find("testsuite")

    if suite is None:
        raise ValueError(f"Relatório XML inválido: {arquivo_xml}")

    total = int(suite.get("tests", 0))
    falhas = int(suite.get("failures", 0))
    erros = int(suite.get("errors", 0))
    ignorados = int(suite.get("skipped", 0))
    tempo = float(suite.get("time", 0))

    registros.append({
        "versao": arquivo_xml.parents[3].name,
        "execucao": arquivo_xml.parents[2].name,
        "repeticao": arquivo_xml.parents[1].name,
        "cenario": arquivo_xml.parent.name,
        "categoria": arquivo_xml.stem,
        "total": total,
        "aprovados": total - falhas - erros - ignorados,
        "falhas": falhas,
        "erros": erros,
        "ignorados": ignorados,
        "tempo_pytest_segundos": tempo,
    })

if not registros:
    raise SystemExit("Nenhum relatório XML encontrado na nova estrutura.")

ARQUIVO_SAIDA = RESULTADOS / "metricas_testes.csv"

with ARQUIVO_SAIDA.open("w", newline="", encoding="utf-8") as arquivo:
    escritor = csv.DictWriter(arquivo, fieldnames=campos)
    escritor.writeheader()
    escritor.writerows(registros)

print(f"Métricas extraídas de {len(registros)} relatórios.")
print(f"Arquivo gerado: {ARQUIVO_SAIDA}")
#!/usr/bin/env bash

set -Eeuo pipefail

# Executa os comandos a partir da raiz do projeto
cd "$(dirname "$0")/.."

JUNIT_XML="${JUNIT_XML:-}"
E2E_STATUS_FILE="${E2E_STATUS_FILE:-}"

# Registra o resultado de uma etapa operacional
registrar_etapa() {
    local etapa="$1"
    local resultado="$2"

    if [[ -n "$E2E_STATUS_FILE" ]]; then
        printf '%s,%s\n' "$etapa" "$resultado" >> "$E2E_STATUS_FILE"
    fi
}

# Inicializa o arquivo de registro, quando solicitado
if [[ -n "$E2E_STATUS_FILE" ]]; then
    printf 'etapa,codigo_saida\n' > "$E2E_STATUS_FILE"
fi

# Remove o ambiente E2E ao finalizar
cleanup() {
    local resultado_original=$?
    local codigo_limpeza=0

    trap - EXIT

    if [[ "$resultado_original" -ne 0 ]]; then
        echo "Falha durante a execução E2E. Exibindo logs..."
        docker compose --profile test logs --tail=100 web-test db-e2e || true
    fi

    echo "Removendo ambiente E2E..."

    docker compose --profile test rm -sf web-test db-e2e \
        || codigo_limpeza=$?

    registrar_etapa "limpeza" "$codigo_limpeza"

    # Preserva a falha original; se não houve falha anterior,
    # considera o resultado da limpeza.
    if [[ "$resultado_original" -ne 0 ]]; then
        exit "$resultado_original"
    fi

    exit "$codigo_limpeza"
}

trap cleanup EXIT

echo "Inicializando ambiente E2E..."

# Remove contêineres anteriores
codigo_preparacao=0

docker compose --profile test rm -sf web-test db-e2e \
    || codigo_preparacao=$?

# Inicializa os serviços apenas se a remoção inicial funcionou
if [[ "$codigo_preparacao" -eq 0 ]]; then
    docker compose --profile test up -d --wait --no-build db-e2e web-test \
        || codigo_preparacao=$?
fi

registrar_etapa "preparacao" "$codigo_preparacao"

# Interrompe caso a preparação tenha falhado
if [[ "$codigo_preparacao" -ne 0 ]]; then
    echo "Erro: não foi possível preparar o ambiente E2E."
    exit "$codigo_preparacao"
fi

echo "Executando testes E2E..."

codigo_pytest=0

if [[ -n "$JUNIT_XML" ]]; then
    docker compose --profile test run --rm \
        --no-deps \
        -e API_URL=http://web-test:5000 \
        tests python -m pytest tests/e2e \
        -v --tb=short \
        --junitxml="$JUNIT_XML" \
        || codigo_pytest=$?
else
    docker compose --profile test run --rm \
        --no-deps \
        -e API_URL=http://web-test:5000 \
        tests python -m pytest tests/e2e \
        -v --tb=short \
        || codigo_pytest=$?
fi

registrar_etapa "pytest" "$codigo_pytest"

exit "$codigo_pytest"
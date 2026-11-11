#!/usr/bin/env bash

set -Eeuo pipefail

# Executa os comandos a partir da raiz do projeto
cd "$(dirname "$0")/.."

# Remove o ambiente E2E ao finalizar, inclusive em caso de falha
cleanup() {
    local resultado=$?

    if [ "$resultado" -ne 0 ]; then
	echo "Falha na execução do E2E. Exibindo logs..."
	docker compose --profile test logs --tail=100 web-test db-e2e || true
    
    fi

    echo  "Removendo ambiente e2e..."
    docker compose --profile test rm -sf web-test db-e2e || true

    return 0
}

trap cleanup EXIT

echo "Inicializando ambiente E2E..."

# Garante que a execução comece com contêineres novos
docker compose --profile test rm -sf web-test db-e2e

# Inicializa o PostgreSQL e a API Flask
docker compose --profile test up -d --wait --no-build db-e2e web-test

echo "Executando testes E2E..."

# Executa o pytest contra a API Flask
docker compose --profile test run --rm \
    --no-deps \
    -e API_URL=http://web-test:5000 \
    tests python -m pytest tests/e2e -v --tb=short

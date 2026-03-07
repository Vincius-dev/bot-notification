#!/bin/sh
# =============================================================================
# dev.sh — Utilitários de desenvolvimento
# =============================================================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_menu() {
    printf "\n${CYAN}========================================${NC}\n"
    printf "${CYAN}   Bot Notification — Dev Utils${NC}\n"
    printf "${CYAN}========================================${NC}\n"
    printf "  ${YELLOW}1.${NC} Criar ambiente virtual e instalar dependências\n"
    printf "  ${YELLOW}2.${NC} Subir MongoDB local (Docker)\n"
    printf "  ${YELLOW}3.${NC} Criar coleções e índices no banco local\n"
    printf "  ${YELLOW}4.${NC} Executar testes\n"
    printf "  ${YELLOW}5.${NC} Subir aplicação completa (Docker Compose)\n"
    printf "  ${YELLOW}6.${NC} Derrubar containers\n"
    printf "  ${YELLOW}7.${NC} Construir imagem Docker de produção\n"
    printf "  ${YELLOW}0.${NC} Sair\n"
    printf "${CYAN}========================================${NC}\n"
    printf "Escolha uma opção: "
}

cmd_venv() {
    printf "${GREEN}>> Criando ambiente virtual...${NC}\n"
    python3 -m venv venv
    . venv/bin/activate
    printf "${GREEN}>> Instalando dependências...${NC}\n"
    pip install -r requirements.txt
    printf "${GREEN}>> Pronto! Ative o venv com: source venv/bin/activate${NC}\n"
}

cmd_mongo_up() {
    printf "${GREEN}>> Subindo MongoDB local...${NC}\n"
    docker compose up mongo -d
    printf "${GREEN}>> MongoDB disponível em localhost:27017${NC}\n"
}

cmd_seed() {
    printf "${GREEN}>> Criando coleções e índices no banco local...${NC}\n"
    python3 scripts/seed_dev_db.py
}

cmd_tests() {
    printf "${GREEN}>> Executando testes...${NC}\n"
    pytest
}

cmd_compose_up() {
    printf "${GREEN}>> Criando volume de assets (se não existir)...${NC}\n"
    docker volume create assets_dev
    printf "${GREEN}>> Subindo aplicação completa via Docker Compose...${NC}\n"
    docker compose up -d
    printf "${GREEN}>> Containers rodando. Acompanhe com: docker attach bot-notification-app${NC}\n"
}

cmd_compose_down() {
    printf "${YELLOW}>> Derrubando containers...${NC}\n"
    docker compose down
}

cmd_build_prod() {
    printf "Informe a versão da imagem (ex: 1.0.0): "
    read -r versao
    if [ -z "$versao" ]; then
        printf "${RED}Versão não informada. Operação cancelada.${NC}\n"
        return
    fi
    printf "${GREEN}>> Construindo imagem bot-notif:${versao}...${NC}\n"
    docker build -t "bot-notif:${versao}" .
    printf "${GREEN}>> Imagem criada: bot-notif:${versao}${NC}\n"
}

# Loop principal
while true; do
    print_menu
    read -r opcao
    case "$opcao" in
        1) cmd_venv ;;
        2) cmd_mongo_up ;;
        3) cmd_seed ;;
        4) cmd_tests ;;
        5) cmd_compose_up ;;
        6) cmd_compose_down ;;
        7) cmd_build_prod ;;
        0)
            printf "${CYAN}Saindo...${NC}\n"
            exit 0
            ;;
        *)
            printf "${RED}Opção inválida.${NC}\n"
            ;;
    esac
done

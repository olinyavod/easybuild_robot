#!/bin/bash
# Скрипт для управления сервисом EasyBuild Bot

SERVICE_NAME="easybuild_bot_py.service"
SERVICE_FILE="/home/olinyavod/projects/easybuild_bot/python/easybuild_bot_py.service"
SYSTEMD_PATH="/etc/systemd/system/$SERVICE_NAME"

# Цвета для вывода
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

function show_help() {
    echo -e "${BLUE}Использование: ./service.sh [команда]${NC}"
    echo ""
    echo "Доступные команды:"
    echo "  install   - Установить сервис в systemd и запустить"
    echo "  start     - Запустить сервис"
    echo "  stop      - Остановить сервис"
    echo "  restart   - Перезапустить сервис"
    echo "  status    - Показать статус сервиса"
    echo "  logs      - Показать последние 50 строк логов"
    echo "  follow    - Показать логи в реальном времени"
    echo "  enable    - Включить автозапуск при загрузке системы"
    echo "  disable   - Отключить автозапуск"
    echo "  uninstall - Остановить и удалить сервис"
    echo ""
}

function install_service() {
    echo -e "${YELLOW}📦 Установка сервиса...${NC}"
    
    # Проверка наличия файла сервиса
    if [ ! -f "$SERVICE_FILE" ]; then
        echo -e "${RED}❌ Ошибка: файл $SERVICE_FILE не найден${NC}"
        exit 1
    fi
    
    # Проверка наличия .env файла
    if [ ! -f "/home/olinyavod/projects/easybuild_bot/python/.env" ]; then
        echo -e "${RED}❌ Ошибка: файл .env не найден${NC}"
        echo "Создайте файл .env с переменной BOT_TOKEN"
        exit 1
    fi
    
    # Проверка виртуального окружения
    if [ ! -d "/home/olinyavod/projects/easybuild_bot/python/.venv" ]; then
        echo -e "${RED}❌ Ошибка: виртуальное окружение .venv не найдено${NC}"
        exit 1
    fi
    
    # Копирование файла сервиса
    echo "Копирование файла сервиса в systemd..."
    sudo cp "$SERVICE_FILE" "$SYSTEMD_PATH"
    
    # Перезагрузка конфигурации systemd
    echo "Перезагрузка конфигурации systemd..."
    sudo systemctl daemon-reload
    
    # Включение автозапуска
    echo "Включение автозапуска..."
    sudo systemctl enable "$SERVICE_NAME"
    
    # Запуск сервиса
    echo "Запуск сервиса..."
    sudo systemctl start "$SERVICE_NAME"
    
    # Проверка статуса
    sleep 2
    if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
        echo -e "${GREEN}✅ Сервис успешно установлен и запущен!${NC}"
        echo ""
        sudo systemctl status "$SERVICE_NAME" --no-pager -l
    else
        echo -e "${RED}❌ Ошибка при запуске сервиса${NC}"
        echo "Проверьте логи: sudo journalctl -u $SERVICE_NAME -n 50"
        exit 1
    fi
}

function start_service() {
    echo -e "${YELLOW}▶️  Запуск сервиса...${NC}"
    sudo systemctl start "$SERVICE_NAME"
    sleep 1
    if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
        echo -e "${GREEN}✅ Сервис запущен${NC}"
    else
        echo -e "${RED}❌ Ошибка при запуске сервиса${NC}"
        exit 1
    fi
}

function stop_service() {
    echo -e "${YELLOW}⏸️  Остановка сервиса...${NC}"
    sudo systemctl stop "$SERVICE_NAME"
    sleep 1
    if ! sudo systemctl is-active --quiet "$SERVICE_NAME"; then
        echo -e "${GREEN}✅ Сервис остановлен${NC}"
    else
        echo -e "${RED}❌ Ошибка при остановке сервиса${NC}"
        exit 1
    fi
}

function restart_service() {
    echo -e "${YELLOW}🔄 Перезапуск сервиса...${NC}"
    sudo systemctl restart "$SERVICE_NAME"
    sleep 1
    if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
        echo -e "${GREEN}✅ Сервис перезапущен${NC}"
    else
        echo -e "${RED}❌ Ошибка при перезапуске сервиса${NC}"
        exit 1
    fi
}

function status_service() {
    sudo systemctl status "$SERVICE_NAME" --no-pager -l
}

function logs_service() {
    echo -e "${BLUE}📜 Последние 50 строк логов:${NC}"
    sudo journalctl -u "$SERVICE_NAME" -n 50 --no-pager
}

function follow_logs() {
    echo -e "${BLUE}📜 Логи в реальном времени (Ctrl+C для выхода):${NC}"
    sudo journalctl -u "$SERVICE_NAME" -f
}

function enable_service() {
    echo -e "${YELLOW}🔧 Включение автозапуска...${NC}"
    sudo systemctl enable "$SERVICE_NAME"
    echo -e "${GREEN}✅ Автозапуск включен${NC}"
}

function disable_service() {
    echo -e "${YELLOW}🔧 Отключение автозапуска...${NC}"
    sudo systemctl disable "$SERVICE_NAME"
    echo -e "${GREEN}✅ Автозапуск отключен${NC}"
}

function uninstall_service() {
    echo -e "${YELLOW}🗑️  Удаление сервиса...${NC}"
    
    # Остановка сервиса
    if sudo systemctl is-active --quiet "$SERVICE_NAME"; then
        echo "Остановка сервиса..."
        sudo systemctl stop "$SERVICE_NAME"
    fi
    
    # Отключение автозапуска
    if sudo systemctl is-enabled --quiet "$SERVICE_NAME"; then
        echo "Отключение автозапуска..."
        sudo systemctl disable "$SERVICE_NAME"
    fi
    
    # Удаление файла сервиса
    if [ -f "$SYSTEMD_PATH" ]; then
        echo "Удаление файла сервиса..."
        sudo rm "$SYSTEMD_PATH"
    fi
    
    # Перезагрузка конфигурации systemd
    echo "Перезагрузка конфигурации systemd..."
    sudo systemctl daemon-reload
    
    echo -e "${GREEN}✅ Сервис удален${NC}"
}

# Главная логика
case "${1:-}" in
    install)
        install_service
        ;;
    start)
        start_service
        ;;
    stop)
        stop_service
        ;;
    restart)
        restart_service
        ;;
    status)
        status_service
        ;;
    logs)
        logs_service
        ;;
    follow)
        follow_logs
        ;;
    enable)
        enable_service
        ;;
    disable)
        disable_service
        ;;
    uninstall)
        uninstall_service
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}❌ Неизвестная команда: ${1:-}${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac


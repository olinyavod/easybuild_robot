#!/bin/bash
# Проверка структуры конфигурации линтеров

echo "🔍 Проверка конфигурации линтеров..."
echo ""

# Цвета
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

check_file() {
    if [ -f "$1" ]; then
        echo -e "${GREEN}✅${NC} $1"
    else
        echo -e "${RED}❌${NC} $1 - отсутствует"
    fi
}

check_executable() {
    if [ -x "$1" ]; then
        echo -e "${GREEN}✅${NC} $1 (исполняемый)"
    else
        echo -e "${YELLOW}⚠️${NC} $1 - не исполняемый"
    fi
}

echo "📁 Конфигурационные файлы:"
echo "─────────────────────────────────"
check_file "python/pyproject.toml"
check_file "dart/analysis_options.yaml"
check_file ".pre-commit-config.yaml"
check_file ".editorconfig"
check_file ".gitignore"

echo ""
echo "🔧 Вспомогательные файлы:"
echo "─────────────────────────────────"
check_file "python/requirements-dev.txt"
check_file ".vscode/settings.json"
check_file ".vscode/extensions.json"

echo ""
echo "📜 Скрипты:"
echo "─────────────────────────────────"
check_executable "python/lint.sh"
check_executable "python/fix.sh"
check_executable "python/lint-help.sh"

echo ""
echo "📚 Документация:"
echo "─────────────────────────────────"
check_file "LINTING.md"
check_file "CI_CD_EXAMPLES.md"

echo ""
echo "════════════════════════════════════════════════════════════"
echo "🎯 Следующие шаги:"
echo "────────────────────────────────────────────────────────────"
echo "1. Установите зависимости:"
echo "   cd python && pip install -r requirements-dev.txt"
echo ""
echo "2. Установите pre-commit хуки:"
echo "   pre-commit install"
echo ""
echo "3. Запустите проверку кода:"
echo "   cd python && ./lint.sh"
echo ""
echo "4. Или автоматически исправьте проблемы:"
echo "   cd python && ./fix.sh"
echo ""
echo "5. Для Dart:"
echo "   cd dart && dart analyze"
echo ""
echo "6. Прочитайте документацию:"
echo "   cat LINTING.md"
echo "════════════════════════════════════════════════════════════"





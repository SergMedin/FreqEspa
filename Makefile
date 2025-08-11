# Makefile для Spanish Analyser

.PHONY: help install test clean run lint format

# Переменные
PYTHON = python3
PIP = pip3
VENV = venv
SRC_DIR = src
TESTS_DIR = tests

# Цвета для вывода
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

help: ## Показать справку по командам
	@echo "$(GREEN)Доступные команды:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(YELLOW)%-20s$(NC) %s\n", $$1, $$2}'

install: ## Установить зависимости
	@echo "$(GREEN)Создание виртуального окружения...$(NC)"
	$(PYTHON) -m venv $(VENV)
	@echo "$(GREEN)Активация виртуального окружения...$(NC)"
	. $(VENV)/bin/activate && $(PIP) install --upgrade pip
	@echo "$(GREEN)Установка зависимостей...$(NC)"
	. $(VENV)/bin/activate && $(PIP) install -r requirements.txt
	@echo "$(GREEN)Установка модуля в режиме разработки...$(NC)"
	. $(VENV)/bin/activate && $(PIP) install -e .

install-dev: ## Установить зависимости для разработки
	@echo "$(GREEN)Установка зависимостей для разработки...$(NC)"
	. $(VENV)/bin/activate && $(PIP) install -e ".[dev]"

test: ## Запустить тесты
	@echo "$(GREEN)Запуск тестов...$(NC)"
	. $(VENV)/bin/activate && $(PYTHON) -m pytest $(TESTS_DIR)/ -v

test-coverage: ## Запустить тесты с покрытием
	@echo "$(GREEN)Запуск тестов с покрытием...$(NC)"
	. $(VENV)/bin/activate && $(PYTHON) -m pytest $(TESTS_DIR)/ --cov=$(SRC_DIR)/spanish_analyser --cov-report=html

run: ## Запустить основной скрипт
	@echo "$(GREEN)Запуск основного скрипта...$(NC)"
	. $(VENV)/bin/activate && $(PYTHON) $(SRC_DIR)/main.py

lint: ## Проверить код линтером
	@echo "$(GREEN)Проверка кода...$(NC)"
	. $(VENV)/bin/activate && flake8 $(SRC_DIR)/ $(TESTS_DIR)/

format: ## Форматировать код
	@echo "$(GREEN)Форматирование кода...$(NC)"
	. $(VENV)/bin/activate && black $(SRC_DIR)/ $(TESTS_DIR)/

clean: ## Очистить временные файлы
	@echo "$(GREEN)Очистка временных файлов...$(NC)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	find . -type d -name "build" -exec rm -rf {} +
	find . -type d -name "dist" -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -exec rm -rf {} +
	find . -type d -name "htmlcov" -exec rm -rf {} +
	rm -f .coverage

venv-activate: ## Активировать виртуальное окружение
	@echo "$(GREEN)Для активации виртуального окружения выполните:$(NC)"
	@echo "$(YELLOW)source $(VENV)/bin/activate$(NC)"

check-venv: ## Проверить виртуальное окружение
	@if [ -d "$(VENV)" ]; then \
		echo "$(GREEN)Виртуальное окружение найдено в $(VENV)$(NC)"; \
	else \
		echo "$(RED)Виртуальное окружение не найдено. Выполните 'make install'$(NC)"; \
	fi

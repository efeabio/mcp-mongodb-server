# Makefile para FastMCP MongoDB Server

.PHONY: help install install-dev test test-fast lint format clean dev-setup ci all run debug

# Variáveis
PYTHON = python3
PIP = pip3
PYTEST = pytest
BLACK = black
ISORT = isort
FLAKE8 = flake8
MYPY = mypy

# Comandos padrão
help: ## Mostra esta ajuda
	@echo "Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Instala dependências de produção
	$(PIP) install -r requirements.txt

install-dev: ## Instala dependências de desenvolvimento
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt

test: ## Executa testes com cobertura
	$(PYTEST) tests/ -v --cov=src --cov-report=term-missing --cov-report=html

test-fast: ## Executa testes sem cobertura
	$(PYTEST) tests/ -v

test-unit: ## Executa apenas testes unitários
	$(PYTEST) tests/unit/ -v

test-integration: ## Executa apenas testes de integração
	$(PYTEST) tests/integration/ -v

lint: ## Verifica qualidade do código
	@echo "Verificando formatação com Black..."
	$(BLACK) --check src/ tests/
	@echo "Verificando ordenação de imports com isort..."
	$(ISORT) --check-only src/ tests/
	@echo "Verificando estilo com flake8..."
	$(FLAKE8) src/ tests/
	@echo "Verificando tipos com mypy..."
	$(MYPY) src/
	@echo "Verificação de qualidade concluída!"

format: ## Formata código automaticamente
	@echo "Formatando código com Black..."
	$(BLACK) src/ tests/
	@echo "Ordenando imports com isort..."
	$(ISORT) src/ tests/
	@echo "Código formatado!"

clean: ## Limpa arquivos temporários
	@echo "Limpando arquivos temporários..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name "*.pyo" -delete 2>/dev/null || true
	find . -name "*.pyd" -delete 2>/dev/null || true
	find . -name ".coverage" -delete 2>/dev/null || true
	find . -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -name ".dmypy.json" -delete 2>/dev/null || true
	@echo "Limpeza concluída!"

clean-venv: ## Remove ambiente virtual
	@echo "Removendo ambiente virtual..."
	rm -rf venv/
	@echo "Ambiente virtual removido!"

dev-setup: install-dev ## Configura ambiente de desenvolvimento
	@echo "Ambiente de desenvolvimento configurado!"
	@echo "Para executar testes: make test"
	@echo "Para verificar código: make lint"
	@echo "Para formatar código: make format"

ci: lint test ## Executa pipeline de CI
	@echo "Pipeline de CI concluído com sucesso!"

all: clean install-dev lint test ## Executa todas as verificações
	@echo "Todas as verificações concluídas!"

run: ## Executa o servidor
	@echo "Executando servidor FastMCP MongoDB..."
	$(PYTHON) -m src.main

debug: ## Executa servidor em modo debug
	@echo "Executando servidor em modo debug..."
	export PYTHONPATH="${PYTHONPATH}:$(PWD)" && \
	export LOG_LEVEL=DEBUG && \
	export DEBUG=true && \
	$(PYTHON) -m src.main

check-deps: ## Verifica dependências desatualizadas
	@echo "Verificando dependências..."
	$(PIP) list --outdated

update-deps: ## Atualiza dependências
	@echo "Atualizando dependências..."
	$(PIP) install --upgrade -r requirements.txt
	$(PIP) install --upgrade -r requirements-dev.txt

security-check: ## Executa verificações de segurança
	@echo "Executando verificações de segurança..."
	@if command -v bandit >/dev/null 2>&1; then \
		echo "Executando Bandit..."; \
		bandit -r src/; \
	else \
		echo "Bandit não encontrado. Instale com: pip install bandit"; \
	fi
	@if command -v safety >/dev/null 2>&1; then \
		echo "Executando Safety..."; \
		safety check -r requirements.txt; \
	else \
		echo "Safety não encontrado. Instale com: pip install safety"; \
	fi

coverage: ## Gera relatório de cobertura
	@echo "Gerando relatório de cobertura..."
	$(PYTEST) tests/ --cov=src --cov-report=html --cov-report=term-missing
	@echo "Relatório de cobertura gerado em htmlcov/"

coverage-xml: ## Gera relatório de cobertura em XML
	@echo "Gerando relatório de cobertura em XML..."
	$(PYTEST) tests/ --cov=src --cov-report=xml
	@echo "Relatório XML gerado em coverage.xml"

docs: ## Gera documentação
	@echo "Gerando documentação..."
	@if command -v pdoc >/dev/null 2>&1; then \
		pdoc --html --output-dir docs src/; \
		echo "Documentação gerada em docs/"; \
	else \
		echo "pdoc não encontrado. Instale com: pip install pdoc"; \
	fi

install-pre-commit: ## Instala hooks do pre-commit
	@echo "Instalando hooks do pre-commit..."
	@if command -v pre-commit >/dev/null 2>&1; then \
		pre-commit install; \
		echo "Hooks do pre-commit instalados!"; \
	else \
		echo "pre-commit não encontrado. Instale com: pip install pre-commit"; \
	fi

pre-commit-run: ## Executa todos os hooks do pre-commit
	@echo "Executando hooks do pre-commit..."
	@if command -v pre-commit >/dev/null 2>&1; then \
		pre-commit run --all-files; \
	else \
		echo "pre-commit não encontrado. Instale com: pip install pre-commit"; \
	fi

# Comandos de desenvolvimento específicos
dev-test: ## Executa testes em modo desenvolvimento
	@echo "Executando testes em modo desenvolvimento..."
	export PYTHONPATH="${PYTHONPATH}:$(PWD)" && \
	export LOG_LEVEL=DEBUG && \
	$(PYTEST) tests/ -v --tb=short

dev-lint: ## Executa linting em modo desenvolvimento
	@echo "Executando linting em modo desenvolvimento..."
	export PYTHONPATH="${PYTHONPATH}:$(PWD)" && \
	$(BLACK) --check src/ tests/ && \
	$(ISORT) --check-only src/ tests/ && \
	$(FLAKE8) src/ tests/ && \
	$(MYPY) src/

# Comandos de manutenção
check-imports: ## Verifica imports não utilizados
	@echo "Verificando imports não utilizados..."
	@if command -v autoflake >/dev/null 2>&1; then \
		autoflake --check --remove-all-unused-imports --recursive src/ tests/; \
	else \
		echo "autoflake não encontrado. Instale com: pip install autoflake"; \
	fi

remove-unused-imports: ## Remove imports não utilizados
	@echo "Removendo imports não utilizados..."
	@if command -v autoflake >/dev/null 2>&1; then \
		autoflake --remove-all-unused-imports --recursive --in-place src/ tests/; \
		echo "Imports não utilizados removidos!"; \
	else \
		echo "autoflake não encontrado. Instale com: pip install autoflake"; \
	fi

# Comandos de validação
validate: ## Valida estrutura do projeto
	@echo "Validando estrutura do projeto..."
	@if [ ! -f "pyproject.toml" ]; then echo "ERRO: pyproject.toml não encontrado"; exit 1; fi
	@if [ ! -f "requirements.txt" ]; then echo "ERRO: requirements.txt não encontrado"; exit 1; fi
	@if [ ! -d "src" ]; then echo "ERRO: diretório src não encontrado"; exit 1; fi
	@if [ ! -d "tests" ]; then echo "ERRO: diretório tests não encontrado"; exit 1; fi
	@echo "Estrutura do projeto válida!"

# Comandos de ajuda
list-commands: ## Lista todos os comandos disponíveis
	@echo "Comandos disponíveis:"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  %-20s %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# Comando padrão
.DEFAULT_GOAL := help

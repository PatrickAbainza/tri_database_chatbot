# ==============================================================================
# Python (uv) Template Tasks (runs in templates/python-uv)
# ==============================================================================
.PHONY: setup-py test-py coverage-py lint-py analyze-py security-py docker-build-py clean-py

setup-py: ## Install Python dependencies using uv
	@echo ">>> Setting up Python environment in templates/python-uv..."
	@cd templates/python-uv && uv sync --all-extras

test-py: ## Run Python tests
	@echo ">>> Running Python tests in templates/python-uv..."
	@cd templates/python-uv && uv run pytest

coverage-py: ## Run Python tests with coverage report
	@echo ">>> Running Python tests with coverage in templates/python-uv..."
	@cd templates/python-uv && uv run pytest --cov=src --cov-report=term-missing --cov-report=xml:coverage.xml

lint-py: ## Run Python linter (Ruff)
	@echo ">>> Running Python linter (Ruff) in templates/python-uv..."
	@cd templates/python-uv && uv run ruff check .

analyze-py: ## Run all Python static analysis checks (Radon, Copydetect, Pydeps)
	@echo ">>> Running Python static analysis in templates/python-uv..."
	@echo "  > Radon Complexity..."
	@cd templates/python-uv && uv run radon cc . -a -s
	@echo "  > Radon Maintainability..."
	@cd templates/python-uv && uv run radon mi . -s
	@echo "  > Copydetect Duplication..."
	@cd templates/python-uv && uv run copydetect -t . --min-tokens 50 -o analysis_results/copydetect_report.html || echo "Copydetect finished (ignore errors if no duplicates found)"
	@echo "  > Pydeps Dependency Graph (JSON)..."
	@cd templates/python-uv && uv run pydeps --json src > analysis_results/pydeps_results.json || echo "Pydeps finished (check analysis_results/pydeps_results.json)"

security-py: ## Run Python dependency vulnerability scan (pip-audit)
	@echo ">>> Running Python security scan in templates/python-uv..."
	@cd templates/python-uv && uv run pip-audit

docker-build-py: ## Build the Python Docker image
	@echo ">>> Building Python Docker image from templates/python-uv/Dockerfile..."
	@docker build -t python-template-app -f templates/python-uv/Dockerfile templates/python-uv

clean-py: ## Clean Python generated files
	@echo ">>> Cleaning Python generated files in templates/python-uv..."
	@rm -rf templates/python-uv/.pytest_cache
	@rm -rf templates/python-uv/.ruff_cache
	@rm -rf templates/python-uv/__pycache__
	@rm -rf templates/python-uv/src/__pycache__
	@rm -rf templates/python-uv/tests/__pycache__
	@rm -f templates/python-uv/coverage.xml
	@rm -rf templates/python-uv/analysis_results

# ==============================================================================
# Node.js (Vitest) Template Tasks (runs in templates/nodejs-vitest)
# ==============================================================================
.PHONY: setup-node test-node coverage-node lint-node analyze-node security-node docker-build-node clean-node

setup-node: ## Install Node.js dependencies using npm
	@echo ">>> Setting up Node.js environment in templates/nodejs-vitest..."
	@cd templates/nodejs-vitest && npm ci

test-node: ## Run Node.js tests (includes coverage)
	@echo ">>> Running Node.js tests with coverage in templates/nodejs-vitest..."
	@cd templates/nodejs-vitest && npm test

coverage-node: test-node ## Alias for running Node.js tests with coverage

lint-node: ## Run Node.js linter (ESLint)
	@echo ">>> Running Node.js linter (ESLint) in templates/nodejs-vitest..."
	@cd templates/nodejs-vitest && npm run lint # Assumes lint script exists

analyze-node: ## Run all Node.js static analysis checks (JSCPD, Dependency Cruiser)
	@echo ">>> Running Node.js static analysis in templates/nodejs-vitest..."
	@echo "  > JSCPD Duplication..."
	@cd templates/nodejs-vitest && npx jscpd src/ --min-lines 5 --threshold 0
	@echo "  > Dependency Cruiser Graph (JSON)..."
	@cd templates/nodejs-vitest && mkdir -p analysis_results && npx depcruise --include-only "^src" --output-type archi src > analysis_results/dependency-graph.json

security-node: ## Run Node.js dependency vulnerability scan (npm audit)
	@echo ">>> Running Node.js security scan in templates/nodejs-vitest..."
	@cd templates/nodejs-vitest && npm audit --audit-level=high

docker-build-node: ## Build the Node.js Docker image
	@echo ">>> Building Node.js Docker image from templates/nodejs-vitest/Dockerfile..."
	@docker build -t nodejs-template-app -f templates/nodejs-vitest/Dockerfile templates/nodejs-vitest

clean-node: ## Clean Node.js generated files
	@echo ">>> Cleaning Node.js generated files in templates/nodejs-vitest..."
	@rm -rf templates/nodejs-vitest/node_modules
	@rm -rf templates/nodejs-vitest/dist
	@rm -rf templates/nodejs-vitest/coverage
	@rm -rf templates/nodejs-vitest/analysis_results

# ==============================================================================
# Combined Tasks
# ==============================================================================
.PHONY: setup test coverage lint analyze security docker-build clean help

setup: setup-py setup-node ## Setup both Python and Node.js environments
test: test-py test-node ## Run tests for both Python and Node.js
coverage: coverage-py coverage-node ## Run tests with coverage for both
lint: lint-py lint-node ## Run linters for both
analyze: analyze-py analyze-node ## Run static analysis for both
security: security-py security-node ## Run security scans for both
docker-build: docker-build-py docker-build-node ## Build Docker images for both
clean: clean-py clean-node ## Clean generated files for both

# ==============================================================================
# Help Target
# ==============================================================================
help: ## Show help for Makefile targets
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
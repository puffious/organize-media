# AI-Powered Media Library Organizer - Makefile
# Production-ready automation for common development and deployment tasks

.PHONY: help install install-dev test clean lint format check setup run-setup
.DEFAULT_GOAL := help

# Colors for output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

help: ## Show this help message
	@echo "$(BLUE)AI-Powered Media Library Organizer$(RESET)"
	@echo "$(BLUE)=================================$(RESET)"
	@echo ""
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'

install: ## Install production dependencies
	@echo "$(BLUE)Installing production dependencies...$(RESET)"
	pip install -r requirements.txt
	@echo "$(GREEN)✅ Dependencies installed$(RESET)"

install-dev: install ## Install development dependencies
	@echo "$(BLUE)Installing development dependencies...$(RESET)"
	pip install -e ".[dev]"
	@echo "$(GREEN)✅ Development environment ready$(RESET)"

setup: install ## Run initial setup and configuration
	@echo "$(BLUE)Running initial setup...$(RESET)"
	python3 quickstart.py
	@echo "$(GREEN)✅ Setup completed$(RESET)"

test-connection: ## Test AI connection and configuration
	@echo "$(BLUE)Testing AI connection...$(RESET)"
	python3 src/main.py test
	@echo "$(GREEN)✅ Connection test completed$(RESET)"

lint: ## Run code linting
	@echo "$(BLUE)Running linting checks...$(RESET)"
	@if command -v flake8 >/dev/null 2>&1; then \
		flake8 src/ --max-line-length=100 --ignore=E203,W503; \
		echo "$(GREEN)✅ Linting completed$(RESET)"; \
	else \
		echo "$(YELLOW)⚠️  flake8 not installed, skipping lint check$(RESET)"; \
	fi

format: ## Format code with black
	@echo "$(BLUE)Formatting code...$(RESET)"
	@if command -v black >/dev/null 2>&1; then \
		black src/ --line-length=100; \
		echo "$(GREEN)✅ Code formatted$(RESET)"; \
	else \
		echo "$(YELLOW)⚠️  black not installed, skipping formatting$(RESET)"; \
	fi

type-check: ## Run type checking with mypy
	@echo "$(BLUE)Running type checks...$(RESET)"
	@if command -v mypy >/dev/null 2>&1; then \
		mypy src/ --ignore-missing-imports; \
		echo "$(GREEN)✅ Type checking completed$(RESET)"; \
	else \
		echo "$(YELLOW)⚠️  mypy not installed, skipping type check$(RESET)"; \
	fi

check: lint type-check ## Run all code quality checks
	@echo "$(GREEN)✅ All checks completed$(RESET)"

clean: ## Clean up temporary files and directories
	@echo "$(BLUE)Cleaning up...$(RESET)"
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ .pytest_cache/ .mypy_cache/
	@echo "$(GREEN)✅ Cleanup completed$(RESET)"

scan: ## Scan a directory (requires MEDIA_PATH environment variable)
	@if [ -z "$(MEDIA_PATH)" ]; then \
		echo "$(RED)❌ MEDIA_PATH environment variable not set$(RESET)"; \
		echo "Usage: make scan MEDIA_PATH=/path/to/media"; \
		exit 1; \
	fi
	@echo "$(BLUE)Scanning directory: $(MEDIA_PATH)$(RESET)"
	python3 src/main.py scan "$(MEDIA_PATH)"

organize-shows: ## Organize TV shows (requires SHOWS_PATH environment variable)
	@if [ -z "$(SHOWS_PATH)" ]; then \
		echo "$(RED)❌ SHOWS_PATH environment variable not set$(RESET)"; \
		echo "Usage: make organize-shows SHOWS_PATH=/path/to/shows"; \
		exit 1; \
	fi
	@echo "$(BLUE)Organizing TV shows: $(SHOWS_PATH)$(RESET)"
	python3 src/main.py organize-show "$(SHOWS_PATH)"

organize-movies: ## Organize movies (requires MOVIES_PATH environment variable)
	@if [ -z "$(MOVIES_PATH)" ]; then \
		echo "$(RED)❌ MOVIES_PATH environment variable not set$(RESET)"; \
		echo "Usage: make organize-movies MOVIES_PATH=/path/to/movies"; \
		exit 1; \
	fi
	@echo "$(BLUE)Organizing movies: $(MOVIES_PATH)$(RESET)"
	python3 src/main.py organize-movies "$(MOVIES_PATH)"

status: ## Show status of media directory (requires MEDIA_PATH environment variable)
	@if [ -z "$(MEDIA_PATH)" ]; then \
		echo "$(RED)❌ MEDIA_PATH environment variable not set$(RESET)"; \
		echo "Usage: make status MEDIA_PATH=/path/to/media"; \
		exit 1; \
	fi
	@echo "$(BLUE)Checking status: $(MEDIA_PATH)$(RESET)"
	python3 src/main.py status "$(MEDIA_PATH)"

cleanup-dirs: ## Clean up empty directories (requires MEDIA_PATH environment variable)
	@if [ -z "$(MEDIA_PATH)" ]; then \
		echo "$(RED)❌ MEDIA_PATH environment variable not set$(RESET)"; \
		echo "Usage: make cleanup-dirs MEDIA_PATH=/path/to/media"; \
		exit 1; \
	fi
	@echo "$(BLUE)Cleaning up empty directories: $(MEDIA_PATH)$(RESET)"
	python3 src/main.py cleanup "$(MEDIA_PATH)"

undo: ## Undo last operation (requires MEDIA_PATH environment variable)
	@if [ -z "$(MEDIA_PATH)" ]; then \
		echo "$(RED)❌ MEDIA_PATH environment variable not set$(RESET)"; \
		echo "Usage: make undo MEDIA_PATH=/path/to/media"; \
		exit 1; \
	fi
	@echo "$(BLUE)Undoing last operation: $(MEDIA_PATH)$(RESET)"
	python3 src/main.py undo "$(MEDIA_PATH)"

validate-env: ## Validate environment configuration
	@echo "$(BLUE)Validating environment...$(RESET)"
	@if [ ! -f .env ]; then \
		echo "$(RED)❌ .env file not found$(RESET)"; \
		echo "Run: make setup"; \
		exit 1; \
	fi
	@if ! grep -q "GEMINI_API_KEY=" .env; then \
		echo "$(RED)❌ GEMINI_API_KEY not found in .env$(RESET)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✅ Environment validated$(RESET)"

package: clean ## Create distribution package
	@echo "$(BLUE)Creating distribution package...$(RESET)"
	python3 setup.py sdist bdist_wheel
	@echo "$(GREEN)✅ Package created in dist/$(RESET)"

install-package: package ## Install the package locally
	@echo "$(BLUE)Installing package locally...$(RESET)"
	pip install dist/*.whl --force-reinstall
	@echo "$(GREEN)✅ Package installed$(RESET)"

# Production shortcuts
quick-setup: ## Quick setup for production use
	@echo "$(BLUE)Quick production setup...$(RESET)"
	$(MAKE) install
	$(MAKE) validate-env || $(MAKE) setup
	$(MAKE) test-connection
	@echo "$(GREEN)✅ Production setup completed$(RESET)"

# Development shortcuts
dev-setup: ## Full development environment setup
	@echo "$(BLUE)Development environment setup...$(RESET)"
	$(MAKE) install-dev
	$(MAKE) validate-env || $(MAKE) setup
	$(MAKE) check
	$(MAKE) test-connection
	@echo "$(GREEN)✅ Development environment ready$(RESET)"

# Usage examples
examples: ## Show usage examples
	@echo "$(BLUE)Usage Examples:$(RESET)"
	@echo ""
	@echo "$(GREEN)Setup:$(RESET)"
	@echo "  make setup                           # Interactive setup"
	@echo "  make quick-setup                     # Production setup"
	@echo "  make dev-setup                       # Development setup"
	@echo ""
	@echo "$(GREEN)Media Operations:$(RESET)"
	@echo "  make scan MEDIA_PATH=/path/to/media"
	@echo "  make organize-shows SHOWS_PATH=/path/to/shows"
	@echo "  make organize-movies MOVIES_PATH=/path/to/movies"
	@echo "  make status MEDIA_PATH=/path/to/media"
	@echo ""
	@echo "$(GREEN)Maintenance:$(RESET)"
	@echo "  make cleanup-dirs MEDIA_PATH=/path/to/media"
	@echo "  make undo MEDIA_PATH=/path/to/media"
	@echo "  make clean                           # Clean temp files"
	@echo ""
	@echo "$(GREEN)Development:$(RESET)"
	@echo "  make check                           # Run all checks"
	@echo "  make format                          # Format code"
	@echo "  make lint                           # Lint code"

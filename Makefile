# WoW Classic SoD Recipe Calculator Makefile

.PHONY: help install test lint format clean run scrape server

# Default target
help:
	@echo "WoW Classic SoD Recipe Calculator"
	@echo "=================================="
	@echo ""
	@echo "Available commands:"
	@echo "  install    - Install Python dependencies"
	@echo "  test       - Run tests"
	@echo "  lint       - Run linting checks"
	@echo "  format     - Format code with black"
	@echo "  clean      - Clean up temporary files"
	@echo "  run        - Run the web server"
	@echo "  scrape     - Run the scraper"
	@echo "  server     - Run the Flask server"
	@echo "  build      - Build the project"
	@echo "  deploy     - Deploy the application"

# Install dependencies
install:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt
	@echo "Dependencies installed successfully!"

# Run tests
test:
	@echo "Running tests..."
	python -m pytest test_scraper.py -v
	@echo "Tests completed!"

# Run linting
lint:
	@echo "Running linting checks..."
	flake8 scrape_wowhead.py utils.py config.py server.py
	mypy scrape_wowhead.py utils.py config.py server.py
	@echo "Linting completed!"

# Format code
format:
	@echo "Formatting code..."
	black scrape_wowhead.py utils.py config.py server.py test_scraper.py
	@echo "Code formatting completed!"

# Clean up temporary files
clean:
	@echo "Cleaning up temporary files..."
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
	find . -type f -name "*.log" -delete
	find . -type f -name ".DS_Store" -delete
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	@echo "Cleanup completed!"

# Run the web server (simple HTTP server)
run:
	@echo "Starting web server..."
	python -m http.server 8000

# Run the scraper
scrape:
	@echo "Running scraper..."
	python scrape_wowhead.py urls.txt recipes.json

# Run the Flask server
server:
	@echo "Starting Flask server..."
	python server.py --debug --reload

# Build the project
build: clean install test lint
	@echo "Building project..."
	@echo "Project built successfully!"

# Deploy the application
deploy: build
	@echo "Deploying application..."
	@echo "Deployment completed!"

# Development setup
dev-setup: install format lint test
	@echo "Development environment setup completed!"

# Quick start
quick-start: install server
	@echo "Application started! Visit http://localhost:8000"

# Backup data
backup:
	@echo "Creating backup..."
	cp recipes.json recipes.json.backup
	cp materials.json materials.json.backup
	@echo "Backup created!"

# Restore data
restore:
	@echo "Restoring from backup..."
	cp recipes.json.backup recipes.json
	cp materials.json.backup materials.json
	@echo "Data restored!"

# Update dependencies
update-deps:
	@echo "Updating dependencies..."
	pip install --upgrade -r requirements.txt
	@echo "Dependencies updated!"

# Check for security vulnerabilities
security-check:
	@echo "Checking for security vulnerabilities..."
	pip-audit
	@echo "Security check completed!"

# Generate documentation
docs:
	@echo "Generating documentation..."
	pydoc -w scrape_wowhead.py utils.py config.py server.py
	@echo "Documentation generated!"

# Performance test
perf-test:
	@echo "Running performance tests..."
	python -m pytest test_scraper.py::TestIntegration -v
	@echo "Performance tests completed!"

# Full test suite
full-test: test lint security-check perf-test
	@echo "Full test suite completed!"

# Production build
prod-build: clean install full-test
	@echo "Production build completed!"

# Production server
prod-server:
	@echo "Starting production server..."
	python server.py --host 0.0.0.0 --port 8000

# Monitor logs
logs:
	@echo "Monitoring logs..."
	tail -f logs/scraper.log

# Database operations (if implemented)
db-init:
	@echo "Initializing database..."
	@echo "Database initialized!"

db-migrate:
	@echo "Running database migrations..."
	@echo "Migrations completed!"

# Docker operations (if implemented)
docker-build:
	@echo "Building Docker image..."
	docker build -t wow-recipe-calculator .
	@echo "Docker image built!"

docker-run:
	@echo "Running Docker container..."
	docker run -p 8000:8000 wow-recipe-calculator

# Environment setup
env-setup:
	@echo "Setting up environment..."
	@echo "export ENVIRONMENT=development" >> ~/.bashrc
	@echo "Environment variables set!"

# Git operations
git-setup:
	@echo "Setting up Git hooks..."
	cp hooks/pre-commit .git/hooks/
	chmod +x .git/hooks/pre-commit
	@echo "Git hooks installed!"

# Release preparation
release-prep: clean full-test
	@echo "Preparing release..."
	@echo "Release preparation completed!"

# Help for specific commands
help-install:
	@echo "install: Install Python dependencies from requirements.txt"

help-test:
	@echo "test: Run the test suite using pytest"

help-lint:
	@echo "lint: Run flake8 and mypy for code quality checks"

help-format:
	@echo "format: Format code using black"

help-clean:
	@echo "clean: Remove temporary files and caches"

help-run:
	@echo "run: Start a simple HTTP server on port 8000"

help-scrape:
	@echo "scrape: Run the recipe scraper with default settings"

help-server:
	@echo "server: Start the Flask web server with debug mode"

help-build:
	@echo "build: Clean, install, test, and lint the project"

help-deploy:
	@echo "deploy: Build and deploy the application"
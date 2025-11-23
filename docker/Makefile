# Makefile for Docker Compose Management
# This Makefile abstracts common Docker commands for the Blog Creator Agent development environment

.PHONY: help build up down restart logs ssh status clean shell rebuild redis

# Default target
help: ## Show this help message
	@echo "Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  %-20s %s\n", $$1, $$2}'

build: ## Build the Docker image
	docker compose -f docker-compose.yml --profile dev build blog-creator-dev

up: ## Start all containers in detached mode
	docker compose -f docker-compose.yml --profile dev up -d

down: ## Stop and remove all containers
	docker compose -f docker-compose.yml --profile dev down

restart: ## Restart all containers
	docker compose -f docker-compose.yml --profile dev restart

logs: ## Show container logs (follow mode)
	docker compose -f docker-compose.yml --profile dev logs -f blog-creator-dev

ssh: ## Connect to the container via SSH
	ssh -p 2226 vscode@localhost

status: ## Show container status
	docker compose -f docker-compose.yml --profile dev ps

clean: ## Remove containers, networks, and volumes
	docker compose -f docker-compose.yml --profile dev down -v --remove-orphans

shell: ## Open a shell in the running container
	docker compose -f docker-compose.yml --profile dev exec blog-creator-dev bash

rebuild: ## Rebuild and restart the container
	docker compose -f docker-compose.yml --profile dev down
	docker compose -f docker-compose.yml --profile dev build blog-creator-dev --no-cache
	docker compose -f docker-compose.yml --profile dev up -d

redis: ## Start only Redis service
	docker compose -f docker-compose.yml --profile dev up -d redis

redis-logs: ## Show Redis logs
	docker compose -f docker-compose.yml --profile dev logs -f redis

elasticsearch: ## Start only Elasticsearch service
	docker compose -f docker-compose.yml --profile dev up -d elasticsearch

elasticsearch-logs: ## Show Elasticsearch logs
	docker compose -f docker-compose.yml --profile dev logs -f elasticsearch

kibana: ## Start only Kibana service
	docker compose -f docker-compose.yml --profile dev up -d kibana

kibana-logs: ## Show Kibana logs
	docker compose -f docker-compose.yml --profile dev logs -f kibana
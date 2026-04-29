DOCKER_COMPOSE = docker compose

dev:
	@figlet "DEVELOPMENT"
	@sleep 1


	$(DOCKER_COMPOSE) --env-file dev.env -f docker-compose.dev.yaml up --build

dev-down:
	@echo "Stopping Development Environment..."
	$(DOCKER_COMPOSE) --env-file dev.env -f docker-compose.dev.yaml down

prod:
	@sleep 1

	$(DOCKER_COMPOSE) --env-file prod.env -f docker-compose.prod.yaml up -d

prod-down:
	@echo "Stopping Production Environment..."
	$(DOCKER_COMPOSE) --env-file prod.env -f docker-compose.prod.yaml down

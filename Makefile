.PHONY: dev dev-down

dev:
	docker compose --env-file dev.env -f docker-compose.yml up --build

dev-down:
	docker compose --env-file dev.env -f docker-compose.yml down

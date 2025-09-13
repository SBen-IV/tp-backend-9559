watch:
	docker compose watch

up:
	docker compose up

build:
	docker compose build

down:
	docker compose down

run: build up

logs:
	docker compose logs -f

enter_backend:
	docker compose exec 9559-backend bash

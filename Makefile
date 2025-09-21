# For development, hot reloads as code is changed
watch:
	docker compose watch

# Run without building (unless never built)
up:
	docker compose up

# Build the images
build:
	docker compose build

# Stop and remove containers
down:
	docker compose down

# Force building images and run
run: build up

# To see logs of containers, useful when using `watch` as it
# doesn't provide logs
logs:
	docker compose logs -f

# Enter the backend container to run migrations
enter_backend:
	docker compose exec 9559-backend bash

# Enter db, once inside you can make SQL queries as usual
enter_db:
	docker compose exec 9559-db psql itil -U postgres

# Remove the volume attached to the database
# It will remove ALL TABLES which will have to be re-created with
# migrations
reset_db:
	docker volume rm backend_9559-db-itil

# Run only tests, 9559-backend service must be up with `watch` or `up`
pytest:
	docker compose exec --env TESTS=1 9559-backend pytest

# Run tests with coverage, 9559-backend service must be up with `watch` or `up`
coverage:
	docker compose exec 9559-backend bash scripts/tests-start.sh

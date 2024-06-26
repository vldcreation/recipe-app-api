test:
	@echo "Running test file"
	docker-compose run --rm app sh -c "python manage.py test"
	@echo "Test completed"

rebuild:
	docker-compose down --remove-orphans --volumes --rmi
	docker system prune -a
	docker system prune --volumes
	docker-compose up

rebuild-app:
	docker-compose up -d --no-deps --build app

start:
	docker-compose up

migration:
	@echo "Create Migration File"
	docker-compose run --rm app sh -c  "python manage.py makemigrations"

migrate:
	@echo "Running Migration File"
	docker-compose run --rm app sh -c  "python manage.py wait_for_db && python manage.py migrate"

lint:
	@echo "Running linter"
	docker-compose run --rm app sh -c "flake8"
	@echo "linter completed"

stop_local_db:
	@echo "Stopped local database"
	@pg_ctl -D "C:\Program Files\PostgreSQL\14\data" stop
	@echo "Successfully stopped database"

start_local_db:
	@echo "Running local database"
	@pg_ctl -D "C:\Program Files\PostgreSQL\14\data" restart
	@echo "Successfully running database"

app ?= ""
createapp:
	@echo "Creatin an app..."
	docker-compose run --rm app sh -c "python manage.py startapp ${app}"
	@echo "${app} created Successfully"

superuser:
	@echo "Running command to create superuser"
	docker-compose run --rm app sh -c "python manage.py createsuperuser"
	@echo "Created superuser Successfully"

.PHONY: test rebuild rebuild-app migration migrate lint start_local_db stop_local_db start createapp superuser
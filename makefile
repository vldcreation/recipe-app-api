test:
	@echo "Running test file"
	docker-compose run --rm app sh -c "python manage.py test"
	@echo "Test completed"

lint:
	@echo "Running linter"
	docker-compose run --rm app sh -c "python manage.py test && flake8"
	@echo "linter completed"

stop_local_db:
	@echo "Stopped local database"
	@pg_ctl -D "C:\Program Files\PostgreSQL\14\data" stop
	@echo "Successfully stopped database"

start_local_db:
	@echo "Running local database"
	@pg_ctl -D "C:\Program Files\PostgreSQL\14\data" restart
	@echo "Successfully running database"

.PHONY: test start_local_db start_local_db lint
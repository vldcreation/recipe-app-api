test:
	@echo "Running test file"
	docker-compose run --rm app sh -c "python manage.py test"
	@echo "Test completed"

.PHONY: test
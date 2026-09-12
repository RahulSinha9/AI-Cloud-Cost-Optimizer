.PHONY: install test lint run docker-build docker-up format

install:
	python -m pip install -e '.[test]'

test:
	pytest --cov=app --cov-report=term-missing

lint:
	ruff check .

format:
	ruff check . --fix

run:
	uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

docker-build:
	docker build -t ai-cloud-cost-optimizer:local .

docker-up:
	docker compose up --build

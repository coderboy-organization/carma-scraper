APP_FILE=app/main.py
APP_MODULE=app.main:app
PORT=8000

.PHONY: install dev run run-prod build

install:
	pip install -r requirements.txt

dev: install
	fastapi dev $(APP_FILE) --reload --port $(PORT)

run:
	uvicorn $(APP_MODULE) --reload --port $(PORT)

run-prod:
	uvicorn $(APP_MODULE) --host 0.0.0.0 --port $(PORT) --workers 2

build:
	fastapi build $(APP_FILE)

docker-build:
	docker build -f Dockerfile.scraper -t devlopersabbir/carmasearch-scraper:latest .

docker-run:
	docker run --env-file .env -p 8000:8000 devlopersabbir/carmasearch-scraper:latest

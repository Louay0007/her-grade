dev:
	uvicorn app.main:app --reload --port 8000
prod:
	docker compose up --build -d
test:
	pytest -q
lint:
	ruff check app vision tests scripts && black --check app vision tests scripts
backup:
	bash scripts/backup.sh
seed:
	python scripts/seed_demo.py

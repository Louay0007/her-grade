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
fetch-inat:
	python scripts/fetch_public_leaf_data.py --source inat --n 800
fetch-pv:
	python scripts/fetch_public_leaf_data.py --source plantvillage --n 800
make-surrogate:
	python scripts/make_surrogate_splits.py
train-surrogate:
	python -m vision.train --data data/surrogate/train --out data/surrogate_baseline.pkl --thresh-out data/surrogate_thresh.json
eval-surrogate:
	python -m vision.eval --data data/surrogate/test --model data/surrogate_baseline.pkl --out docs/evidence/surrogate_eval.json
train-bench:
	python -m vision.train --data data/raw/rosemary --out data/rosemary_baseline.pkl
eval-bench:
	python -m vision.eval --data data/raw/rosemary --out docs/evidence/eval_results.json

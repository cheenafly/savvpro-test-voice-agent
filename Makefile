BACKEND := backend
PY := .venv/bin/python

.PHONY: install seed train test lint run-backend run-frontend

install:
	cd $(BACKEND) && python3 -m venv .venv && $(PY) -m pip install --upgrade pip && $(PY) -m pip install -r requirements.txt
	cd frontend && [ -f package.json ] && npm install || true

seed:
	cd $(BACKEND) && $(PY) -m app.db.seed

train:
	cd $(BACKEND) && $(PY) -m app.nlu.train

test:
	cd $(BACKEND) && $(PY) -m pytest

lint:
	cd $(BACKEND) && $(PY) -m ruff check . && $(PY) -m ruff format --check .

run-backend:
	cd $(BACKEND) && $(PY) -m uvicorn app.main:app --reload

run-frontend:
	cd frontend && npm run dev

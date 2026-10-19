PY := .venv/bin/python

env:
	python3.12 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt

test:
	$(PY) -m pytest -q tests

reproduce:
	$(PY) -m src.reproduce

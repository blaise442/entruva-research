PY := .venv/bin/python

env:
	python3.12 -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install -r requirements.txt

test:
	$(PY) -m pytest -q tests

reproduce:
	$(PY) -m src.reproduce
	$(PY) -m src.features.build
	$(PY) -m src.models.run_primary
	$(PY) -m src.models.run_robustness
	$(PY) -m src.adversarial.run_s3
	$(PY) -m src.adversarial.run_reputation

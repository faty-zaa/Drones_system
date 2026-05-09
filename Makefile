PY = python3
PIP = pip
PDB = pdb
FILE = fly.py

install:
	@$(PIP) install -r requirements.txt || true

run:
	@$(PY) $(FILE) $(ARG) || true

debug:
	@$(PY) -m $(PDB) $(FILE) || true

clean:
	@rm -rf __pycache__ .mypy_cache *.pyc || true

lint:
	@flake8 . || true
	@mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs || true
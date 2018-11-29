PYTEST_OPTS ?= ""
PYTEST_SRC ?= tests/
PYTEST_RUN_OPTS ?= -s -vvv

all: build

.PHONY: docs
docs:
	cd docs && make html

docs-clean:
	cd docs && sphinx-apidoc -H "API Reference" -M -f -o source ../datacatalog

release: build
	twine upload dist/*

build:
	python3 setup.py sdist bdist_wheel

clean: schemas-clean docs-clean
	rm -rf build *egg-info dist
	find . -d -name '*__pycache__*' -exec rm -rf {} \;
	find . -d -name '*.pytest_cache*' -exec rm -rf {} \;

developer-smoketests: smoketest-agave smoketest-config smoketest-google smoketest-mongo-local

smoketest-agave:
	python -m pytest -v --longrun -k agave_client_smoke $(PYTEST_SRC)

smoketest-config:
	python -m pytest -k config_yml_smoke $(PYTEST_SRC)

smoketest-mongo-local:
	python -m pytest -v -k db_connection $(PYTEST_SRC)

smoketest-google:

challenge_problems:
	python -m scripts.build_challenge_problems

experiment_designs: challenge_problems
	python -m scripts.build_experiment_designs

.PHONY: schemas
schemas: schemas-build schemas-validate

schemas-build:
	python -m scripts.build_schemas

schemas-validate:
	python -m pytest -v --longrun -k validate_all_schemas $(PYTEST_SRC)

schemas-test:
	LOCALONLY=1 MAKETESTS=1 python scripts/build_schemas.py

schemas-clean:
	rm -rf schemas/*.jsonschema

mongo-up:
	cd docker && docker-compose up -d --force-recreate --quiet-pull

mongo-down:
	cd docker && docker-compose down

tests-longrun:
	python -m pytest --cache-clear --longrun $(PYTEST_RUN_OPTS) $(PYTEST_SRC)

.PHONY: tests
tests:
	python -m pytest --cache-clear $(PYTEST_RUN_OPTS) $(PYTEST_OPTS) $(PYTEST_SRC)

tests-classify:
	python -m pytest $(PYTEST_RUN_OPTS) -k "formats_classify" $(PYTEST_SRC)

PYTEST_OPTS ?= ""
PYTEST_SRC ?= tests/

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

clean: schemas-clean
	rm -rf build *egg-info dist
	find . -d -name '*__pycache__*' -exec rm -rf {} \;
	find . -d -name '*.pytest_cache*' -exec rm -rf {} \;


.PHONY: schemas
schemas: schemas-clean
	python scripts/build_experiment_references.py && \
	python scripts/build_schemas.py

schemas-test:
	LOCALONLY=1 MAKETESTS=1 python scripts/build_schemas.py

schemas-clean:
	rm -rf schemas/*.jsonschema

mongo-up:
	cd docker && docker-compose up -d --force-recreate --quiet-pull

mongo-down:
	cd docker && docker-compose down

tests-longrun:
	python -m pytest --cache-clear --longrun $(PYTEST_SRC)

.PHONY: tests
tests:
	python -m pytest --cache-clear $(PYTEST_OPTS) $(PYTEST_SRC)

tests-classify:
	python -m pytest -s -vvv -k "formats_classify" $(PYTEST_SRC)

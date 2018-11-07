PYTEST_OPTS ?= ""

all: build

release: build
	twine upload dist/*

build:
	python3 setup.py sdist bdist_wheel

clean: schemas-clean
	rm -rf build *egg-info dist
	find . -d -name '*__pycache__*' -exec rm -rf {} \;

.PHONY: schemas
schemas: schemas-clean
	python scripts/build_experiment_references.py && \
	python scripts/build_schemas.py

schemas-test:
	MAKETESTS=1 python scripts/build_schemas.py

schemas-clean:
	rm -rf schemas/*.jsonschema

mongodb-up:
	cd docker && docker-compose up -d --force-recreate --quiet-pull

mongodb-down:
	cd docker && docker-compose down

tests-longrun:
	python -m pytest --cache-clear --longrun

.PHONY: tests
tests:
	python -m pytest --cache-clear $(PYTEST_OPTS)


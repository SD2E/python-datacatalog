PYTEST_OPTS ?= ""
PYTEST_SRC ?= tests/
PYTEST_RUN_OPTS ?= -s -vvv

all: build

# Generic all docs
.PHONY: docs
docs: docs-autodoc
	cd docs && make html

# Init automatic API documentation
docs-autodoc:
	cd docs && sphinx-apidoc -H "API Reference" -M -f -o source ../datacatalog

# Release on PyPi
release: build
	twine upload dist/*

build:
	python3 setup.py sdist bdist_wheel

# Clean all build artifacts
clean: schemas-clean docs-clean
	rm -rf build *egg-info dist
	find . -d -name '*__pycache__*' -exec rm -rf {} \;
	find . -d -name '*.pytest_cache*' -exec rm -rf {} \;
	cd docs && make clean

# Run all developer environment smoketests
developer-smoketests: smoketest-agave smoketest-config smoketest-google smoketest-mongo-local smoketest-pypi smoketest-dockerhub

# Verify usable TACC.cloud API client
smoketest-agave:
	python -m pytest -v --longrun -k agave_client_smoke $(PYTEST_SRC)

# Verify ../config.yml is loadable YAML
smoketest-config:
	python -m pytest -k config_yml_smoke $(PYTEST_SRC)

# Verify connection to MongoDB Docker container
smoketest-mongo-local:
	python -m pytest -v -k db_connection $(PYTEST_SRC)

# Verify Google service account is functional
smoketest-google:

# Verify PyPi
smoketest-pypi:

# Verify Dockerhub
smoketest-dockerhub:

challenge_problems:
	python -m scripts.build_challenge_problems

experiment_designs: challenge_problems
	python -m scripts.build_experiment_designs

.PHONY: schemas
schemas: schemas-build schemas-validate

# Generate new build of ../schemas/
schemas-build:
	python -m scripts.build_schemas

# schemas can be built (does not overwrite ../schemas/)
schemas-test:
	LOCALONLY=1 MAKETESTS=1 python scripts/build_schemas.py

# Contents of ../schemas/ are conformant JSON schema draft-04+
schemas-validate:
	python -m pytest -v --longrun -k validate_all_schemas $(PYTEST_SRC)

# Exemplar files from formats.runners validate to sample_set.json
schemas-validate-products:
	python -m pytest -v --networked -k validate_jsonschema $(PYTEST_SRC)

# Remove all built JSON schema files
schemas-clean:
	rm -rf schemas/*.jsonschema

# Start local Mongo service
mongo-up:
	cd docker && docker-compose up -d --force-recreate --quiet-pull

# Stop local Mongo service
mongo-down:
	cd docker && docker-compose down

# Activate tests marked with @longrun
tests-longrun:
	python -m pytest --longrun $(PYTEST_RUN_OPTS) $(PYTEST_SRC)

# Activate tests marked with @networked
tests-networked:
	python -m pytest --networked $(PYTEST_RUN_OPTS) $(PYTEST_SRC)

# Generic all tests
.PHONY: tests
tests:
	python -m pytest $(PYTEST_RUN_OPTS) $(PYTEST_OPTS) $(PYTEST_SRC)

# Test detection of lab trace formats
tests-formats-classify:
	python -m pytest $(PYTEST_RUN_OPTS) -k "formats_classify" $(PYTEST_SRC)

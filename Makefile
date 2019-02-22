PYTEST_OPTS ?=
PYTEST_SRC ?= tests/
# PYTEST_RUN_OPTS ?= -s -vvv
PYTEST_MAX_FAIL ?= 100
PYTEST_FAIL_OPTS ?= --maxfail=$(PYTEST_MAX_FAIL)
PYTEST_RUN_OPTS ?= -s $(PYTEST_FAIL_OPTS)
EXPORTS ?= challenge_problem experiment_design

# <empty> -staging or -production
DB_ENV ?= -localhost

all: build

# Generic all docs
.PHONY: docs

docs: docs-sphinx docs-fsm-png

docs-sphinx:
	cd docs && make html

# Init automatic API documentation
docs-autodoc: uml
	cd docs && sphinx-apidoc --maxdepth 1 -M -H "API Reference" -f -o source ../datacatalog
	if [ -f "uml/classes.png" ]; then cp "uml/classes.png" docs/source; fi

docs-clean:
	cd docs && make clean

docs-fsm-png:
	python -m scripts.build_fsm_graph --filename docs/pipelines/fsm --title "PipelineJob States Diagram"

deps: deps-mac

deps-mac:
	brew install libmagic
	brew install shared-mime-info

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

# Run all developer environment smoketests
developer-smoketests: smoketest-virtualenv smoketest-agave smoketest-config smoketest-google smoketest-mongo-local smoketest-pypi smoketest-dockerhub

user-smoketests: smoketest-virtualenv smoketest-agave smoketest-mongo-local
# Verify usable TACC.cloud API client
smoketest-agave:
	python -m pytest --bootstrap -v --longrun -k agave_client_smoke $(PYTEST_SRC)

# Verify ../config.yml is loadable YAML
smoketest-config:
	python -m pytest --bootstrap -k config_yml_smoke $(PYTEST_SRC)

# Verify connection to MongoDB Docker container
smoketest-mongo-local:
	python -m pytest --bootstrap -v -k db_connection $(PYTEST_SRC)

# Verify Google service account is functional
smoketest-google:
	python -m pytest --bootstrap --networked -v -k gdrive_smoke $(PYTEST_SRC)

.SILENT: smoketest-virtualenv
smoketest-virtualenv:
	if [ -z "$(VIRTUAL_ENV)" ]; then \
		echo "No Python virtualenv is active\n"; \
		echo "Example setup instructions:"; \
		echo "% virtualenv <env>; source <env>/bin/activate; pip install --upgrade -r requirements.txt\n"; \
		echo "Example load instructions:" ;\
		echo "% source <env>/bin/activate\n"; \
		exit 1; fi

# Verify PyPi
smoketest-pypi:

# Verify Dockerhub
smoketest-dockerhub:

# Update actual database
challenge_problems:
	python -m scripts.build_challenge_problems $(DB_ENV)

experiment_designs:
	python -m scripts.build_experiment_designs $(DB_ENV)

# Regenerates the schema tree, including a sync w Google
.PHONY: schemas
schemas: challenge_problems experiment_designs schemas-build schemas-validate

# Generate new build of ../schemas/
schemas-build:
	python -m scripts.build_schemas

# schemas can be built (does not overwrite ../schemas/)
schemas-test:
	LOCALONLY=1 MAKETESTS=1 python -m scripts.build_schemas

# Contents of ../schemas/ are conformant JSON schema draft-04+
schemas-validate:
	python -m pytest -v --networked -k validate_allschemas $(PYTEST_SRC)

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
	python -m pytest --longrun $(PYTEST_RUN_OPTS) $(PYTEST_OPTS) $(PYTEST_SRC)

# Activate tests marked with @networked
tests-networked:
	python -m pytest --networked $(PYTEST_RUN_OPTS) $(PYTEST_OPTS) $(PYTEST_SRC)

tests-import-from-bootstrap-dirs:
	cp -rf bootstrap/files/* tests/data/file/files/
	cp -rf bootstrap/pipelines/* tests/data/pipeline/
#	cp bootstrap/jobs/* tests/data/pipelinejob/

# Generic all tests
.PHONY: tests
tests:
	python -m pytest $(PYTEST_RUN_OPTS) $(PYTEST_OPTS) $(PYTEST_SRC)

# Test detection of lab trace formats
tests-formats-classify:
	python -m pytest $(PYTEST_RUN_OPTS) -k "formats_classify" $(PYTEST_SRC)

# This is a set of targets to bring up a fresh catalog defined by the code repo

bootstrap-tests: bootstrap bootstrap-extras

bootstrap: bootstrap-database bootstrap-references bootstrap-pipelines bootstrap-views bootstrap-schemas
bootstrap-extras: bootstrap-challenge-problems-extra bootstrap-experiment-designs-extra bootstrap-experiments-extra bootstrap-samples-extra bootstrap-measurements-extra bootstrap-files-extra

bootstrap-google: bootstrap-challenge-problems bootstrap-experiment-designs
bootstrap-mongodb: bootstrap-database bootstrap-references bootstrap-files bootstrap-pipelines bootstrap-views

bootstrap-database:
	python -m bootstrap.create_database $(DB_ENV)

bootstrap-challenge-problems: challenge_problems
bootstrap-challenge-problems-extra:
	python -m bootstrap.manage_challenges auto $(DB_ENV)

bootstrap-experiment-designs: experiment_designs
bootstrap-experiment-designs-extra:
	python -m bootstrap.manage_experiment_designs auto $(DB_ENV)

bootstrap-experiments:
	python -m bootstrap.manage_experiments auto $(DB_ENV)

bootstrap-experiments-extra: bootstrap-experiments

bootstrap-samples:
	python -m bootstrap.manage_samples auto $(DB_ENV)

bootstrap-samples-extra: bootstrap-samples

bootstrap-measurements:
	python -m bootstrap.manage_measurements auto $(DB_ENV)

bootstrap-measurements-extra: bootstrap-measurements

bootstrap-references:
	python -m bootstrap.manage_references auto $(DB_ENV)

bootstrap-references-extra: bootstrap-references

bootstrap-files:
	python -m bootstrap.manage_files auto $(DB_ENV)

bootstrap-files-extra: bootstrap-files

bootstrap-pipelines:
	python -m bootstrap.manage_pipelines auto $(DB_ENV)

bootstrap-processes:
	python -m bootstrap.manage_processes auto $(DB_ENV)

bootstrap-views:
	python -m bootstrap.manage_views auto $(DB_ENV)

bootstrap-schemas: schemas-build

# Currently, export values from production to enviromnent to bootstrap directories
exports:
	for C in $(EXPORTS); do python -m scripts.export_collection $$C -production -o "bootstrap/$${C}s/production-export.json"; done

.PHONY: uml
uml:
	cd uml && pyreverse -o png ../datacatalog

virtualenv:
	virtualenv env && \
	source env/bin/activate && \
	pip install --upgrade -r requirements.txt

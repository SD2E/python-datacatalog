PYTEST_OPTS ?= ""
PYTEST_SRC ?= tests


all: build

release: build
	twine upload dist/*

build:
	python3 setup.py sdist bdist_wheel

clean:
	rm -rf build *egg-info dist
	find . -d -name '*__pycache__*' -exec rm -rf {} \;

tests:

tests-classify:
	python -m pytest -s -vvv -k "format_imports" $(PYTEST_SRC)

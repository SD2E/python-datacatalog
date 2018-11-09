all: build

release: build
	twine upload dist/*

build:
	python3 setup.py sdist bdist_wheel

clean:
	rm -rf build *egg-info dist

tests:

tests-classify:
	pytest  -k "format_imports" tests

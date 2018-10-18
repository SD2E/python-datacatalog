all: build

release: build
	twine upload dist/*

build:
	python3 setup.py sdist bdist_wheel

clean:
	rm -rf build *egg-info dist

schemas-build: schemas-clean
	python scripts/build_schemas.py

schemas-clean:
	rm -rf schemas/*.jsonschema

mongodb-up:
	cd docker && docker-compose up -d --force-recreate --quiet-pull

mongodb-down:
	cd docker && docker-compose down

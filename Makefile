.PHONY: configure build test python-test lint doctor clean

configure:
	cmake --preset dev

build: configure
	cmake --build --preset dev

test: build
	ctest --preset dev
	python -m pytest

python-test:
	python -m pytest

lint:
	python -m ruff check python scripts
	python -m mypy python/opencuda

doctor:
	python scripts/opencuda_doctor.py

clean:
	cmake -E remove_directory build

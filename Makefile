# Makefile for gopass-utils
# Assumes you are inside packaging311-venv


PROJECT_NAME = gopass-utils
PYTHON = python3

.PHONY: clean build check upload

clean:
	rm -rf dist build *.egg-info

check:
	check-manifest
	validate-pyproject

build: clean check
	python -m build

validate: build
	twine check dist/*

upload: validate
	twine upload dist/*

all: clean build validate

# Help display
help:
	@echo "Usage:"
	@echo "  make clean      # Clean all build artifacts"
	@echo "  make check      # Check manifest and validate pyproject"
	@echo "  make build      # Build PyPI artifacts (sdist + wheel)"
	@echo "  make validate   # Validate PyPI files"
	@echo "  make all        # Clean + Build + Validate"
	@echo "  make help       # Show this help"

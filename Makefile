PYTHON = python3

install:
	$(PYTHON) -m pip install flake8 mypy

run:
	$(PYTHON) a_maze_ing.py config.txt

debug:
	$(PYTHON) -m pdb a_maze_ing.py config.txt

clean:
	rm -rf __pycache__ .mypy_cache build *.egg-info

lint:
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs

lint-strict:
	flake8 .
	mypy . --strict

build:
	$(PYTHON) -m pip wheel . --no-deps --wheel-dir .
	rm -rf build *.egg-info

.PHONY: install run debug clean lint lint-strict build

.PHONY: all clean lint type test test-cov

CMD:=poetry run
PYMODULE:=src
TESTS:=tests

all: type test lint

lint:
	$(CMD) flake8 $(PYMODULE) $(TESTS) $(EXTRACODE)

type:
	$(CMD) mypy $(PYMODULE) $(TESTS) $(EXTRACODE)

test:
	$(CMD) pytest --cov=$(PYMODULE) $(TESTS)

test-cov:
	$(CMD) pytest --cov=$(PYMODULE) $(TESTS) --cov-report html

black:
	$(CMD) black $(PYMODULE) $(TESTS)

isort:
	$(CMD) isort $(PYMODULE) $(TESTS)

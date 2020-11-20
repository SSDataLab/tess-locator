.PHONY: all clean lint type test test-cov black isort

CMD:=poetry run
PYMODULE:=src
TESTS:=tests

all: type test lint

lint:
	$(CMD) flake8 $(PYMODULE) $(TESTS) --max-line-length=127

type:
	$(CMD) mypy $(PYMODULE) $(TESTS)

test:
	$(CMD) pytest --cov=$(PYMODULE) $(TESTS)

test-cov:
	$(CMD) pytest --cov=$(PYMODULE) $(TESTS) --cov-report html

black:
	$(CMD) black $(PYMODULE) $(TESTS)

isort:
	$(CMD) isort $(PYMODULE) $(TESTS)

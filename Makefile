PYTHON ?= python3

.PHONY: help test clean

help:
	@printf '%s\n' \
		'test  Run unit tests' \
		'clean Remove build artifacts and caches'

test:
	$(PYTHON) -m unittest discover -s tests -v

clean:
	rm -rf build dist .pytest_cache .coverage .coverage.* *.egg-info searp_sdk.egg-info
	find . -type d -name '__pycache__' -prune -exec rm -rf {} +

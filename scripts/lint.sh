#!/bin/bash

declare -i e=0

flake8 || ((++e))
isort -q -c --df . || ((++e))
mypy --no-error-summary . || ((++e))
bandit -c pyproject.toml -r . || ((++e))

exit $e

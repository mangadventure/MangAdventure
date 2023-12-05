#!/bin/bash

declare -i e=0

flake8 || ((e+=1))
isort -q -c --df . || ((e+=2))
mypy --no-error-summary . || ((e+=4))
bandit -q -c pyproject.toml -r . || ((e+=8))

exit $e

#!/usr/bin/env python

from subprocess import run

run("python -m piptools compile -o requirements.txt pyproject.toml")
run("python -m piptools compile --extra dev -o requirements-dev.txt pyproject.toml")
run("python -m piptools compile --extra package -o requirements-package.txt pyproject.toml")

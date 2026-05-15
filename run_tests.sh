#!/usr/bin/env bash

source venv/bin/activate
tox run -m tests
deactivate

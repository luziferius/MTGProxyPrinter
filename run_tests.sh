#!/bin/bash

source venv/bin/activate
tox run -m tests
deactivate

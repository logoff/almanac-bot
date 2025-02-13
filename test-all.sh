#!/usr/bin/env bash
set -xe
python -m compileall -f almanacbot -q
ruff check

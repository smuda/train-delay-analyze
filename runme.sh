#!/bin/sh
set -e
cd "$(dirname "$0")"

if [ -f .env ]; then
    set -a
    . ./.env
    set +a
fi

git pull --ff-only
.venv/bin/python report.py

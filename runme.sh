#!/bin/sh
set -e
cd "$(dirname "$0")"

if [ -f .env ]; then
    set -a
    . ./.env
    set +a
fi

.venv/bin/python fetch.py
git add data/raw
git diff --cached --quiet data/raw || git commit -m "chore: add raw trip files" -- data/raw
.venv/bin/python report.py

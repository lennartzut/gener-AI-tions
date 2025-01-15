#!/bin/bash
set -e

# 1) Run migrations
alembic upgrade head

# 2) Start the Gunicorn server
gunicorn run:app --bind 0.0.0.0:$PORT --workers 3

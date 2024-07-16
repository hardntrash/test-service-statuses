#!/bin/bash

alembic upgrade head
python -m uvicorn core.main:application --host 0.0.0.0 --port=8000 --reload

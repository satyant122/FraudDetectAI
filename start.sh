#!/bin/sh
set -e

# Run alembic migrations
alembic upgrade head || true

if [ "$APP_MODE" = "api" ]; then
    echo "Starting FastAPI Banking API on port 8000..."
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000
elif [ "$APP_MODE" = "streamlit" ]; then
    echo "Starting Streamlit App on port 8501..."
    exec streamlit run app/streamlit_app.py --server.port 8501 --server.address 0.0.0.0
else
    echo "Starting FastAPI Banking API on port 8000 (background)..."
    uvicorn app.main:app --host 0.0.0.0 --port 8000 &
    echo "Starting Streamlit Web Dashboard on port 8501..."
    exec streamlit run app/streamlit_app.py --server.port 8501 --server.address 0.0.0.0
fi

#!/bin/bash

echo "🚀 Starting AI Code Assistant..."

# Start FastAPI in background
echo "Starting FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &

# Wait a moment for FastAPI to start
sleep 3

# Start Streamlit
echo "Starting Streamlit frontend..."
streamlit run frontend/streamlit_app.py --server.port 8501 --server.address 0.0.0.0

# Keep container running
wait
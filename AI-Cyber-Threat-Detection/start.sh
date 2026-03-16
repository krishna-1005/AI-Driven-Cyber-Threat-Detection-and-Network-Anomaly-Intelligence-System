#!/bin/bash

# Port mapping for Render
PORT=${PORT:-10000}

echo "Starting Production Flask Backend..."
# Single worker to save memory, no daemon to let Render manage the process
gunicorn --bind 0.0.0.0:5000 --chdir AI-Cyber-Threat-Detection/backend app:app --workers 1 --worker-class sync --timeout 60 &

echo "Waiting 10s for backend and ML models to load..."
sleep 10

echo "Starting Streamlit Dashboard..."
# Streamlit memory optimizations
streamlit run AI-Cyber-Threat-Detection/dashboard/dashboard.py \
    --server.port $PORT \
    --server.address 0.0.0.0 \
    --client.toolbarMode hidden \
    --browser.gatherUsageStats false

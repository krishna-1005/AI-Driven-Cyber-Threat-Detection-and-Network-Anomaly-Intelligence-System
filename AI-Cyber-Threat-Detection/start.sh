#!/bin/bash

echo "Starting Production Flask Backend..."
# Run backend with gunicorn for stability and lower memory overhead
gunicorn --bind 0.0.0.0:5000 --chdir AI-Cyber-Threat-Detection/backend app:app --daemon

echo "Waiting for backend to initialize..."
sleep 5

echo "Starting Streamlit Dashboard..."
# Streamlit runs on the port Render expects (10000)
streamlit run AI-Cyber-Threat-Detection/dashboard/dashboard.py --server.port 10000 --server.address 0.0.0.0

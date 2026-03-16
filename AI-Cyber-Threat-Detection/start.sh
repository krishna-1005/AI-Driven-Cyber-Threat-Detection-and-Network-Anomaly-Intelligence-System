#!/bin/bash

echo "Starting Flask API..."
python AI-Cyber-Threat-Detection/backend/app.py &

echo "Starting Traffic Simulator..."
python AI-Cyber-Threat-Detection/simulator/send_data.py &

echo "Starting Streamlit Dashboard..."
streamlit run AI-Cyber-Threat-Detection/dashboard/dashboard.py --server.port 10000 --server.address 0.0.0.0

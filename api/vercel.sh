#!/bin/bash
# Install Python dependencies
pip install -r requirements.txt

# Make sure PYTHONPATH includes the api directory
export PYTHONPATH="/var/task/api:$PYTHONPATH"

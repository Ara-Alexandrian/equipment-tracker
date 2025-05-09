#!/bin/bash
# Start script for Equipment Tracker

# Make sure we're in the right directory
cd "$(dirname "$0")"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not found."
    exit 1
fi

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Install requirements
    echo "Installing requirements..."
    pip install -r requirements.txt
else
    # Activate virtual environment
    source venv/bin/activate
fi

# Check if Resources directory exists and has files
if [ ! -d "Resources" ] || [ ! "$(ls -A Resources 2>/dev/null)" ]; then
    echo "Warning: Resources directory is empty or does not exist."
    echo "Please ensure you have the required Excel files in the Resources directory."
fi

# Create output directory if it doesn't exist
mkdir -p output

# Start the application
echo "Starting Equipment Tracker..."
echo "Open your browser and navigate to http://localhost:5000"
python run.py
#!/bin/bash
# Start script for Equipment Tracker

# Get directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Detect IP address
IP_ADDRESS=$(hostname -I | awk '{print $1}')
if [ -z "$IP_ADDRESS" ]; then
    IP_ADDRESS="localhost"
fi

# Set up environment - first try conda, then venv
if command -v conda &> /dev/null; then
    # Activate conda environment if it exists
    if conda env list | grep -q "equipment-tracker"; then
        echo "Activating conda environment 'equipment-tracker'..."
        source "$(conda info --base)/etc/profile.d/conda.sh"
        conda activate equipment-tracker
    else
        echo "Conda environment 'equipment-tracker' not found."
        
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
    fi
else
    # No conda, use venv
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
fi

# Check if Resources directory exists and has files
if [ ! -d "Resources" ] || [ ! "$(ls -A Resources 2>/dev/null)" ]; then
    echo "Warning: Resources directory is empty or does not exist."
    echo "Please ensure you have the required Excel files in the Resources directory."
fi

# Create output and logs directories if they don't exist
mkdir -p output
mkdir -p logs

# Set default host and port
HOST=${1:-0.0.0.0}
PORT=${2:-5000}

# Start the application
echo "Starting Equipment Tracker..."
echo "Access the application at:"
echo "  - Local:    http://localhost:$PORT"
echo "  - Network:  http://$IP_ADDRESS:$PORT"
echo "Press Ctrl+C to stop the server"

python run.py --host "$HOST" --port "$PORT"
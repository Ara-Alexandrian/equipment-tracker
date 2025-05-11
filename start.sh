#!/bin/bash
# Unified start script for Equipment Tracker application

# Default values
HOST="192.168.1.11"
PORT="8889"
DEBUG=0
CLEAR_CACHE=0

# Parse command line arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --debug)
      DEBUG=1
      shift
      ;;
    --port=*)
      PORT="${1#*=}"
      shift
      ;;
    --host=*)
      HOST="${1#*=}"
      shift
      ;;
    --ticket)
      PORT="8899"
      DEBUG=1
      shift
      ;;
    --clear-cache)
      CLEAR_CACHE=1
      shift
      ;;
    *)
      echo "Unknown parameter: $1"
      echo "Usage: $0 [--debug] [--port=PORT] [--host=HOST] [--ticket] [--clear-cache]"
      exit 1
      ;;
  esac
done

# Check if we need to add version timestamps to static files for cache busting
if [ $CLEAR_CACHE -eq 1 ]; then
  # Add a timestamp to each JS and CSS file reference in templates
  TIMESTAMP=$(date +%s)
  echo "Adding cache-busting timestamp ($TIMESTAMP) to static files..."

  # Create a backup of the equipment_management.html file
  cp app/templates/admin/equipment_management.html app/templates/admin/equipment_management.html.bak

  # Add debug message to the equipment_management.html file to verify it's being used
  echo "Adding debug markers to equipment_management.html..."
  sed -i "s/<h1>Equipment Management<\/h1>/<h1>Equipment Management (Updated: $TIMESTAMP)<\/h1>/" app/templates/admin/equipment_management.html
fi

# Build the command
if [ $DEBUG -eq 1 ]; then
  CMD="python run.py --host $HOST --port $PORT --debug"
else
  CMD="python run.py --host $HOST --port $PORT"
fi

# Run the application
echo "Starting Equipment Tracker on $HOST:$PORT (Debug: $DEBUG)"
$CMD
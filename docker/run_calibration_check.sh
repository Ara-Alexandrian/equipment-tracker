#!/bin/bash
# Daily calibration check script for Equipment Tracker
#
# This script runs the calibration notifier to check for upcoming or overdue calibrations
# and send email notifications to appropriate users.
#
# Recommended to be scheduled as a daily cron job:
# 0 8 * * * /path/to/equipment-tracker/cron_jobs/run_calibration_check.sh
#

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
# Get the parent directory (equipment tracker base directory)
BASE_DIR="$( dirname "$SCRIPT_DIR" )"

# Change to the base directory
cd $BASE_DIR

# Activate virtual environment if exists (uncomment if using venv)
# source venv/bin/activate

# Run the calibration notifier
echo "$(date) - Starting daily calibration check..."
python calibration_notifier.py >> logs/calibration_notifier.log 2>&1

# Check the exit status
if [ $? -eq 0 ]; then
    echo "$(date) - Daily calibration check completed successfully" >> logs/calibration_notifier.log
else
    echo "$(date) - ERROR: Daily calibration check failed" >> logs/calibration_notifier.log
fi

# Deactivate virtual environment if used (uncomment if using venv)
# deactivate
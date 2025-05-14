#!/usr/bin/env python3
"""
Calibration notification script for Equipment Tracker.
This script checks for equipment with upcoming or overdue calibrations
and sends email notifications to appropriate users.

Usage:
  python calibration_notifier.py [--debug]

Options:
  --debug    Run in debug mode without sending actual emails
"""
import os
import sys
import argparse
import json
import logging
from datetime import datetime
from app.models.json_utils import DateTimeEncoder
from app.models.json_equipment import JsonEquipmentDataManager
from app.utils.notifications.calibration_check import check_and_send_calibration_notifications

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('calibration_notifier')

def main():
    """Main function to check calibration and send notifications."""
    parser = argparse.ArgumentParser(description="Run calibration checks and send notifications")
    parser.add_argument('--debug', action='store_true', help='Run in debug mode (no emails)')
    args = parser.parse_args()
    
    # Set base directory
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Set data directories
    json_data_dir = os.path.join(base_dir, 'app', 'data')
    users_file_path = os.path.join(json_data_dir, 'users.json')
    
    # Check if data directory exists
    if not os.path.exists(json_data_dir):
        logger.error(f"Data directory not found at {json_data_dir}")
        sys.exit(1)
    
    # Debug mode settings update
    if args.debug:
        from app.utils.notifications.config import DEFAULT_SETTINGS
        DEFAULT_SETTINGS['debug_mode'] = True
        logger.info("Running in DEBUG mode - no emails will be sent")
    
    # Initialize equipment manager
    equipment_manager = JsonEquipmentDataManager(json_data_dir)
    
    # Run calibration check and send notifications
    logger.info("Starting calibration check...")
    
    # Track start time
    start_time = datetime.now()
    
    # Send notifications
    result = check_and_send_calibration_notifications(equipment_manager, users_file_path)
    
    # Calculate duration
    duration = (datetime.now() - start_time).total_seconds()
    
    # Log results
    if result['sent'] > 0:
        logger.info(f"Sent {result['sent']} notifications to {result['users']} users "
                   f"for {result['items']} equipment items in {duration:.2f} seconds")
    else:
        logger.info(f"No notifications sent. Checked {result['items']} equipment items "
                  f"for {result['users']} users in {duration:.2f} seconds")
    
    # Save notification log
    log_file = os.path.join(json_data_dir, 'notification_logs.json')
    
    try:
        # Load existing logs
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                logs = json.load(f)
        else:
            logs = []
        
        # Add this run's log
        logs.append({
            'timestamp': datetime.now().isoformat(),
            'notifications_sent': result['sent'],
            'users_notified': result['users'],
            'items_included': result['items'],
            'duration_seconds': round(duration, 2),
            'debug_mode': args.debug
        })
        
        # Save logs (keep only last 100 entries)
        with open(log_file, 'w') as f:
            json.dump(logs[-100:], f, cls=DateTimeEncoder, indent=2)
            
    except Exception as e:
        logger.error(f"Error saving notification log: {e}")

if __name__ == '__main__':
    main()
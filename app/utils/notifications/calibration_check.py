"""
Calibration check utility for identifying equipment that needs alerts.
"""
import json
import os
import logging
from datetime import datetime
from app.utils.notifications.config import get_notification_settings, get_users_to_notify
from app.utils.notifications.email_service import email_service

# Initialize logger
logger = logging.getLogger(__name__)

class CalibrationCheck:
    """Utility class for checking equipment calibration status and sending notifications."""
    
    def __init__(self, equipment_manager, users_file_path):
        """Initialize calibration check service.
        
        Args:
            equipment_manager: Equipment data manager instance
            users_file_path: Path to the users JSON file
        """
        self.equipment_manager = equipment_manager
        self.users_file_path = users_file_path
        self.settings = get_notification_settings()
        
    def load_users(self):
        """Load user data from JSON file.
        
        Returns:
            Dictionary of user data
        """
        try:
            if not os.path.exists(self.users_file_path):
                logger.warning(f"Users file not found at {self.users_file_path}")
                return {}
                
            with open(self.users_file_path, 'r') as f:
                return json.load(f)
                
        except Exception as e:
            logger.error(f"Error loading users data: {e}")
            return {}
    
    def check_calibration_status(self):
        """Check calibration status of all equipment.
        
        Returns:
            Tuple containing (due_soon_items, overdue_items)
        """
        # Get threshold from settings
        due_soon_threshold = self.settings.get('due_soon_threshold', 30)
        
        # Get equipment due soon and overdue
        due_soon_items = self.equipment_manager.get_calibration_due_soon(days=due_soon_threshold)
        
        # Split into due soon and overdue
        overdue_items = []
        actual_due_soon = []
        
        for item in due_soon_items:
            if item.get('calibration_status') == 'overdue':
                overdue_items.append(item)
            else:
                actual_due_soon.append(item)
        
        return actual_due_soon, overdue_items
    
    def prepare_notifications_by_user(self):
        """Prepare notifications grouped by user.
        
        Returns:
            Dictionary mapping email addresses to equipment lists 
            Format: {
                'user@example.com': {
                    'due_soon': [...],
                    'overdue': [...]
                }
            }
        """
        # Get equipment need notification
        due_soon_items, overdue_items = self.check_calibration_status()
        
        # Get users to notify
        users = self.load_users()
        users_to_notify = get_users_to_notify(users)
        
        # Group notifications by user
        notifications = {}
        
        for user in users_to_notify:
            email = user.get('email')
            if not email:
                continue
                
            notifications[email] = {
                'due_soon': due_soon_items if self.settings.get('send_due_soon_emails', True) else [],
                'overdue': overdue_items if self.settings.get('send_overdue_emails', True) else []
            }
        
        return notifications
    
    def send_notifications(self):
        """Send calibration notifications to users.
        
        Returns:
            Dictionary with notification statistics
        """
        # Prepare notifications by user
        notifications = self.prepare_notifications_by_user()
        
        # Check if any notifications need to be sent
        if not notifications:
            logger.info("No notifications to send.")
            return {'sent': 0, 'users': 0, 'items': 0}
        
        # Count items
        total_items = sum(
            len(data.get('due_soon', [])) + len(data.get('overdue', []))
            for data in notifications.values()
        )
        
        # Send notifications
        if self.settings.get('debug_mode', False):
            # In debug mode, just log instead of sending
            for email, data in notifications.items():
                logger.info(f"Would send notification to {email}: "
                           f"{len(data.get('due_soon', []))} due soon, "
                           f"{len(data.get('overdue', []))} overdue")
            results = {email: True for email in notifications}
        else:
            # Actually send the emails
            results = email_service.send_bulk_calibration_notification(notifications)
        
        # Count successes
        sent_count = sum(1 for success in results.values() if success)
        
        # Return statistics
        return {
            'sent': sent_count,
            'users': len(notifications),
            'items': total_items,
            'timestamp': datetime.now().isoformat()
        }


def check_and_send_calibration_notifications(equipment_manager, users_file_path):
    """Check calibration status and send notifications if needed.
    
    Args:
        equipment_manager: Equipment data manager instance
        users_file_path: Path to the users JSON file
        
    Returns:
        Dictionary with notification statistics
    """
    checker = CalibrationCheck(equipment_manager, users_file_path)
    return checker.send_notifications()
"""
Configuration settings for the notification system.
"""

# Default notification settings
DEFAULT_SETTINGS = {
    # Thresholds for calibration notifications (in days)
    'due_soon_threshold': 30,     # Send reminder when calibration due within 30 days
    'reminder_intervals': [30, 14, 7, 3, 1],  # Send reminders at these day intervals
    
    # Email notification settings
    'send_due_soon_emails': True,   # Send emails for due soon notifications
    'send_overdue_emails': True,    # Send emails for overdue notifications
    
    # User roles that should receive notifications
    'notify_roles': ['admin', 'physicist'],
    
    # Email subject prefixes
    'email_subject_prefix': '[Equipment Tracker] ',
    
    # Application URL (for links in notifications)
    'application_url': 'http://localhost:5000',
    
    # Debug mode - print notifications instead of sending emails
    'debug_mode': False
}


def get_notification_settings():
    """Get the current notification settings.
    
    Returns:
        Dictionary containing notification settings
    """
    return DEFAULT_SETTINGS.copy()


def get_users_to_notify(user_data):
    """Get a list of users who should receive notifications.
    
    Args:
        user_data: Dictionary of user data
        
    Returns:
        List of user dictionaries with notification settings
    """
    settings = get_notification_settings()
    notify_roles = settings.get('notify_roles', ['admin', 'physicist'])
    
    users_to_notify = []
    
    for username, user in user_data.items():
        # Skip users without email or with notifications disabled
        if not user.get('email') or user.get('notifications_disabled', False):
            continue
            
        # Check if user's role should receive notifications
        if user.get('role') in notify_roles:
            users_to_notify.append(user)
    
    return users_to_notify
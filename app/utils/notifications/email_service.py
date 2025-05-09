"""
Email notification service for Equipment Tracker.
Provides functionality to send email notifications for calibration alerts.
"""
from flask import current_app, render_template
from flask_mail import Mail, Message
import logging
from datetime import datetime
import os

# Initialize logger
logger = logging.getLogger(__name__)

class EmailService:
    """Email notification service for sending calibration alerts."""
    
    def __init__(self, app=None):
        """Initialize the email service.
        
        Args:
            app: Flask application instance
        """
        self.mail = Mail()
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize the service with the Flask app.
        
        Args:
            app: Flask application instance
        """
        # Check if mail settings are configured
        if not app.config.get('MAIL_SERVER'):
            app.config.setdefault('MAIL_SERVER', os.environ.get('MAIL_SERVER', 'smtp.marybird.com'))
            app.config.setdefault('MAIL_PORT', os.environ.get('MAIL_PORT', 587))
            app.config.setdefault('MAIL_USE_TLS', os.environ.get('MAIL_USE_TLS', True))
            app.config.setdefault('MAIL_USE_SSL', os.environ.get('MAIL_USE_SSL', False))
            app.config.setdefault('MAIL_USERNAME', os.environ.get('MAIL_USERNAME', None))
            app.config.setdefault('MAIL_PASSWORD', os.environ.get('MAIL_PASSWORD', None))
            app.config.setdefault('MAIL_DEFAULT_SENDER', 
                                 os.environ.get('MAIL_DEFAULT_SENDER', 'equipment-tracker@marybird.com'))
            app.config.setdefault('MAIL_MAX_EMAILS', os.environ.get('MAIL_MAX_EMAILS', None))
            app.config.setdefault('MAIL_ASCII_ATTACHMENTS', os.environ.get('MAIL_ASCII_ATTACHMENTS', False))
        
        self.mail.init_app(app)
    
    def send_email(self, subject, recipients, template_name, **kwargs):
        """Send an email using a template.
        
        Args:
            subject: Email subject
            recipients: List of email recipients
            template_name: Name of the email template to use
            **kwargs: Additional context variables for the template
        
        Returns:
            Boolean indicating if the email was sent successfully
        """
        try:
            # Create message
            msg = Message(
                subject,
                recipients=recipients,
                sender=current_app.config.get('MAIL_DEFAULT_SENDER')
            )
            
            # Render template for both HTML and text parts
            msg.html = render_template(f'emails/{template_name}.html', **kwargs)
            msg.body = render_template(f'emails/{template_name}.txt', **kwargs)
            
            # Send email
            self.mail.send(msg)
            
            logger.info(f"Email sent to {', '.join(recipients)} with subject '{subject}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def send_calibration_due_notification(self, user_email, equipment_items):
        """Send email notification for equipment with calibration due soon.
        
        Args:
            user_email: Email address of the recipient
            equipment_items: List of equipment items that need calibration
        
        Returns:
            Boolean indicating if the email was sent successfully
        """
        return self.send_email(
            subject="Equipment Calibration Reminder",
            recipients=[user_email],
            template_name="calibration_reminder",
            equipment=equipment_items,
            timestamp=datetime.now(),
            app_url=current_app.config.get('APPLICATION_URL', 'http://localhost:5000')
        )
    
    def send_calibration_overdue_notification(self, user_email, equipment_items):
        """Send email notification for equipment with calibration overdue.
        
        Args:
            user_email: Email address of the recipient
            equipment_items: List of equipment items with overdue calibration
        
        Returns:
            Boolean indicating if the email was sent successfully
        """
        return self.send_email(
            subject="URGENT: Equipment Calibration Overdue",
            recipients=[user_email],
            template_name="calibration_overdue",
            equipment=equipment_items,
            timestamp=datetime.now(),
            app_url=current_app.config.get('APPLICATION_URL', 'http://localhost:5000')
        )
    
    def send_bulk_calibration_notification(self, notifications):
        """Send calibration notifications in bulk.
        
        Args:
            notifications: Dict mapping email addresses to equipment lists
                Format: {
                    'user@example.com': {
                        'due_soon': [...],
                        'overdue': [...]
                    }
                }
        
        Returns:
            Dict with email addresses and success status
        """
        results = {}
        
        for email, data in notifications.items():
            due_soon = data.get('due_soon', [])
            overdue = data.get('overdue', [])
            success = True
            
            # Send overdue notifications
            if overdue:
                overdue_success = self.send_calibration_overdue_notification(email, overdue)
                success = success and overdue_success
            
            # Send due soon notifications
            if due_soon:
                due_soon_success = self.send_calibration_due_notification(email, due_soon)
                success = success and due_soon_success
            
            results[email] = success
        
        return results


# Create a singleton instance
email_service = EmailService()
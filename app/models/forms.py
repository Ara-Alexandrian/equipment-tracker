"""
Forms for Equipment Tracker
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Email, Optional, NumberRange, Length

class LoginForm(FlaskForm):
    """Login form."""
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')

class NotificationPreferencesForm(FlaskForm):
    """Form for user notification preferences."""
    receive_due_soon = BooleanField('Receive notifications for equipment due for calibration soon')
    receive_overdue = BooleanField('Receive notifications for equipment with overdue calibration')
    days_before_due = IntegerField('Days before due date to receive notifications', 
                                validators=[NumberRange(min=1, max=90)],
                                default=30)
    email_format = SelectField('Email Format', 
                             choices=[('html', 'HTML (Rich formatting)'), 
                                      ('text', 'Plain Text')])
    
class UserProfileForm(FlaskForm):
    """Form for editing user profile."""
    name = StringField('Full Name', validators=[DataRequired(), Length(min=2, max=100)])
    email = StringField('Email Address', validators=[DataRequired(), Email()])
    role = SelectField('Role', choices=[('admin', 'Administrator'), 
                                       ('physicist', 'Physicist'), 
                                       ('user', 'Regular User')])
    password = PasswordField('New Password (leave blank to keep current)')
    confirm_password = PasswordField('Confirm New Password')
    
class EquipmentCheckoutForm(FlaskForm):
    """Form for equipment checkout."""
    location = StringField('Location', validators=[DataRequired()])
    expected_return = StringField('Expected Return Date/Time', validators=[DataRequired()])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=500)])
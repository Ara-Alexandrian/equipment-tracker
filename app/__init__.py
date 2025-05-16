"""
GearVue Flask Application
"""
from flask import Flask, session, json, request
from flask_mail import Mail
from flask_wtf.csrf import CSRFProtect
from app.models.equipment import EquipmentDataManager
from app.models.json_equipment import JsonEquipmentDataManager
from app.models.json_checkout import JsonCheckoutManager
from app.models.json_utils import DateTimeEncoder
from app.models.standard_values import StandardValuesManager
from app.utils.notifications.email_service import email_service
import datetime
import os

# Configure Flask's JSON encoder to handle datetime objects
json.JSONEncoder = DateTimeEncoder

# Create Flask application
app = Flask(__name__)
app.config.from_mapping(
    SECRET_KEY='dev',
    DATA_DIR='Resources',
    JSON_DATA_DIR='app/data',
    SESSION_PERMANENT=True,
    PERMANENT_SESSION_LIFETIME=datetime.timedelta(days=7),
    # Disable CSRF protection globally for easy mobile access
    WTF_CSRF_ENABLED=False,

    # Email configuration (override with environment variables in production)
    MAIL_SERVER=os.environ.get('MAIL_SERVER', 'smtp.marybird.com'),
    MAIL_PORT=int(os.environ.get('MAIL_PORT', 587)),
    MAIL_USE_TLS=os.environ.get('MAIL_USE_TLS', 'True').lower() in ['true', '1', 't'],
    MAIL_USE_SSL=os.environ.get('MAIL_USE_SSL', 'False').lower() in ['true', '1', 't'],
    MAIL_USERNAME=os.environ.get('MAIL_USERNAME', None),
    MAIL_PASSWORD=os.environ.get('MAIL_PASSWORD', None),
    MAIL_DEFAULT_SENDER=os.environ.get('MAIL_DEFAULT_SENDER', 'gearvue@marybird.com'),

    # Application URL for links in notifications
    APPLICATION_URL=os.environ.get('APPLICATION_URL', 'http://localhost:5000'),

    # Automatic report configuration
    AUTO_REPORTS_ENABLED=os.environ.get('AUTO_REPORTS_ENABLED', 'True').lower() in ['true', '1', 't'],
    AUTO_REPORTS_STORAGE_PATH=os.environ.get('AUTO_REPORTS_STORAGE_PATH', 'reports/auto')
)

# Ensure JSON data directory exists
os.makedirs(app.config['JSON_DATA_DIR'], exist_ok=True)

# Initialize data managers
# Legacy Excel-based equipment manager
excel_equipment_manager = EquipmentDataManager(app.config['DATA_DIR'])

# New JSON-based managers
equipment_manager = JsonEquipmentDataManager(app.config['JSON_DATA_DIR'])
checkout_manager = JsonCheckoutManager(app.config['JSON_DATA_DIR'])
standard_values_manager = StandardValuesManager(app.config['JSON_DATA_DIR'])

# Initialize Flask-Mail
mail = Mail(app)

# Initialize CSRF protection but disable it for QR code landing pages
csrf = CSRFProtect()
# We're not initializing CSRFProtect with our app to disable CSRF site-wide temporarily

# Initialize email notification service
email_service.init_app(app)

# Import and register routes
from app.routes import dashboard, api, checkout, visual, reports, admin, ticket, equipment_landing, qr_access
from app.routes import transport, qr_transport, auto_reports

app.register_blueprint(dashboard.bp)
app.register_blueprint(api.bp)
app.register_blueprint(checkout.bp)
app.register_blueprint(visual.bp)
app.register_blueprint(reports.bp)
app.register_blueprint(admin.bp)
app.register_blueprint(ticket.bp)
app.register_blueprint(equipment_landing.bp)
app.register_blueprint(qr_access.bp)
app.register_blueprint(transport.bp)
app.register_blueprint(qr_transport.bp)
app.register_blueprint(auto_reports.bp)

# Add template context processors
@app.context_processor
def inject_context():
    """Inject variables and functions into template context."""
    return {
        'now': datetime.datetime.now(),
        'user': session.get('user', None)
    }

# Add template filters
@app.template_filter('datetime')
def format_datetime(value, format='%Y-%m-%d %H:%M:%S'):
    """Format a datetime object or string as a string."""
    if not value:
        return ''
    if isinstance(value, str):
        try:
            value = datetime.datetime.fromisoformat(value)
        except (ValueError, TypeError):
            return value
    return value.strftime(format)

@app.template_filter('friendly_datetime')
def friendly_datetime(value):
    """Format a datetime object or string as MM/DD/YYYY HH:MM AM/PM."""
    if not value:
        return ''
    if isinstance(value, str):
        try:
            value = datetime.datetime.fromisoformat(value)
        except (ValueError, TypeError):
            # If conversion fails, try another approach by parsing ISO format
            if 'T' in value:
                parts = value.split('T')
                if len(parts) == 2:
                    date_parts = parts[0].split('-')
                    time_parts = parts[1].split(':')
                    if len(date_parts) == 3 and len(time_parts) >= 2:
                        # Build date string in MM/DD/YYYY format
                        date_str = f"{date_parts[1]}/{date_parts[2]}/{date_parts[0]}"

                        # Build time string in HH:MM AM/PM format
                        hour = int(time_parts[0])
                        am_pm = 'AM' if hour < 12 else 'PM'
                        display_hour = hour if hour <= 12 else hour - 12
                        display_hour = display_hour if display_hour != 0 else 12
                        time_str = f"{display_hour}:{time_parts[1]} {am_pm}"

                        return f"{date_str} {time_str}"
            return value

    # Format datetime object
    return value.strftime("%m/%d/%Y %I:%M %p")

@app.template_filter('from_iso_date')
def from_iso_date(value):
    """Convert ISO date string to datetime object."""
    if not value:
        return datetime.datetime.now()
    
    if isinstance(value, str):
        try:
            return datetime.datetime.fromisoformat(value.replace('Z', '+00:00'))
        except (ValueError, TypeError):
            return datetime.datetime.now()
    
    return value

# Define main route 
# Add special header for QR routes
@app.after_request
def add_response_headers(response):
    """Add response headers for security and caching."""
    # Explicitly disable login checks for QR routes
    if request.path.startswith('/qr/') or request.path.startswith('/equipment/'):
        # Special header to indicate no login required
        response.headers['X-No-Login-Required'] = 'True'

    # Add cache-busting headers to all responses
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    # Add a timestamp to force browser refresh
    response.headers['Last-Modified'] = datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')

    return response

@app.route('/')
def index():
    return dashboard.index()
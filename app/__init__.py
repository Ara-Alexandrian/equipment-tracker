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
    APPLICATION_URL=os.environ.get('APPLICATION_URL', 'http://localhost:5000')
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

app.register_blueprint(dashboard.bp)
app.register_blueprint(api.bp)
app.register_blueprint(checkout.bp)
app.register_blueprint(visual.bp)
app.register_blueprint(reports.bp)
app.register_blueprint(admin.bp)
app.register_blueprint(ticket.bp)
app.register_blueprint(equipment_landing.bp)
app.register_blueprint(qr_access.bp)

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
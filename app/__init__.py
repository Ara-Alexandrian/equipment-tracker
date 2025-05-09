"""
Equipment Tracker Flask Application
"""
from flask import Flask, session, json
from app.models.equipment import EquipmentDataManager
from app.models.json_equipment import JsonEquipmentDataManager
from app.models.json_checkout import JsonCheckoutManager
from app.models.json_utils import DateTimeEncoder
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
    PERMANENT_SESSION_LIFETIME=datetime.timedelta(days=7)
)

# Ensure JSON data directory exists
os.makedirs(app.config['JSON_DATA_DIR'], exist_ok=True)

# Initialize data managers
# Legacy Excel-based equipment manager
excel_equipment_manager = EquipmentDataManager(app.config['DATA_DIR'])

# New JSON-based managers
equipment_manager = JsonEquipmentDataManager(app.config['JSON_DATA_DIR'])
checkout_manager = JsonCheckoutManager(app.config['JSON_DATA_DIR'])

# Import and register routes
from app.routes import dashboard, api, checkout, visual, reports

app.register_blueprint(dashboard.bp)
app.register_blueprint(api.bp)
app.register_blueprint(checkout.bp)
app.register_blueprint(visual.bp)
app.register_blueprint(reports.bp)

# Add template context processors
@app.context_processor
def inject_context():
    """Inject variables and functions into template context."""
    return {
        'now': datetime.datetime.now(),
        'user': session.get('user', None)
    }

# Define main route 
@app.route('/')
def index():
    return dashboard.index()
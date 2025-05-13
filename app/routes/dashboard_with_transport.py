"""
Dashboard routes with transport request integration
"""
from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from app import equipment_manager, checkout_manager
from app.models.ticket import TicketManager, EquipmentCondition
from app.models.transport_request import TransportManager  # New import
import os

bp = Blueprint('dashboard_transport', __name__, url_prefix='/dashboard-transport')

# Initialize managers
ticket_manager = TicketManager()
transport_manager = TransportManager()  # New transport manager instance

def login_required(view):
    """View decorator that redirects anonymous users to the login page."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('checkout.login', next=request.url))
        return view(**kwargs)
    return wrapped_view

@bp.route('/')
@login_required
def index():
    """Dashboard home page."""
    # Get total equipment count
    all_equipment = equipment_manager.get_all_equipment()
    
    # Get equipment that needs calibration soon
    calibration_due_soon = equipment_manager.get_calibration_due_soon(days=30)
    
    # Get checked out equipment
    checked_out = checkout_manager.get_checked_out_equipment()
    
    # Get open tickets
    open_tickets = ticket_manager.get_tickets_by_status('open')
    
    # Get in-progress transport requests
    transport_requests = transport_manager.get_pending_transport_requests()
    
    # Get equipment with warning or critical condition
    equipment_warning = ticket_manager.get_equipment_with_condition(EquipmentCondition.WARNING)
    equipment_critical = ticket_manager.get_equipment_with_condition(EquipmentCondition.CRITICAL)
    
    stats = {
        'total_equipment': len(all_equipment),
        'checked_out': len(checked_out),
        'calibration_due': len(calibration_due_soon),
        'open_tickets': len(open_tickets),
        'transport_requests': len(transport_requests),  # New stat
        'equipment_warning': len(equipment_warning),
        'equipment_critical': len(equipment_critical)
    }
    
    return render_template('dashboard/index.html', 
                          stats=stats,
                          calibration_due_soon=calibration_due_soon[:5],
                          checked_out=checked_out[:5],
                          open_tickets=open_tickets[:5],
                          transport_requests=transport_requests[:5],  # New data for template
                          equipment_warning=equipment_warning,
                          equipment_critical=equipment_critical)

@bp.route('/equipment')
@login_required
def equipment_list():
    """List all equipment."""
    # Get all equipment
    all_equipment = equipment_manager.get_all_equipment()
    
    # Get filter parameters
    category = request.args.get('category', '')
    location = request.args.get('location', '')
    query = request.args.get('query', '')
    
    # Apply filters
    filtered_equipment = all_equipment
    
    if category:
        filtered_equipment = [e for e in filtered_equipment if e.get('category') == category]
    
    if location:
        filtered_equipment = [e for e in filtered_equipment if location.lower() in (e.get('location') or '').lower()]
    
    if query:
        filtered_equipment = equipment_manager.search_equipment(query)
    
    # Get unique values for filters
    categories = sorted(set(e.get('category') for e in all_equipment if e.get('category')))
    locations = equipment_manager.get_unique_locations()
    
    return render_template('dashboard/equipment_list.html', 
                          equipment=filtered_equipment,
                          categories=categories,
                          locations=locations,
                          current_filters={
                              'category': category,
                              'location': location,
                              'query': query
                          })

@bp.route('/equipment/<string:equipment_id>')
@login_required
def equipment_detail(equipment_id):
    """Equipment detail page with transport integration."""
    # Get equipment details
    equipment = equipment_manager.get_equipment_by_id(equipment_id)
    
    if not equipment:
        flash('Equipment not found', 'error')
        return redirect(url_for('dashboard.equipment_list'))
    
    # Get checkout history
    checkout_history = checkout_manager.get_checkout_history(equipment_id=equipment_id, limit=10)
    
    # Get condition from ticket system
    condition = ticket_manager.get_equipment_condition(equipment_id)
    
    # Get tickets for this equipment
    tickets = ticket_manager.get_tickets_by_equipment(equipment_id)
    
    # Get transport requests for this equipment (NEW)
    transport_requests = transport_manager.get_requests_by_equipment(equipment_id)
    
    # Check if QR code exists
    qr_code_path = os.path.join('app', 'static', 'qrcodes', f'qr_{equipment_id}.png')
    qr_code_url = url_for('static', filename=f'qrcodes/qr_{equipment_id}.png') if os.path.exists(qr_code_path) else None
    
    return render_template('dashboard/equipment_detail_with_transport.html',  # New template with transport
                          equipment=equipment,
                          checkout_history=checkout_history,
                          condition=condition,
                          tickets=tickets,
                          transport_requests=transport_requests,  # New data
                          qr_code_url=qr_code_url,
                          checkout_manager=checkout_manager)

@bp.route('/calibration')
@login_required
def calibration():
    """Calibration tracking page."""
    # Get filter parameters
    status = request.args.get('status', '')
    
    # Get calibration data based on filter
    if status == 'overdue':
        calibration_equipment = [e for e in equipment_manager.get_calibration_due_soon() 
                               if e.get('calibration_status') == 'overdue']
    elif status == 'due_soon':
        calibration_equipment = [e for e in equipment_manager.get_calibration_due_soon() 
                               if e.get('calibration_status') == 'due_soon']
    else:
        calibration_equipment = equipment_manager.get_calibration_due_soon(days=90)
    
    # Transport-related calibration (NEW)
    calibration_transports = []
    for equipment in calibration_equipment:
        equipment_id = equipment.get('id')
        related_transports = transport_manager.get_requests_by_equipment(equipment_id)
        calibration_transports_for_equipment = [t for t in related_transports 
                                             if t.transport_type == 'calibration' and 
                                             t.status not in ['completed', 'cancelled']]
        if calibration_transports_for_equipment:
            equipment['has_transport_request'] = True
            equipment['transport_request'] = calibration_transports_for_equipment[0]
        else:
            equipment['has_transport_request'] = False
    
    return render_template('dashboard/calibration.html',
                          calibration_equipment=calibration_equipment,
                          current_filter=status)
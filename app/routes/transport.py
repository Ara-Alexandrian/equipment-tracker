"""
Transport request routes for equipment movement management
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app import equipment_manager, checkout_manager, csrf
from app.models.transport_request import (
    TransportManager, TransportStatus, TransportPriority, 
    TransportType, TransportRequest
)
import functools
from datetime import datetime, timedelta
import uuid

bp = Blueprint('transport', __name__, url_prefix='/transport')

# Initialize transport manager
transport_manager = TransportManager()

def login_required(view):
    """View decorator that redirects anonymous users to the login page."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('checkout.login', next=request.url))
        return view(**kwargs)
    return wrapped_view

def physicist_required(view):
    """View decorator that requires the user to be a physicist or administrator."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('checkout.login', next=request.url))
        
        user = session['user']
        if user['role'] not in ['admin', 'physicist']:
            flash('This action requires physicist or admin privileges.', 'error')
            return redirect(url_for('dashboard.index'))
        
        return view(**kwargs)
    return wrapped_view

@bp.route('/')
@login_required
def index():
    """Transport request dashboard"""
    # Get all pending transport requests
    pending_requests = transport_manager.get_pending_transport_requests()
    
    # Get requests created by current user
    user_requests = transport_manager.get_requests_by_user(session['user']['username'])
    
    # For physicists and admins, also get requests they're coordinating
    coordinator_requests = []
    if session['user']['role'] in ['admin', 'physicist']:
        coordinator_requests = transport_manager.get_requests_by_user(
            session['user']['username'], role="transport_coordinator"
        )
    
    # Get upcoming requests in the next 7 days
    upcoming_requests = transport_manager.get_upcoming_transport_requests(days=7)
    
    return render_template(
        'transport/index.html',
        pending_requests=pending_requests,
        user_requests=user_requests,
        coordinator_requests=coordinator_requests,
        upcoming_requests=upcoming_requests
    )

@bp.route('/create/<string:equipment_id>', methods=['GET', 'POST'])
@login_required
def create(equipment_id):
    """Create a new transport request"""
    # Get equipment details
    equipment = equipment_manager.get_equipment_by_id(equipment_id)
    
    if not equipment:
        flash('Equipment not found', 'error')
        return redirect(url_for('dashboard.index'))
    
    # Get equipment status
    status = checkout_manager.get_equipment_status(equipment_id)
    
    if request.method == 'POST':
        # Get form data
        origin = request.form.get('origin', status.get('location', 'Unknown'))
        destination = request.form.get('destination', '')
        requested_date_str = request.form.get('requested_date', '')
        transport_type = request.form.get('transport_type', TransportType.RELOCATION)
        priority = request.form.get('priority', TransportPriority.MEDIUM)
        special_instructions = request.form.get('special_instructions', '')
        
        # Validate required fields
        if not destination:
            flash('Destination is required', 'error')
            return redirect(url_for('transport.create', equipment_id=equipment_id))
        
        # Parse requested date if provided
        requested_date = None
        if requested_date_str:
            try:
                # Format expected: YYYY-MM-DD
                requested_date = datetime.strptime(requested_date_str, '%Y-%m-%d')
                # Set time to 10 AM
                requested_date = requested_date.replace(hour=10, minute=0, second=0)
            except ValueError:
                flash('Invalid date format. Please use YYYY-MM-DD', 'error')
                return redirect(url_for('transport.create', equipment_id=equipment_id))
        
        # Create the transport request
        transport_request = transport_manager.create_transport_request(
            equipment_id=equipment_id,
            origin=origin,
            destination=destination,
            requested_by=session['user']['username'],
            requested_date=requested_date,
            special_instructions=special_instructions,
            transport_type=transport_type,
            priority=priority
        )
        
        flash('Transport request created successfully', 'success')
        return redirect(url_for('transport.view', request_id=transport_request.id))
    
    # GET request - render the form
    # For select dropdowns, get standard values
    locations = equipment_manager.get_unique_locations()
    
    # Add current user's name to special instructions template
    user = session['user']
    contact_info = f"Contact: {user['name']}"
    
    return render_template(
        'transport/create.html',
        equipment=equipment,
        status=status,
        locations=locations,
        contact_info=contact_info,
        transport_types=vars(TransportType),
        transport_priorities=vars(TransportPriority),
        min_date=datetime.now().strftime('%Y-%m-%d'),
        default_date=(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    )

@bp.route('/view/<string:request_id>')
def view(request_id):
    """View transport request details"""
    # Get transport request
    transport_request = transport_manager.get_transport_request(request_id)
    
    if not transport_request:
        flash('Transport request not found', 'error')
        return redirect(url_for('transport.index'))
    
    # Get equipment details
    equipment = equipment_manager.get_equipment_by_id(transport_request.equipment_id)
    
    # Check if current user is coordinator or has permission to manage
    can_manage = False
    if 'user' in session:
        user = session['user']
        if (user['role'] in ['admin', 'physicist'] or 
            user['username'] == transport_request.transport_coordinator or
            user['username'] == transport_request.requested_by):
            can_manage = True
    
    return render_template(
        'transport/view.html',
        transport_request=transport_request,
        equipment=equipment,
        can_manage=can_manage,
        statuses=vars(TransportStatus)
    )

@bp.route('/add_comment/<string:request_id>', methods=['POST'])
def add_comment(request_id):
    """Add a comment to a transport request"""
    # Get transport request
    transport_request = transport_manager.get_transport_request(request_id)
    
    if not transport_request:
        flash('Transport request not found', 'error')
        return redirect(url_for('transport.index'))
    
    # Get comment data
    comment = request.form.get('comment', '')
    
    if not comment:
        flash('Comment cannot be empty', 'error')
        return redirect(url_for('transport.view', request_id=request_id))
    
    # Determine user
    user_name = 'Anonymous'
    if 'user' in session:
        user_name = session['user']['name']
    
    # Add the comment
    transport_manager.add_comment(request_id, comment, user_name)
    
    flash('Comment added successfully', 'success')
    return redirect(url_for('transport.view', request_id=request_id))

@bp.route('/update_status/<string:request_id>', methods=['POST'])
@physicist_required
def update_status(request_id):
    """Update the status of a transport request"""
    # Get transport request
    transport_request = transport_manager.get_transport_request(request_id)
    
    if not transport_request:
        flash('Transport request not found', 'error')
        return redirect(url_for('transport.index'))
    
    # Get form data
    new_status = request.form.get('status', '')
    
    if not new_status or new_status not in vars(TransportStatus).values():
        flash('Invalid status', 'error')
        return redirect(url_for('transport.view', request_id=request_id))
    
    # Update status
    transport_manager.update_transport_request(
        request_id,
        status=new_status,
        transport_coordinator=session['user']['username'] if new_status == TransportStatus.APPROVED else transport_request.transport_coordinator
    )
    
    # Add a comment about the status change
    status_comment = f"Status changed to: {new_status}"
    transport_manager.add_comment(
        request_id, 
        status_comment, 
        session['user']['name']
    )
    
    flash('Transport request updated successfully', 'success')
    return redirect(url_for('transport.view', request_id=request_id))

@bp.route('/equipment/<string:equipment_id>')
def equipment_requests(equipment_id):
    """View transport requests for a specific piece of equipment"""
    # Get equipment details
    equipment = equipment_manager.get_equipment_by_id(equipment_id)
    
    if not equipment:
        flash('Equipment not found', 'error')
        return redirect(url_for('dashboard.index'))
    
    # Get requests for this equipment
    requests = transport_manager.get_requests_by_equipment(equipment_id)
    
    return render_template(
        'transport/equipment_requests.html',
        equipment=equipment,
        requests=requests
    )

@bp.route('/completed')
@login_required
def completed():
    """View completed transport requests"""
    # Get completed transport requests
    completed_requests = transport_manager.get_requests_by_status(TransportStatus.COMPLETED)
    
    return render_template(
        'transport/completed.html',
        completed_requests=completed_requests
    )

@bp.route('/equipment/<string:equipment_id>/schedule_transport', methods=['GET', 'POST'])
@physicist_required  
def schedule_transport(equipment_id):
    """Schedule transport for a piece of equipment (for physicists/admins)"""
    # Get equipment details
    equipment = equipment_manager.get_equipment_by_id(equipment_id)
    
    if not equipment:
        flash('Equipment not found', 'error')
        return redirect(url_for('dashboard.index'))
    
    # Get equipment status
    status = checkout_manager.get_equipment_status(equipment_id)
    
    if request.method == 'POST':
        # Get form data
        origin = request.form.get('origin', status.get('location', 'Unknown'))
        destination = request.form.get('destination', '')
        scheduled_date_str = request.form.get('scheduled_date', '')
        transport_type = request.form.get('transport_type', TransportType.RELOCATION)
        priority = request.form.get('priority', TransportPriority.MEDIUM)
        special_instructions = request.form.get('special_instructions', '')
        
        # Validate required fields
        if not destination:
            flash('Destination is required', 'error')
            return redirect(url_for('transport.schedule_transport', equipment_id=equipment_id))
        
        # Parse scheduled date if provided
        scheduled_date = None
        if scheduled_date_str:
            try:
                # Format expected: YYYY-MM-DD
                scheduled_date = datetime.strptime(scheduled_date_str, '%Y-%m-%d')
                # Set time to 10 AM
                scheduled_date = scheduled_date.replace(hour=10, minute=0, second=0)
            except ValueError:
                flash('Invalid date format. Please use YYYY-MM-DD', 'error')
                return redirect(url_for('transport.schedule_transport', equipment_id=equipment_id))
        
        # Create the transport request - already approved and scheduled
        transport_request = transport_manager.create_transport_request(
            equipment_id=equipment_id,
            origin=origin,
            destination=destination,
            requested_by=session['user']['username'],
            requested_date=scheduled_date,
            special_instructions=special_instructions,
            transport_type=transport_type,
            priority=priority
        )
        
        # Update to scheduled status
        transport_manager.update_transport_request(
            transport_request.id,
            status=TransportStatus.SCHEDULED,
            transport_coordinator=session['user']['username'],
            scheduled_date=scheduled_date
        )
        
        flash('Transport scheduled successfully', 'success')
        return redirect(url_for('transport.view', request_id=transport_request.id))
    
    # GET request - render the form
    # For select dropdowns, get standard values
    locations = equipment_manager.get_unique_locations()
    
    return render_template(
        'transport/schedule.html',
        equipment=equipment,
        status=status,
        locations=locations,
        transport_types=vars(TransportType),
        transport_priorities=vars(TransportPriority),
        min_date=datetime.now().strftime('%Y-%m-%d'),
        default_date=(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    )
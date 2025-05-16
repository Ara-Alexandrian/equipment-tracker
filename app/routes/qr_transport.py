"""
QR code accessible transport request routes - no login required
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import equipment_manager, checkout_manager
from app.models.transport_request import (
    TransportManager, TransportStatus, TransportPriority, 
    TransportType, TransportRequest
)
from datetime import datetime, timedelta
import uuid

# Create a blueprint for QR code transport access
bp = Blueprint('qr_transport', __name__, url_prefix='/qr/transport')

# Initialize transport manager
transport_manager = TransportManager()

@bp.route('/equipment/<string:equipment_id>')
def request_transport(equipment_id):
    """Create transport request via QR code without login"""
    # Get equipment details
    equipment = equipment_manager.get_equipment_by_id(equipment_id)
    
    if not equipment:
        flash('Equipment not found', 'error')
        return redirect(url_for('equipment.landing_page'))
    
    # Get current status
    status = checkout_manager.get_equipment_status(equipment_id)
    
    # Get locations for dropdown
    locations = equipment_manager.get_unique_locations()
    
    # For mobile QR scanning, we keep the form simple
    return render_template(
        'transport/qr_request.html',
        equipment=equipment,
        status=status,
        locations=locations,
        transport_types=vars(TransportType),
        transport_priorities=vars(TransportPriority),
        min_date=datetime.now().strftime('%Y-%m-%d'),
        default_date=(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    )

@bp.route('/submit/<string:equipment_id>', methods=['POST'])
def submit_request(equipment_id):
    """Submit a transport request via QR code"""
    # Get equipment details
    equipment = equipment_manager.get_equipment_by_id(equipment_id)
    
    if not equipment:
        flash('Equipment not found', 'error')
        return redirect(url_for('equipment.landing_page'))
    
    # Get equipment status
    status = checkout_manager.get_equipment_status(equipment_id)
    
    # Get form data
    origin = request.form.get('origin', status.get('location', 'Unknown'))
    destination = request.form.get('destination', '')
    requested_date_str = request.form.get('requested_date', '')
    transport_type = request.form.get('transport_type', TransportType.RELOCATION)
    priority = request.form.get('priority', TransportPriority.MEDIUM)
    special_instructions = request.form.get('special_instructions', '')
    requester_name = request.form.get('requester_name', 'Anonymous User')
    requester_contact = request.form.get('requester_contact', '')
    
    # Validate required fields
    if not destination:
        flash('Destination is required', 'error')
        return redirect(url_for('qr_transport.request_transport', equipment_id=equipment_id))
    
    if not requester_name:
        flash('Your name is required', 'error')
        return redirect(url_for('qr_transport.request_transport', equipment_id=equipment_id))
    
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
            return redirect(url_for('qr_transport.request_transport', equipment_id=equipment_id))
    
    # Add contact info to special instructions
    if requester_contact:
        contact_info = f"Contact info: {requester_contact}\n\n"
        special_instructions = contact_info + special_instructions
    
    # Create the transport request
    transport_request = transport_manager.create_transport_request(
        equipment_id=equipment_id,
        origin=origin,
        destination=destination,
        requested_by=requester_name,  # Use provided name since user might not be logged in
        requested_date=requested_date,
        special_instructions=special_instructions,
        transport_type=transport_type,
        priority=priority
    )
    
    flash('Transport request created successfully! Your request will be reviewed by the physics team.', 'success')
    
    # Return confirmation page
    return render_template(
        'transport/request_confirmation.html',
        transport_request=transport_request,
        equipment=equipment
    )

@bp.route('/view/<string:request_id>')
def view_request(request_id):
    """View transport request details via QR code"""
    # Get transport request
    transport_request = transport_manager.get_transport_request(request_id)
    
    if not transport_request:
        flash('Transport request not found', 'error')
        return redirect(url_for('equipment.landing_page'))
    
    # Get equipment details
    equipment = equipment_manager.get_equipment_by_id(transport_request.equipment_id)
    
    return render_template(
        'transport/qr_view.html',
        transport_request=transport_request,
        equipment=equipment,
        statuses=vars(TransportStatus)
    )

@bp.route('/add_comment/<string:request_id>', methods=['POST'])
def add_comment(request_id):
    """Add a comment to a transport request via QR code"""
    # Get transport request
    transport_request = transport_manager.get_transport_request(request_id)
    
    if not transport_request:
        flash('Transport request not found', 'error')
        return redirect(url_for('equipment.landing_page'))
    
    # Get comment data
    comment = request.form.get('comment', '')
    commenter_name = request.form.get('commenter_name', 'Anonymous')
    
    if not comment:
        flash('Comment cannot be empty', 'error')
        return redirect(url_for('qr_transport.view_request', request_id=request_id))
    
    # Add the comment
    transport_manager.add_comment(request_id, comment, commenter_name)
    
    flash('Comment added successfully', 'success')
    return redirect(url_for('qr_transport.view_request', request_id=request_id))

@bp.route('/equipment/<string:equipment_id>/history')
def equipment_history(equipment_id):
    """View transport history for equipment via QR code"""
    # Get equipment details
    equipment = equipment_manager.get_equipment_by_id(equipment_id)
    
    if not equipment:
        flash('Equipment not found', 'error')
        return redirect(url_for('equipment.landing_page'))
    
    # Get all transport requests for this equipment
    requests = transport_manager.get_requests_by_equipment(equipment_id)
    
    return render_template(
        'transport/qr_history.html',
        equipment=equipment,
        requests=requests
    )
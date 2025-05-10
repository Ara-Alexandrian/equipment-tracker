"""
QR code direct access routes - no login required
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import equipment_manager, checkout_manager, csrf
from app.models.ticket import TicketManager, TicketStatus, TicketPriority, TicketType, EquipmentCondition
from datetime import datetime, timedelta
import uuid

# Create a completely separate blueprint for QR code access
bp = Blueprint('qr', __name__, url_prefix='/qr')

# Initialize ticket manager
ticket_manager = TicketManager()

@bp.route('/checkout/<string:equipment_id>', methods=['GET', 'POST'])
@csrf.exempt
def quick_checkout(equipment_id):
    """Quick checkout without requiring login"""
    # Get equipment details
    equipment = equipment_manager.get_equipment_by_id(equipment_id)
    
    if not equipment:
        flash('Equipment not found', 'error')
        return redirect(url_for('equipment.landing_page', equipment_id=equipment_id))
    
    # Get status
    status = checkout_manager.get_equipment_status(equipment_id)
    
    # If equipment is already checked out, redirect to landing page
    if status and status.get('status') == "Checked Out":
        flash('This equipment is already checked out', 'warning')
        return redirect(url_for('equipment.landing_page', equipment_id=equipment_id))
    
    # Handle form submission
    if request.method == 'POST':
        location = request.form.get('location')
        expected_return_days = int(request.form.get('expected_return_days', 1))
        notes = request.form.get('notes', '')
        
        # Get the user identification
        user_name = request.form.get('user_name', '').strip()
        user_initials = request.form.get('user_initials', '').strip().upper()
        selected_user = request.form.get('selected_user', '').strip()
        
        # Determine username
        if selected_user and selected_user != "other":
            username = selected_user
        elif user_initials:
            username = user_initials
        elif user_name:
            username = user_name
        else:
            flash('Please provide your name or initials', 'danger')
            locations = equipment_manager.get_unique_locations()

            # Get all users for dropdown - make a clean copy without passwords
            users = {}
            for username, info in checkout_manager.users.items():
                user_info = info.copy()
                if 'password' in user_info:
                    user_info.pop('password')
                users[username] = user_info

            return render_template(
                'checkout/quick_check_out.html',
                equipment=equipment,
                status=status,
                locations=locations,
                users=users,
                checkout_manager=checkout_manager
            )
        
        if checkout_manager.checkout_equipment(
            equipment_id, 
            username,
            location,
            expected_return_days,
            notes
        ):
            flash('Equipment checked out successfully', 'success')
            return redirect(url_for('equipment.landing_page', equipment_id=equipment_id))
        else:
            flash('Failed to check out equipment', 'danger')
    
    # Get all locations for dropdown
    locations = equipment_manager.get_unique_locations()
    
    # Get all users for dropdown - make a clean copy without passwords
    users = {}
    for username, info in checkout_manager.users.items():
        user_info = info.copy()
        if 'password' in user_info:
            user_info.pop('password')
        users[username] = user_info

    return render_template(
        'checkout/quick_check_out.html',
        equipment=equipment,
        status=status,
        locations=locations,
        users=users,
        checkout_manager=checkout_manager
    )

@bp.route('/checkin/<string:equipment_id>', methods=['GET', 'POST'])
@csrf.exempt
def quick_checkin(equipment_id):
    """Quick check-in without requiring login"""
    # Get equipment details
    equipment = equipment_manager.get_equipment_by_id(equipment_id)
    
    if not equipment:
        flash('Equipment not found', 'error')
        return redirect(url_for('equipment.landing_page', equipment_id=equipment_id))
    
    # Get status
    status = checkout_manager.get_equipment_status(equipment_id)
    
    # If equipment is not checked out, redirect to landing page
    if not status or not status.get('status') == "Checked Out":
        flash('This equipment is not checked out', 'warning')
        return redirect(url_for('equipment.landing_page', equipment_id=equipment_id))
    
    # Handle form submission
    if request.method == 'POST':
        return_location = request.form.get('return_location')
        notes = request.form.get('notes', '')
        
        # Get the user identification
        user_name = request.form.get('user_name', '').strip()
        user_initials = request.form.get('user_initials', '').strip().upper()
        selected_user = request.form.get('selected_user', '').strip()
        
        # Determine username
        if selected_user and selected_user != "other":
            username = selected_user
        elif user_initials:
            username = user_initials
        elif user_name:
            username = user_name
        else:
            flash('Please provide your name or initials', 'danger')
            locations = equipment_manager.get_unique_locations()

            # Get all users for dropdown - make a clean copy without passwords
            users = {}
            for username, info in checkout_manager.users.items():
                user_info = info.copy()
                if 'password' in user_info:
                    user_info.pop('password')
                users[username] = user_info

            return render_template(
                'checkout/quick_check_in.html',
                equipment=equipment,
                status=status,
                locations=locations,
                users=users,
                checkout_manager=checkout_manager
            )
        
        if checkout_manager.return_equipment(
            equipment_id,
            username,
            return_location,
            notes
        ):
            flash('Equipment checked in successfully', 'success')
            return redirect(url_for('equipment.landing_page', equipment_id=equipment_id))
        else:
            flash('Failed to check in equipment', 'danger')
    
    # Get all locations for dropdown
    locations = equipment_manager.get_unique_locations()
    
    # Get all users for dropdown - make a clean copy without passwords
    users = {}
    for username, info in checkout_manager.users.items():
        user_info = info.copy()
        if 'password' in user_info:
            user_info.pop('password')
        users[username] = user_info

    return render_template(
        'checkout/quick_check_in.html',
        equipment=equipment,
        status=status,
        locations=locations,
        users=users,
        checkout_manager=checkout_manager
    )

@bp.route('/ticket/<string:equipment_id>', methods=['GET', 'POST'])
@csrf.exempt
def quick_ticket(equipment_id):
    """Create a new ticket without requiring login"""
    # Get equipment details
    equipment = equipment_manager.get_equipment_by_id(equipment_id)
    
    if not equipment:
        flash('Equipment not found', 'danger')
        return redirect(url_for('equipment.landing_page', equipment_id=equipment_id))
    
    # Get equipment status
    status = checkout_manager.get_equipment_status(equipment_id)
    
    # Get current condition
    condition = ticket_manager.get_equipment_condition(equipment_id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        ticket_type = request.form.get('ticket_type', TicketType.ISSUE)
        priority = request.form.get('priority', TicketPriority.MEDIUM)
        
        # Get the creator information
        creator_name = request.form.get('creator_name', '').strip()
        creator_initials = request.form.get('creator_initials', '').strip().upper()
        selected_user = request.form.get('selected_user', '').strip()
        
        # Use the provided creator info
        if selected_user and selected_user != "other":
            created_by = selected_user
        elif creator_initials:
            created_by = creator_initials
        elif creator_name:
            created_by = creator_name
        else:
            flash('Please provide your name or initials', 'danger')
            # Get all users for dropdown - make a clean copy without passwords
            users = {}
            for username, info in checkout_manager.users.items():
                user_info = info.copy()
                if 'password' in user_info:
                    user_info.pop('password')
                users[username] = user_info

            return render_template(
                'ticket/quick_create.html',
                equipment=equipment,
                status=status,
                condition=condition,
                ticket_types=[(TicketType.ISSUE, 'Issue/Problem'),
                            (TicketType.REQUEST, 'Request'),
                            (TicketType.MAINTENANCE, 'Maintenance'),
                            (TicketType.CALIBRATION, 'Calibration')],
                priorities=[(TicketPriority.LOW, 'Low'),
                           (TicketPriority.MEDIUM, 'Medium'),
                           (TicketPriority.HIGH, 'High'),
                           (TicketPriority.CRITICAL, 'Critical')],
                users=users,
                checkout_manager=checkout_manager
            )
        
        # Equipment condition stays the same for quick tickets
        equipment_condition = condition
        
        if not title or not description:
            flash('Title and description are required', 'danger')
        else:
            # Create the ticket
            ticket = ticket_manager.create_ticket(
                equipment_id=equipment_id,
                title=title,
                description=description,
                created_by=created_by,
                ticket_type=ticket_type,
                priority=priority,
                equipment_condition=equipment_condition
            )
            
            flash('Ticket created successfully', 'success')
            return redirect(url_for('equipment.landing_page', equipment_id=equipment_id))
    
    # Get all users for dropdown - make a clean copy without passwords
    users = {}
    for username, info in checkout_manager.users.items():
        user_info = info.copy()
        if 'password' in user_info:
            user_info.pop('password')
        users[username] = user_info

    return render_template(
        'ticket/quick_create.html',
        equipment=equipment,
        status=status,
        condition=condition,
        ticket_types=[(TicketType.ISSUE, 'Issue/Problem'), 
                    (TicketType.REQUEST, 'Request'),
                    (TicketType.MAINTENANCE, 'Maintenance'),
                    (TicketType.CALIBRATION, 'Calibration')],
        priorities=[(TicketPriority.LOW, 'Low'), 
                   (TicketPriority.MEDIUM, 'Medium'),
                   (TicketPriority.HIGH, 'High'),
                   (TicketPriority.CRITICAL, 'Critical')],
        users=users,
        checkout_manager=checkout_manager
    )
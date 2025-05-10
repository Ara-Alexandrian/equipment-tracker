"""
Ticket and QR code landing page routes
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app import equipment_manager, checkout_manager, csrf
from app.models.ticket import TicketManager, TicketStatus, TicketPriority, TicketType, EquipmentCondition
import functools
import qrcode
import io
import base64
from datetime import datetime

bp = Blueprint('ticket', __name__, url_prefix='/ticket')

# Initialize ticket manager
ticket_manager = TicketManager()

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
        
        if session['user'].get('role') not in ['admin', 'physicist']:
            flash('Clinical physicist privileges required.', 'danger')
            return redirect(url_for('dashboard.index'))
        
        return view(**kwargs)
    return wrapped_view

@bp.route('/')
@login_required
def index():
    """Ticket system dashboard"""
    # Get recent tickets
    recent_tickets = ticket_manager.get_all_tickets(limit=10)
    
    # Count tickets by status
    open_count = len(ticket_manager.get_tickets_by_status(TicketStatus.OPEN))
    in_progress_count = len(ticket_manager.get_tickets_by_status(TicketStatus.IN_PROGRESS))
    resolved_count = len(ticket_manager.get_tickets_by_status(TicketStatus.RESOLVED))
    closed_count = len(ticket_manager.get_tickets_by_status(TicketStatus.CLOSED))
    
    # Count equipment by condition
    normal_count = len(ticket_manager.get_equipment_with_condition(EquipmentCondition.NORMAL))
    warning_count = len(ticket_manager.get_equipment_with_condition(EquipmentCondition.WARNING))
    critical_count = len(ticket_manager.get_equipment_with_condition(EquipmentCondition.CRITICAL))
    
    # Get tickets assigned to current user (for physicists and admins)
    assigned_tickets = []
    if session['user'].get('role') in ['admin', 'physicist']:
        assigned_tickets = ticket_manager.get_tickets_by_user(session['user']['username'], role="assigned_to")
    
    # Get tickets created by current user
    created_tickets = ticket_manager.get_tickets_by_user(session['user']['username'], role="created_by")
    
    return render_template(
        'ticket/index.html',
        recent_tickets=recent_tickets,
        open_count=open_count,
        in_progress_count=in_progress_count,
        resolved_count=resolved_count,
        closed_count=closed_count,
        normal_count=normal_count,
        warning_count=warning_count,
        critical_count=critical_count,
        assigned_tickets=assigned_tickets,
        created_tickets=created_tickets,
        ticket_status=TicketStatus,
        ticket_priority=TicketPriority,
        ticket_type=TicketType,
        equipment_condition=EquipmentCondition,
        checkout_manager=checkout_manager,
        equipment_manager=equipment_manager
    )

@bp.route('/quick-create/<string:equipment_id>', methods=['GET', 'POST'])
@csrf.exempt
def quick_create_ticket(equipment_id):
    """Create a new ticket for a piece of equipment without requiring login"""
    # Get equipment details
    equipment = equipment_manager.get_equipment_by_id(equipment_id)
    
    if not equipment:
        flash('Equipment not found', 'danger')
        return redirect(url_for('dashboard.equipment_list'))
    
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
                users=checkout_manager.users,
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
    
    # Get all users for dropdown
    users = {username: info for username, info in checkout_manager.users.items() 
            if 'password' not in info}
    
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

@bp.route('/create/<string:equipment_id>', methods=['GET', 'POST'])
@login_required
def create_ticket(equipment_id):
    """Create a new ticket for a piece of equipment"""
    # Get equipment details
    equipment = equipment_manager.get_equipment_by_id(equipment_id)
    
    if not equipment:
        flash('Equipment not found', 'danger')
        return redirect(url_for('dashboard.equipment_list'))
    
    # Get equipment status
    status = checkout_manager.get_equipment_status(equipment_id)
    
    # Get current condition
    condition = ticket_manager.get_equipment_condition(equipment_id)
    
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        ticket_type = request.form.get('ticket_type', TicketType.ISSUE)
        priority = request.form.get('priority', TicketPriority.MEDIUM)
        
        # Get the requested equipment condition
        equipment_condition = condition  # Default to current condition
        
        # Only allow equipment condition changes for admins and physicists
        if session['user'].get('role') in ['admin', 'physicist']:
            equipment_condition = request.form.get('equipment_condition', condition)
        
        if not title or not description:
            flash('Title and description are required', 'danger')
        else:
            # Create the ticket
            ticket = ticket_manager.create_ticket(
                equipment_id=equipment_id,
                title=title,
                description=description,
                created_by=session['user']['username'],
                ticket_type=ticket_type,
                priority=priority,
                equipment_condition=equipment_condition
            )
            
            flash('Ticket created successfully', 'success')
            return redirect(url_for('ticket.view_ticket', ticket_id=ticket.id))
    
    return render_template(
        'ticket/create.html',
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
        conditions=[(EquipmentCondition.NORMAL, 'Normal - Fully Operational'),
                   (EquipmentCondition.WARNING, 'Warning - Needs Attention'),
                   (EquipmentCondition.CRITICAL, 'Critical - Out of Service')]
    )

@bp.route('/view/<string:ticket_id>', methods=['GET', 'POST'])
@login_required
def view_ticket(ticket_id):
    """View a specific ticket"""
    ticket = ticket_manager.get_ticket(ticket_id)
    
    if not ticket:
        flash('Ticket not found', 'danger')
        return redirect(url_for('ticket.index'))
    
    # Get equipment details
    equipment = equipment_manager.get_equipment_by_id(ticket.equipment_id)
    
    # Process comment form
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add_comment':
            comment = request.form.get('comment')
            
            if comment:
                ticket_manager.add_comment(
                    ticket_id=ticket_id,
                    comment=comment,
                    user=session['user']['username']
                )
                flash('Comment added successfully', 'success')
                return redirect(url_for('ticket.view_ticket', ticket_id=ticket_id))
            else:
                flash('Comment cannot be empty', 'danger')
        
        elif action == 'update_status' and session['user'].get('role') in ['admin', 'physicist']:
            new_status = request.form.get('status')
            
            if new_status in [TicketStatus.OPEN, TicketStatus.IN_PROGRESS, TicketStatus.RESOLVED, TicketStatus.CLOSED]:
                ticket_manager.update_ticket(
                    ticket_id=ticket_id,
                    status=new_status
                )
                flash('Ticket status updated successfully', 'success')
                return redirect(url_for('ticket.view_ticket', ticket_id=ticket_id))
            else:
                flash('Invalid status', 'danger')
        
        elif action == 'assign' and session['user'].get('role') in ['admin', 'physicist']:
            assigned_to = request.form.get('assigned_to')
            
            ticket_manager.update_ticket(
                ticket_id=ticket_id,
                assigned_to=assigned_to
            )
            flash('Ticket assigned successfully', 'success')
            return redirect(url_for('ticket.view_ticket', ticket_id=ticket_id))
        
        elif action == 'update_condition' and session['user'].get('role') in ['admin', 'physicist']:
            equipment_condition = request.form.get('equipment_condition')
            
            if equipment_condition in [EquipmentCondition.NORMAL, EquipmentCondition.WARNING, EquipmentCondition.CRITICAL]:
                ticket_manager.update_ticket(
                    ticket_id=ticket_id,
                    equipment_condition=equipment_condition
                )
                flash('Equipment condition updated successfully', 'success')
                return redirect(url_for('ticket.view_ticket', ticket_id=ticket_id))
            else:
                flash('Invalid equipment condition', 'danger')
    
    # Get users for assignment (physicists and admins)
    users = {}
    for username, info in checkout_manager.users.items():
        if info.get('role') in ['admin', 'physicist']:
            if 'password' in info:
                info_copy = info.copy()
                info_copy.pop('password')
                users[username] = info_copy
            else:
                users[username] = info
    
    return render_template(
        'ticket/view.html',
        ticket=ticket,
        equipment=equipment,
        users=users,
        checkout_manager=checkout_manager,
        ticket_status=TicketStatus,
        ticket_priority=TicketPriority,
        ticket_type=TicketType,
        equipment_condition=EquipmentCondition,
        statuses=[(TicketStatus.OPEN, 'Open'), 
                 (TicketStatus.IN_PROGRESS, 'In Progress'),
                 (TicketStatus.RESOLVED, 'Resolved'),
                 (TicketStatus.CLOSED, 'Closed')],
        conditions=[(EquipmentCondition.NORMAL, 'Normal - Fully Operational'),
                   (EquipmentCondition.WARNING, 'Warning - Needs Attention'),
                   (EquipmentCondition.CRITICAL, 'Critical - Out of Service')]
    )

@bp.route('/list')
@login_required
def list_tickets():
    """List all tickets"""
    # Filter parameters
    status = request.args.get('status')
    priority = request.args.get('priority')
    ticket_type = request.args.get('type')
    equipment_id = request.args.get('equipment_id')
    assigned_to = request.args.get('assigned_to')
    created_by = request.args.get('created_by')
    
    # Get all tickets
    all_tickets = ticket_manager.get_all_tickets()
    
    # Apply filters
    filtered_tickets = all_tickets
    
    if status:
        filtered_tickets = [t for t in filtered_tickets if t.status == status]
    
    if priority:
        filtered_tickets = [t for t in filtered_tickets if t.priority == priority]
    
    if ticket_type:
        filtered_tickets = [t for t in filtered_tickets if t.ticket_type == ticket_type]
    
    if equipment_id:
        filtered_tickets = [t for t in filtered_tickets if t.equipment_id == equipment_id]
    
    if assigned_to:
        filtered_tickets = [t for t in filtered_tickets if t.assigned_to == assigned_to]
    
    if created_by:
        filtered_tickets = [t for t in filtered_tickets if t.created_by == created_by]
    
    return render_template(
        'ticket/list.html',
        tickets=filtered_tickets,
        filter_status=status,
        filter_priority=priority,
        filter_type=ticket_type,
        filter_equipment_id=equipment_id,
        filter_assigned_to=assigned_to,
        filter_created_by=created_by,
        checkout_manager=checkout_manager,
        equipment_manager=equipment_manager,
        ticket_status=TicketStatus,
        ticket_priority=TicketPriority,
        ticket_type=TicketType,
        equipment_condition=EquipmentCondition,
        statuses=[(TicketStatus.OPEN, 'Open'), 
                 (TicketStatus.IN_PROGRESS, 'In Progress'),
                 (TicketStatus.RESOLVED, 'Resolved'),
                 (TicketStatus.CLOSED, 'Closed')],
        priorities=[(TicketPriority.LOW, 'Low'), 
                   (TicketPriority.MEDIUM, 'Medium'),
                   (TicketPriority.HIGH, 'High'),
                   (TicketPriority.CRITICAL, 'Critical')],
        types=[(TicketType.ISSUE, 'Issue/Problem'), 
              (TicketType.REQUEST, 'Request'),
              (TicketType.MAINTENANCE, 'Maintenance'),
              (TicketType.CALIBRATION, 'Calibration')]
    )

@bp.route('/equipment/<string:equipment_id>')
@login_required
def equipment_tickets(equipment_id):
    """List all tickets for a specific piece of equipment"""
    # Get equipment details
    equipment = equipment_manager.get_equipment_by_id(equipment_id)
    
    if not equipment:
        flash('Equipment not found', 'danger')
        return redirect(url_for('dashboard.equipment_list'))
    
    # Get equipment status
    status = checkout_manager.get_equipment_status(equipment_id)
    
    # Get equipment condition
    condition = ticket_manager.get_equipment_condition(equipment_id)
    
    # Get tickets for this equipment
    tickets = ticket_manager.get_tickets_by_equipment(equipment_id)
    
    return render_template(
        'ticket/equipment_tickets.html',
        equipment=equipment,
        status=status,
        condition=condition,
        tickets=tickets,
        checkout_manager=checkout_manager,
        ticket_status=TicketStatus,
        ticket_priority=TicketPriority,
        ticket_type=TicketType,
        equipment_condition=EquipmentCondition
    )

@bp.route('/qr/<string:equipment_id>')
@physicist_required
def generate_qr(equipment_id):
    """Generate QR code for a piece of equipment"""
    # Get equipment details
    equipment = equipment_manager.get_equipment_by_id(equipment_id)
    
    if not equipment:
        flash('Equipment not found', 'danger')
        return redirect(url_for('dashboard.equipment_list'))
    
    # Generate QR code URL
    qr_url = request.host_url + 'equipment/' + equipment_id
    
    # Generate QR code
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(qr_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save to in-memory file
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    img_data = img_io.getvalue()
    
    # Convert to base64 for embedding in HTML
    img_base64 = base64.b64encode(img_data).decode('utf-8')
    
    return render_template(
        'ticket/qr_code.html',
        equipment=equipment,
        qr_url=qr_url,
        qr_image=img_base64
    )

@bp.route('/api/condition/<string:equipment_id>', methods=['GET'])
def api_equipment_condition(equipment_id):
    """API endpoint to get equipment condition"""
    condition = ticket_manager.get_equipment_condition(equipment_id)
    
    return jsonify({
        'status': 'success',
        'equipment_id': equipment_id,
        'condition': condition
    })
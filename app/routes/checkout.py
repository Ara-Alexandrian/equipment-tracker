"""
Checkout routes for equipment checkout system
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app import checkout_manager, equipment_manager
import functools

bp = Blueprint('checkout', __name__, url_prefix='/checkout')

def login_required(view):
    """View decorator that redirects anonymous users to the login page."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('checkout.login', next=request.url))
        return view(**kwargs)
    return wrapped_view

def admin_required(view):
    """View decorator that requires the user to be an administrator."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user' not in session:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('checkout.login', next=request.url))
        
        if session['user'].get('role') != 'admin':
            flash('Administrator privileges required.', 'danger')
            return redirect(url_for('dashboard.index'))
        
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

@bp.route('/login', methods=('GET', 'POST'))
def login():
    """User login page."""
    next_url = request.args.get('next', url_for('dashboard.index'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = checkout_manager.authenticate_user(username, password)
        
        if user:
            session.clear()
            session['user'] = user
            flash(f'Welcome, {user["name"]}!', 'success')
            return redirect(next_url)
        
        flash('Invalid username or password', 'danger')
    
    return render_template('checkout/login.html', next_url=next_url)

@bp.route('/logout')
def logout():
    """Log out the current user."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('dashboard.index'))

@bp.route('/')
@login_required
def index():
    """Checkout dashboard."""
    # Get recent checkout history
    history = checkout_manager.get_checkout_history(limit=10)
    
    # Get currently checked out equipment
    checked_out = checkout_manager.get_checked_out_equipment()
    
    # Get overdue equipment
    overdue = checkout_manager.get_overdue_equipment()
    
    return render_template(
        'checkout/index.html',
        history=history,
        checked_out=checked_out,
        overdue=overdue
    )

@bp.route('/equipment/<string:equipment_id>', methods=('GET', 'POST'))
@login_required
def equipment_detail(equipment_id):
    """Equipment checkout status and history."""
    # Get equipment details
    equipment = equipment_manager.get_equipment_by_id(equipment_id)
    
    if not equipment:
        flash('Equipment not found', 'error')
        return redirect(url_for('dashboard.equipment_list'))
    
    # Get status
    status = checkout_manager.get_equipment_status(equipment_id)
    
    # Get checkout history
    history = checkout_manager.get_checkout_history(equipment_id=equipment_id)
    
    # Handle checkout/return actions
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'checkout':
            location = request.form.get('location')
            expected_return_days = int(request.form.get('expected_return_days', 1))
            notes = request.form.get('notes', '')
            
            if checkout_manager.checkout_equipment(
                equipment_id, 
                session['user']['username'],
                location,
                expected_return_days,
                notes
            ):
                flash('Equipment checked out successfully', 'success')
            else:
                flash('Failed to check out equipment', 'danger')
                
        elif action == 'return':
            return_location = request.form.get('return_location')
            notes = request.form.get('notes', '')
            
            if checkout_manager.return_equipment(
                equipment_id,
                session['user']['username'],
                return_location,
                notes
            ):
                flash('Equipment returned successfully', 'success')
            else:
                flash('Failed to return equipment', 'danger')
                
        elif action == 'update_status' and session['user']['role'] in ['admin', 'physicist']:
            new_status = request.form.get('status')
            location = request.form.get('location')
            notes = request.form.get('notes', '')
            
            if checkout_manager.update_equipment_status(
                equipment_id,
                new_status,
                location=location,
                notes=notes,
                user=session['user']['username']
            ):
                flash('Equipment status updated successfully', 'success')
            else:
                flash('Failed to update equipment status', 'danger')
        
        # Refresh status and history
        status = checkout_manager.get_equipment_status(equipment_id)
        history = checkout_manager.get_checkout_history(equipment_id=equipment_id)
    
    return render_template(
        'checkout/equipment_detail.html',
        equipment=equipment,
        status=status,
        history=history,
        status_options=checkout_manager.STATUS_OPTIONS
    )

@bp.route('/history')
@login_required
def history():
    """View full checkout history."""
    # Get filter parameters
    equipment_id = request.args.get('equipment_id')
    user = request.args.get('user')
    
    # Get history
    history = checkout_manager.get_checkout_history(equipment_id=equipment_id, user=user)
    
    return render_template(
        'checkout/history.html',
        history=history,
        equipment_id=equipment_id,
        user=user
    )

@bp.route('/admin')
@admin_required
def admin():
    """Administrator dashboard."""
    # Get all users
    users = {username: info for username, info in checkout_manager.users.items() 
             if 'password' not in info}
    
    # Get equipment counts by status
    status_counts = {}
    for status in checkout_manager.STATUS_OPTIONS:
        status_counts[status] = len(checkout_manager.get_equipment_by_status(status))
    
    return render_template(
        'checkout/admin.html',
        users=users,
        status_counts=status_counts
    )

@bp.route('/admin/users', methods=('GET', 'POST'))
@admin_required
def manage_users():
    """Manage users."""
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'add':
            username = request.form.get('username')
            name = request.form.get('name')
            email = request.form.get('email')
            role = request.form.get('role')
            password = request.form.get('password')
            
            if checkout_manager.add_user(
                username, 
                name, 
                email, 
                role, 
                password,
                session['user']['username']
            ):
                flash(f'User {username} added successfully', 'success')
            else:
                flash('Failed to add user', 'danger')
                
        elif action == 'update':
            username = request.form.get('username')
            name = request.form.get('name')
            email = request.form.get('email')
            role = request.form.get('role')
            password = request.form.get('password')
            
            update_args = {
                'username': username,
                'name': name,
                'email': email,
                'role': role,
                'admin_user': session['user']['username']
            }
            
            # Only include password if it was provided
            if password:
                update_args['password'] = password
            
            if checkout_manager.update_user(**update_args):
                flash(f'User {username} updated successfully', 'success')
            else:
                flash('Failed to update user', 'danger')
                
        elif action == 'delete':
            username = request.form.get('username')
            
            if checkout_manager.delete_user(username, session['user']['username']):
                flash(f'User {username} deleted successfully', 'success')
            else:
                flash('Failed to delete user - cannot delete last admin', 'danger')
    
    # Get all users
    users = {username: info for username, info in checkout_manager.users.items() 
             if 'password' not in info}
    
    return render_template(
        'checkout/manage_users.html',
        users=users
    )

@bp.route('/api/status/<string:equipment_id>', methods=['GET'])
def api_equipment_status(equipment_id):
    """API endpoint to get equipment status."""
    status = checkout_manager.get_equipment_status(equipment_id)
    
    return jsonify({
        'status': 'success',
        'equipment_id': equipment_id,
        'data': status
    })

@bp.route('/api/checkout/<string:equipment_id>', methods=['POST'])
def api_checkout_equipment(equipment_id):
    """API endpoint to check out equipment."""
    # Require authentication
    if 'user' not in session:
        return jsonify({
            'status': 'error',
            'message': 'Authentication required'
        }), 401
    
    data = request.json
    
    if not data:
        return jsonify({
            'status': 'error',
            'message': 'Missing request data'
        }), 400
    
    location = data.get('location')
    expected_return_days = data.get('expected_return_days', 1)
    notes = data.get('notes', '')
    
    if not location:
        return jsonify({
            'status': 'error',
            'message': 'Location is required'
        }), 400
    
    if checkout_manager.checkout_equipment(
        equipment_id, 
        session['user']['username'],
        location,
        expected_return_days,
        notes
    ):
        return jsonify({
            'status': 'success',
            'message': 'Equipment checked out successfully'
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Failed to check out equipment'
        }), 500

@bp.route('/api/return/<string:equipment_id>', methods=['POST'])
def api_return_equipment(equipment_id):
    """API endpoint to return equipment."""
    # Require authentication
    if 'user' not in session:
        return jsonify({
            'status': 'error',
            'message': 'Authentication required'
        }), 401
    
    data = request.json
    
    if not data:
        return jsonify({
            'status': 'error',
            'message': 'Missing request data'
        }), 400
    
    return_location = data.get('return_location')
    notes = data.get('notes', '')
    
    if checkout_manager.return_equipment(
        equipment_id,
        session['user']['username'],
        return_location,
        notes
    ):
        return jsonify({
            'status': 'success',
            'message': 'Equipment returned successfully'
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'Failed to return equipment'
        }), 500
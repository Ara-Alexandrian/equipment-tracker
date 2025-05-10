"""
Checkout routes for equipment checkout system
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app import checkout_manager, equipment_manager, csrf
from app.models.forms import LoginForm, NotificationPreferencesForm
from app.models.json_utils import DateTimeEncoder
import functools
import json
import os

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
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        user = checkout_manager.authenticate_user(username, password)
        
        if user:
            session.clear()
            session['user'] = user
            session['user']['username'] = username
            flash(f'Welcome, {user["name"]}!', 'success')
            return redirect(next_url)
        
        flash('Invalid username or password', 'danger')
    
    return render_template('checkout/login.html', form=form, next_url=next_url)

@bp.route('/logout')
def logout():
    """Log out the current user."""
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('dashboard.index'))

@bp.route('/profile/notifications', methods=['GET', 'POST'])
@login_required
def notification_preferences():
    """User notification preferences."""
    # Get current user data
    username = session['user']['username']
    users_file_path = os.path.join(checkout_manager.data_dir, 'users.json')
    
    # Load all user data
    try:
        with open(users_file_path, 'r') as f:
            users_data = json.load(f)
    except:
        flash('Could not load user data', 'danger')
        return redirect(url_for('checkout.index'))
    
    if username not in users_data:
        flash('User data not found', 'danger')
        return redirect(url_for('checkout.index'))
    
    # Get user data and initialize form
    user_data = users_data[username]
    form = NotificationPreferencesForm()
    
    # On form submit
    if form.validate_on_submit():
        # Update user preferences
        user_data['notification_preferences'] = {
            'receive_due_soon': form.receive_due_soon.data,
            'receive_overdue': form.receive_overdue.data,
            'days_before_due': form.days_before_due.data,
            'email_format': form.email_format.data
        }
        
        # Save updated user data
        try:
            with open(users_file_path, 'w') as f:
                json.dump(users_data, f, cls=DateTimeEncoder, indent=2)
            
            # Update session data
            session['user'] = user_data
            session['user']['username'] = username
            
            flash('Notification preferences updated successfully', 'success')
        except Exception as e:
            flash(f'Error saving preferences: {str(e)}', 'danger')
    
    # On GET request, populate form with current values
    elif request.method == 'GET':
        # Get current preferences or set defaults
        prefs = user_data.get('notification_preferences', {})
        form.receive_due_soon.data = prefs.get('receive_due_soon', True)
        form.receive_overdue.data = prefs.get('receive_overdue', True)
        form.days_before_due.data = prefs.get('days_before_due', 30)
        form.email_format.data = prefs.get('email_format', 'html')
    
    return render_template(
        'checkout/notification_preferences.html',
        form=form,
        user=user_data
    )

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

@bp.route('/quick-check-out/<string:equipment_id>', methods=('GET', 'POST'))
@csrf.exempt
def quick_check_out(equipment_id):
    """Quick checkout without requiring login."""
    # Get equipment details
    equipment = equipment_manager.get_equipment_by_id(equipment_id)
    
    if not equipment:
        flash('Equipment not found', 'error')
        return redirect(url_for('dashboard.equipment_list'))
    
    # Get status
    status = checkout_manager.get_equipment_status(equipment_id)
    
    # If equipment is already checked out, redirect to landing page
    if status and status.get('checked_out'):
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
            users = {username: info for username, info in checkout_manager.users.items() 
                    if 'password' not in info}
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
    
    # Get all users for dropdown
    users = {username: info for username, info in checkout_manager.users.items() 
            if 'password' not in info}
    
    return render_template(
        'checkout/quick_check_out.html',
        equipment=equipment,
        status=status,
        locations=locations,
        users=users,
        checkout_manager=checkout_manager
    )

@bp.route('/check-out/<string:equipment_id>', methods=('GET', 'POST'))
@login_required
def check_out(equipment_id):
    """Dedicated checkout page with a pre-filled form."""
    # Get equipment details
    equipment = equipment_manager.get_equipment_by_id(equipment_id)
    
    if not equipment:
        flash('Equipment not found', 'error')
        return redirect(url_for('dashboard.equipment_list'))
    
    # Get status
    status = checkout_manager.get_equipment_status(equipment_id)
    
    # If equipment is already checked out, redirect to detail page
    if status and status.get('checked_out'):
        flash('This equipment is already checked out', 'warning')
        return redirect(url_for('checkout.equipment_detail', equipment_id=equipment_id))
    
    # Handle form submission
    if request.method == 'POST':
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
            return redirect(url_for('checkout.equipment_detail', equipment_id=equipment_id))
        else:
            flash('Failed to check out equipment', 'danger')
    
    # Get user's preferred location from previous checkouts if available
    preferred_location = None
    user_history = checkout_manager.get_checkout_history(user=session['user']['username'])
    if user_history:
        # Find most recent checkout location
        for entry in sorted(user_history, key=lambda x: x.get('timestamp', ''), reverse=True):
            if entry.get('location'):
                preferred_location = entry.get('location')
                break
    
    # Get all locations for dropdown
    locations = equipment_manager.get_unique_locations()
    
    return render_template(
        'checkout/check_out.html',
        equipment=equipment,
        status=status,
        preferred_location=preferred_location,
        locations=locations
    )

@bp.route('/quick-check-in/<string:equipment_id>', methods=('GET', 'POST'))
@csrf.exempt
def quick_check_in(equipment_id):
    """Quick check-in without requiring login."""
    # Get equipment details
    equipment = equipment_manager.get_equipment_by_id(equipment_id)
    
    if not equipment:
        flash('Equipment not found', 'error')
        return redirect(url_for('dashboard.equipment_list'))
    
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
            users = {username: info for username, info in checkout_manager.users.items() 
                    if 'password' not in info}
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
    
    # Get all users for dropdown
    users = {username: info for username, info in checkout_manager.users.items() 
            if 'password' not in info}
    
    return render_template(
        'checkout/quick_check_in.html',
        equipment=equipment,
        status=status,
        locations=locations,
        users=users,
        checkout_manager=checkout_manager
    )

@bp.route('/check-in/<string:equipment_id>', methods=('GET', 'POST'))
@login_required
def check_in(equipment_id):
    """Dedicated check-in page with a pre-filled form."""
    # Get equipment details
    equipment = equipment_manager.get_equipment_by_id(equipment_id)
    
    if not equipment:
        flash('Equipment not found', 'error')
        return redirect(url_for('dashboard.equipment_list'))
    
    # Get status
    status = checkout_manager.get_equipment_status(equipment_id)
    
    # If equipment is not checked out, redirect to detail page
    if not status or not status.get('checked_out'):
        flash('This equipment is not checked out', 'warning')
        return redirect(url_for('checkout.equipment_detail', equipment_id=equipment_id))
    
    # If equipment is checked out by someone else, only admins can check it in
    if status.get('checked_out_by') != session['user']['username'] and session['user'].get('role') not in ['admin', 'physicist']:
        flash('You cannot check in equipment checked out by someone else', 'danger')
        return redirect(url_for('checkout.equipment_detail', equipment_id=equipment_id))
    
    # Handle form submission
    if request.method == 'POST':
        return_location = request.form.get('return_location')
        notes = request.form.get('notes', '')
        
        if checkout_manager.return_equipment(
            equipment_id,
            session['user']['username'],
            return_location,
            notes
        ):
            flash('Equipment checked in successfully', 'success')
            return redirect(url_for('checkout.equipment_detail', equipment_id=equipment_id))
        else:
            flash('Failed to check in equipment', 'danger')
    
    # Get all locations for dropdown
    locations = equipment_manager.get_unique_locations()
    
    return render_template(
        'checkout/check_in.html',
        equipment=equipment,
        status=status,
        locations=locations
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

            # Debug print - will show in server logs
            print(f"Add user request - username: {username}, name: {name}, email: {email}, role: {role}")
            print(f"Admin user: {session['user']['username']}")

            try:
                # Validate inputs to avoid common errors
                if not username or not username.strip():
                    flash('Username cannot be empty', 'danger')
                    return redirect(url_for('checkout.manage_users'))

                if not name or not name.strip():
                    flash('Name cannot be empty', 'danger')
                    return redirect(url_for('checkout.manage_users'))

                if not email or not email.strip():
                    flash('Email cannot be empty', 'danger')
                    return redirect(url_for('checkout.manage_users'))

                if not role or role not in ['admin', 'physicist', 'user']:
                    flash('Invalid role selected', 'danger')
                    return redirect(url_for('checkout.manage_users'))

                if not password or not password.strip():
                    flash('Password cannot be empty', 'danger')
                    return redirect(url_for('checkout.manage_users'))

                # Print the session data for debugging
                print(f"Session user data: {session.get('user', {})}")

                # Try to get the actual user data from checkout_manager
                user_data = checkout_manager.get_user(session['user']['username'])
                print(f"User from checkout_manager: {user_data}")

                # Use a hardcoded admin name (temporary fix)
                admin_username = session['user']['username']

                # Additional check - if user isn't working, try the default admin
                if admin_username not in checkout_manager.users or checkout_manager.users[admin_username].get('role') != 'admin':
                    print(f"Warning: Admin user {admin_username} not found or not admin, using 'admin' instead")
                    admin_username = 'admin'

                # Attempt to add user with better error reporting
                result = checkout_manager.add_user(
                    username,
                    name,
                    email,
                    role,
                    password,
                    admin_username  # Use the validated admin username
                )

                if result:
                    flash(f'User {username} added successfully', 'success')
                else:
                    # Check common issues
                    if username in checkout_manager.users:
                        flash(f'Username "{username}" already exists', 'danger')
                    elif session['user']['username'] not in checkout_manager.users:
                        flash('Admin user not found in user database', 'danger')
                    elif checkout_manager.users[session['user']['username']].get('role') != 'admin':
                        flash('You must have admin privileges to add users', 'danger')
                    else:
                        flash('Failed to add user - Check permissions to write to the data directory', 'danger')
            except Exception as e:
                import traceback
                traceback.print_exc()
                flash(f'Error adding user: {str(e)}', 'danger')
                
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
    
    # Get all users - make a clean copy without passwords
    users = {}
    for username, info in checkout_manager.users.items():
        # Create a copy of the user info without the password
        user_info = info.copy()
        if 'password' in user_info:
            user_info.pop('password')
        users[username] = user_info

    # Debug output
    print(f"Found {len(users)} users to display")

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
        
@bp.route('/notifications/history')
@physicist_required
def notification_history():
    """View notification history."""
    # Load notification logs
    logs_file_path = os.path.join(checkout_manager.data_dir, 'notification_logs.json')
    
    logs = []
    if os.path.exists(logs_file_path):
        try:
            with open(logs_file_path, 'r') as f:
                logs = json.load(f)
                
            # Sort logs by timestamp (newest first)
            logs.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        except Exception as e:
            flash(f'Error loading notification logs: {str(e)}', 'danger')
    
    return render_template(
        'checkout/notification_history.html',
        logs=logs
    )
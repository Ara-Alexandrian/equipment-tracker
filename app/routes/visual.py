"""
Visual dashboard routes for equipment status visualization
"""
from flask import Blueprint, render_template, request, jsonify, session
from app import equipment_manager, checkout_manager
import random
import functools

bp = Blueprint('visual', __name__, url_prefix='/visual')

def login_required(view):
    """View decorator that redirects anonymous users to the login page."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user' not in session:
            return jsonify({"error": "Authentication required"}), 401
        return view(**kwargs)
    return wrapped_view

@bp.route('/')
def index():
    """Visual dashboard home page."""
    # Get all equipment
    equipment_list = equipment_manager.get_all_equipment()
    
    # Get unique categories
    categories = set(item.get('category', 'Unknown') for item in equipment_list)
    
    return render_template(
        'visual/index.html',
        categories=categories
    )

@bp.route('/api/equipment')
def api_equipment():
    """API endpoint to get equipment data for visualization."""
    # Get all equipment
    equipment_list = equipment_manager.get_all_equipment()
    
    # Get filter parameters
    category = request.args.get('category')
    
    # Filter by category if specified
    if category:
        equipment_list = [item for item in equipment_list if item.get('category') == category]
    
    # Prepare nodes and links for visualization
    nodes = []
    links = []
    
    # Add category nodes
    category_nodes = {}
    for item in equipment_list:
        cat = item.get('category', 'Unknown')
        if cat not in category_nodes:
            category_nodes[cat] = {
                'id': 'cat_' + cat.replace(' ', '_'),
                'name': cat,
                'type': 'category',
                'group': 1,
                'size': 30,
                'count': 0
            }
            nodes.append(category_nodes[cat])
        
        # Increment category count
        category_nodes[cat]['count'] += 1
    
    # Update category node sizes based on counts
    for node in nodes:
        if node['type'] == 'category':
            node['size'] = max(30, min(80, 30 + node['count'] * 2))
    
    # Add manufacturer nodes
    mfg_nodes = {}
    for item in equipment_list:
        mfg = item.get('manufacturer', 'Unknown')
        cat = item.get('category', 'Unknown')
        
        if mfg not in mfg_nodes:
            mfg_nodes[mfg] = {
                'id': 'mfg_' + mfg.replace(' ', '_'),
                'name': mfg,
                'type': 'manufacturer',
                'group': 2,
                'size': 20,
                'count': 0
            }
            nodes.append(mfg_nodes[mfg])
            
            # Link to category
            links.append({
                'source': mfg_nodes[mfg]['id'],
                'target': category_nodes[cat]['id'],
                'value': 2
            })
        
        # Increment manufacturer count
        mfg_nodes[mfg]['count'] += 1
    
    # Update manufacturer node sizes based on counts
    for node in nodes:
        if node['type'] == 'manufacturer':
            node['size'] = max(15, min(40, 15 + node['count'] * 1.5))
    
    # Add equipment nodes
    for item in equipment_list:
        # Get equipment status
        status = checkout_manager.get_equipment_status(item.get('id'))
        
        # Determine node color by status
        status_color = '#28a745'  # Default: green for 'In Storage'
        if status.get('status') == 'Checked Out':
            status_color = '#007bff'  # Blue
        elif status.get('status') == 'In Calibration':
            status_color = '#17a2b8'  # Cyan
        elif status.get('status') == 'Under Repair':
            status_color = '#ffc107'  # Yellow
        elif status.get('status') == 'Out of Service':
            status_color = '#dc3545'  # Red
        
        # Create equipment node
        equipment_node = {
            'id': 'eq_' + item.get('id', 'unknown').replace(' ', '_'),
            'equipment_id': item.get('id'),
            'name': f"{item.get('manufacturer', '')} {item.get('model', '')}",
            'serial': item.get('serial_number', 'Unknown'),
            'type': 'equipment',
            'group': 3,
            'size': 10,
            'status': status.get('status', 'Unknown'),
            'location': status.get('location', 'Unknown'),
            'color': status_color
        }
        nodes.append(equipment_node)
        
        # Link to manufacturer
        mfg = item.get('manufacturer', 'Unknown')
        links.append({
            'source': equipment_node['id'],
            'target': mfg_nodes[mfg]['id'],
            'value': 1
        })
    
    return jsonify({
        'nodes': nodes,
        'links': links
    })

@bp.route('/api/equipment/status')
def api_equipment_status():
    """API endpoint to get equipment status summary for visualization."""
    # Get all status counts
    status_counts = {status: 0 for status in checkout_manager.STATUS_OPTIONS}
    
    # Count equipment by status
    for equipment_id in checkout_manager.equipment_status:
        status = checkout_manager.equipment_status[equipment_id].get('status')
        if status in status_counts:
            status_counts[status] += 1
    
    # Format for visualization
    result = []
    for status, count in status_counts.items():
        # Determine color by status
        color = '#28a745'  # Default: green for 'In Storage'
        if status == 'Checked Out':
            color = '#007bff'  # Blue
        elif status == 'In Calibration':
            color = '#17a2b8'  # Cyan
        elif status == 'Under Repair':
            color = '#ffc107'  # Yellow
        elif status == 'Out of Service':
            color = '#dc3545'  # Red
        
        result.append({
            'status': status,
            'count': count,
            'color': color
        })
    
    return jsonify(result)

@bp.route('/api/equipment/category')
def api_equipment_category():
    """API endpoint to get equipment counts by category."""
    # Get all equipment
    equipment_list = equipment_manager.get_all_equipment()
    
    # Count equipment by category
    category_counts = {}
    for item in equipment_list:
        category = item.get('category', 'Unknown')
        if category not in category_counts:
            category_counts[category] = 0
        category_counts[category] += 1
    
    # Format for visualization
    result = []
    for category, count in category_counts.items():
        result.append({
            'category': category,
            'count': count
        })
    
    return jsonify(result)

@bp.route('/api/calibration/schedule')
def api_calibration_schedule():
    """API endpoint to get calibration schedule data."""
    # Get equipment list with calibration data
    equipment_list = equipment_manager.get_all_equipment()
    
    # Group by month (random for demonstration)
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # In a real implementation, parse actual calibration dates
    # For now, generate random data for visualization
    monthly_data = {
        'all': {month: random.randint(0, 10) for month in months},
        'Chamber': {month: random.randint(0, 5) for month in months},
        'Electrometer': {month: random.randint(0, 3) for month in months},
        'Survey Meter': {month: random.randint(0, 4) for month in months}
    }
    
    return jsonify({
        'months': months,
        'data': monthly_data
    })
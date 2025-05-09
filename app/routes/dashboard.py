"""
Dashboard routes for the Equipment Tracker
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.equipment import EquipmentDataManager
from app import equipment_manager

bp = Blueprint('dashboard', __name__)

@bp.route('/')
def index():
    """Render the main dashboard page."""
    # Get equipment statistics
    stats = equipment_manager.get_equipment_stats()
    
    # Get the latest equipment
    latest_equipment = equipment_manager.get_all_equipment()[:10]
    
    return render_template(
        'dashboard/index.html', 
        stats=stats, 
        latest_equipment=latest_equipment
    )

@bp.route('/equipment')
def equipment_list():
    """Render the equipment list page."""
    # Get query parameters for filtering
    category = request.args.get('category')
    location = request.args.get('location')
    search_query = request.args.get('q')
    
    # Filter equipment based on parameters
    if category:
        equipment = equipment_manager.get_equipment_by_category(category)
    elif location:
        equipment = equipment_manager.get_equipment_by_location(location)
    elif search_query:
        equipment = equipment_manager.search_equipment(search_query)
    else:
        equipment = equipment_manager.get_all_equipment()
    
    # Get unique locations and manufacturers for filters
    locations = equipment_manager.get_unique_locations()
    
    return render_template(
        'dashboard/equipment_list.html',
        equipment=equipment,
        locations=locations,
        selected_category=category,
        selected_location=location,
        search_query=search_query
    )

@bp.route('/equipment/<string:equipment_id>')
def equipment_detail(equipment_id):
    """Render the equipment detail page."""
    # Get equipment by ID
    equipment = equipment_manager.get_equipment_by_id(equipment_id)
    
    if not equipment:
        flash('Equipment not found', 'error')
        return redirect(url_for('dashboard.equipment_list'))
    
    return render_template(
        'dashboard/equipment_detail.html',
        equipment=equipment
    )

@bp.route('/calibration')
def calibration_overview():
    """Render the calibration overview page."""
    # Get equipment with calibration due soon
    due_soon = equipment_manager.get_calibration_due_soon()
    
    return render_template(
        'dashboard/calibration.html',
        due_soon=due_soon
    )
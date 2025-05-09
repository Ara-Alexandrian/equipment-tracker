"""
Dashboard routes for the Equipment Tracker
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.equipment import EquipmentDataManager
from app import equipment_manager
from datetime import datetime

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
    """Render the calibration overview page with filtering options."""
    # Get filter parameters
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    status = request.args.get('status')
    
    # Parse dates if provided
    start_date = None
    end_date = None
    
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        except ValueError:
            pass
            
    if end_date_str:
        try:
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        except ValueError:
            pass
    
    # If no filters, just show equipment due soon
    if not start_date and not end_date and not status:
        due_soon = equipment_manager.get_calibration_due_soon()
        filtered_items = due_soon
    else:
        # Use the new filter function
        filtered_items = equipment_manager.filter_by_calibration_date(
            start_date=start_date,
            end_date=end_date,
            status=status
        )
    
    # Group by category
    items_by_category = {}
    for item in filtered_items:
        category = item.get('category', 'Unknown')
        if category not in items_by_category:
            items_by_category[category] = []
        items_by_category[category].append(item)
    
    # Calculate overall counts and percentages
    all_equipment = equipment_manager.get_all_equipment()
    total_count = len(all_equipment)
    filtered_count = len(filtered_items)
    
    filtered_percent = round(filtered_count / total_count * 100) if total_count > 0 else 0
    
    # Get counts by status for chart
    status_counts = {
        'current': 0,
        'due_soon': 0,
        'overdue': 0,
        'unknown': 0
    }
    
    for item in all_equipment:
        date_str = str(item.get('calibration_due_date', ''))
        cal_date = equipment_manager._parse_calibration_date(date_str)
        
        if not cal_date:
            status_counts['unknown'] += 1
            continue
        
        try:
            # Convert ISO format string back to datetime for comparison
            if isinstance(cal_date, str):
                try:
                    # Try to parse as ISO format
                    cal_date_dt = datetime.fromisoformat(cal_date)
                except ValueError:
                    # If that fails, it might not be an ISO string, mark as unknown
                    status_counts['unknown'] += 1
                    continue
            else:
                cal_date_dt = cal_date
                
            # Now it's safe to calculate the difference
            delta = cal_date_dt - datetime.now()
            
            if delta.days < 0:
                status_counts['overdue'] += 1
            elif delta.days <= 30:
                status_counts['due_soon'] += 1
            else:
                status_counts['current'] += 1
        except Exception as e:
            # If anything goes wrong, count as unknown
            status_counts['unknown'] += 1
            continue
    
    return render_template(
        'dashboard/calibration.html',
        filtered_items=filtered_items,
        items_by_category=items_by_category,
        filtered_count=filtered_count,
        total_count=total_count,
        filtered_percent=filtered_percent,
        status_counts=status_counts,
        start_date=start_date_str,
        end_date=end_date_str,
        status=status
    )
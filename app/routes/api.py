"""
API routes for the Equipment Tracker
"""
from flask import Blueprint, jsonify, request
from app import equipment_manager

bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/equipment')
def get_equipment():
    """Get all equipment or filtered by category, location, or search query."""
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
    
    return jsonify({
        'status': 'success',
        'count': len(equipment),
        'equipment': equipment
    })

@bp.route('/equipment/<string:equipment_id>')
def get_equipment_by_id(equipment_id):
    """Get equipment by ID."""
    equipment = equipment_manager.get_equipment_by_id(equipment_id)
    
    if not equipment:
        return jsonify({
            'status': 'error',
            'message': f'Equipment with ID {equipment_id} not found'
        }), 404
    
    return jsonify({
        'status': 'success',
        'equipment': equipment
    })

@bp.route('/stats')
def get_stats():
    """Get equipment statistics."""
    stats = equipment_manager.get_equipment_stats()
    
    return jsonify({
        'status': 'success',
        'stats': stats
    })

@bp.route('/locations')
def get_locations():
    """Get unique locations."""
    locations = equipment_manager.get_unique_locations()
    
    return jsonify({
        'status': 'success',
        'locations': locations
    })

@bp.route('/manufacturers')
def get_manufacturers():
    """Get unique manufacturers."""
    manufacturers = equipment_manager.get_unique_manufacturers()
    
    return jsonify({
        'status': 'success',
        'manufacturers': manufacturers
    })

@bp.route('/calibration/due-soon')
def get_calibration_due_soon():
    """Get equipment with calibration due soon."""
    days = request.args.get('days', 30, type=int)
    due_soon = equipment_manager.get_calibration_due_soon(days)
    
    return jsonify({
        'status': 'success',
        'count': len(due_soon),
        'equipment': due_soon
    })
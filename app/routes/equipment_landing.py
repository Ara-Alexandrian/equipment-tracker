"""
Equipment landing page routes for QR code scans
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import equipment_manager, checkout_manager
from app.models.ticket import TicketManager, EquipmentCondition
from datetime import datetime

bp = Blueprint('equipment', __name__, url_prefix='/equipment')

# Initialize ticket manager
ticket_manager = TicketManager()

@bp.route('/<string:equipment_id>')
def landing_page(equipment_id):
    """Landing page for equipment QR code scans"""
    # Get equipment details
    equipment = equipment_manager.get_equipment_by_id(equipment_id)
    
    if not equipment:
        flash('Equipment not found', 'danger')
        return redirect(url_for('dashboard.equipment_list'))
    
    # Get equipment status (checked out or available)
    status = checkout_manager.get_equipment_status(equipment_id)
    
    # Get equipment condition
    condition = ticket_manager.get_equipment_condition(equipment_id)
    
    # Get condition class (for display styling)
    condition_class = 'success'
    if condition == EquipmentCondition.WARNING:
        condition_class = 'warning'
    elif condition == EquipmentCondition.CRITICAL:
        condition_class = 'danger'
    
    # Check if the user is logged in
    is_logged_in = 'user' in session
    
    return render_template(
        'equipment/landing.html',
        equipment=equipment,
        status=status,
        condition=condition,
        condition_class=condition_class,
        is_logged_in=is_logged_in,
        checkout_manager=checkout_manager
    )
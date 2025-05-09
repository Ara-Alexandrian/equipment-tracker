"""
Admin routes for equipment management and reporting
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app import equipment_manager
from app.routes.checkout import admin_required, physicist_required
from datetime import datetime
import json
import os

bp = Blueprint('admin', __name__, url_prefix='/admin')

@bp.route('/equipment')
@admin_required
def equipment_management():
    """Equipment management page for administrators."""
    # Get equipment information
    all_equipment = equipment_manager.get_all_equipment()
    
    # Get stats for cards
    stats = equipment_manager.get_equipment_stats()
    
    # Get filter parameters
    category = request.args.get('category')
    location = request.args.get('location')
    manufacturer = request.args.get('manufacturer')
    
    # Apply filters if provided
    filtered_equipment = all_equipment
    if category:
        filtered_equipment = [item for item in filtered_equipment if item.get('category') == category]
    if location:
        filtered_equipment = [item for item in filtered_equipment if item.get('location') == location]
    if manufacturer:
        filtered_equipment = [item for item in filtered_equipment if item.get('manufacturer') == manufacturer]
    
    # Get unique values for filters
    manufacturers = equipment_manager.get_unique_manufacturers()
    locations = equipment_manager.get_unique_locations()
    
    # Get categories (Chamber, Electrometer, Survey Meter)
    categories = ['Chamber', 'Electrometer', 'Survey Meter']
    
    return render_template(
        'admin/equipment_management.html',
        equipment=filtered_equipment,
        stats=stats,
        manufacturers=manufacturers,
        locations=locations,
        categories=categories,
        selected_category=category,
        selected_location=location,
        selected_manufacturer=manufacturer
    )

@bp.route('/equipment/create', methods=['POST'])
@admin_required
def create_equipment():
    """Create a new equipment item."""
    # Get form data
    equipment_id = request.form.get('equipment_id')
    category = request.form.get('category')
    equipment_type = request.form.get('equipment_type')
    manufacturer = request.form.get('manufacturer')
    model = request.form.get('model')
    serial_number = request.form.get('serial_number')
    location = request.form.get('location')
    calibration_due_date = request.form.get('calibration_due_date')
    notes = request.form.get('notes', '')
    
    # Generate a default ID if not provided
    if not equipment_id:
        equipment_id = f"{category}-{manufacturer}-{serial_number}"
    
    # Load existing equipment data
    equipment_json = os.path.join(equipment_manager.data_dir, 'equipment.json')
    
    try:
        with open(equipment_json, 'r') as f:
            equipment_data = json.load(f)
    except:
        equipment_data = []
    
    # Check if equipment with this ID already exists
    for item in equipment_data:
        if item.get('id') == equipment_id:
            flash(f'Equipment with ID {equipment_id} already exists', 'danger')
            return redirect(url_for('admin.equipment_management'))
    
    # Create new equipment item
    new_equipment = {
        'id': equipment_id,
        'category': category,
        'equipment_type': equipment_type,
        'manufacturer': manufacturer,
        'model': model,
        'serial_number': serial_number,
        'location': location,
        'calibration_due_date': calibration_due_date,
        'notes': notes
    }
    
    # Add to the list
    equipment_data.append(new_equipment)
    
    # Save the updated data
    try:
        with open(equipment_json, 'w') as f:
            json.dump(equipment_data, f, indent=2)
        flash(f'Equipment {equipment_id} added successfully', 'success')
        
        # Force reload of equipment data
        equipment_manager.load_data()
    except Exception as e:
        flash(f'Error saving equipment data: {str(e)}', 'danger')
    
    return redirect(url_for('admin.equipment_management'))

@bp.route('/equipment/edit/<string:equipment_id>', methods=['POST'])
@admin_required
def edit_equipment(equipment_id):
    """Edit an existing equipment item."""
    # Get form data
    category = request.form.get('category')
    equipment_type = request.form.get('equipment_type')
    manufacturer = request.form.get('manufacturer')
    model = request.form.get('model')
    serial_number = request.form.get('serial_number')
    location = request.form.get('location')
    calibration_due_date = request.form.get('calibration_due_date')
    notes = request.form.get('notes', '')
    
    # Load existing equipment data
    equipment_json = os.path.join(equipment_manager.data_dir, 'equipment.json')
    
    try:
        with open(equipment_json, 'r') as f:
            equipment_data = json.load(f)
    except:
        flash('Error loading equipment data', 'danger')
        return redirect(url_for('admin.equipment_management'))
    
    # Find and update the equipment item
    found = False
    for item in equipment_data:
        if item.get('id') == equipment_id:
            item.update({
                'category': category,
                'equipment_type': equipment_type,
                'manufacturer': manufacturer,
                'model': model,
                'serial_number': serial_number,
                'location': location,
                'calibration_due_date': calibration_due_date,
                'notes': notes
            })
            found = True
            break
    
    if not found:
        flash(f'Equipment with ID {equipment_id} not found', 'danger')
        return redirect(url_for('admin.equipment_management'))
    
    # Save the updated data
    try:
        with open(equipment_json, 'w') as f:
            json.dump(equipment_data, f, indent=2)
        flash(f'Equipment {equipment_id} updated successfully', 'success')
        
        # Force reload of equipment data
        equipment_manager.load_data()
    except Exception as e:
        flash(f'Error saving equipment data: {str(e)}', 'danger')
    
    return redirect(url_for('admin.equipment_management'))

@bp.route('/equipment/delete/<string:equipment_id>', methods=['POST'])
@admin_required
def delete_equipment(equipment_id):
    """Delete an equipment item."""
    # Load existing equipment data
    equipment_json = os.path.join(equipment_manager.data_dir, 'equipment.json')
    
    try:
        with open(equipment_json, 'r') as f:
            equipment_data = json.load(f)
    except:
        flash('Error loading equipment data', 'danger')
        return redirect(url_for('admin.equipment_management'))
    
    # Find and remove the equipment item
    found = False
    for i, item in enumerate(equipment_data):
        if item.get('id') == equipment_id:
            del equipment_data[i]
            found = True
            break
    
    if not found:
        flash(f'Equipment with ID {equipment_id} not found', 'danger')
        return redirect(url_for('admin.equipment_management'))
    
    # Save the updated data
    try:
        with open(equipment_json, 'w') as f:
            json.dump(equipment_data, f, indent=2)
        flash(f'Equipment {equipment_id} deleted successfully', 'success')
        
        # Force reload of equipment data
        equipment_manager.load_data()
    except Exception as e:
        flash(f'Error saving equipment data: {str(e)}', 'danger')
    
    return redirect(url_for('admin.equipment_management'))

@bp.route('/reports')
@physicist_required
def reports():
    """Report generation page."""
    return render_template('admin/reports.html')

@bp.route('/generate-report', methods=['POST'])
@physicist_required
def generate_report():
    """Generate a report based on form data and forward to the report generator."""
    # Get report parameters
    report_type = request.form.get('report_type', 'inventory')
    report_format = request.form.get('report_format', 'pdf')
    date_range = request.form.get('date_range', 'all')
    
    # Forward to the reports blueprint which has the actual implementation
    try:
        from app.routes.reports import generate_report as reports_generate_report
        return reports_generate_report()
    except Exception as e:
        # Log the error and return a friendly error message
        print(f"Error generating report: {str(e)}")
        return jsonify({
            "status": "error",
            "error": f"Error generating report: {str(e)}"
        }), 500
"""
Admin routes for equipment management and reporting
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from app import equipment_manager
from app.routes.checkout import admin_required, physicist_required
from datetime import datetime
import json
import os
import sys
import subprocess
import tempfile
import uuid
from pathlib import Path

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
    view_mode = request.args.get('mode', 'normal') # 'normal' or 'direct'

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

    # Determine which template to use based on view mode
    if view_mode == 'direct':
        template_name = 'admin/equipment_direct_list.html'
    else:
        # Use the default template (with JS)
        template_name = 'admin/equipment_management.html'

    return render_template(
        template_name,
        equipment=filtered_equipment,
        stats=stats,
        manufacturers=manufacturers,
        locations=locations,
        categories=categories,
        selected_category=category,
        selected_location=location,
        selected_manufacturer=manufacturer
    )

@bp.route('/equipment/direct')
@admin_required
def equipment_management_direct():
    """Direct server-side equipment management page without JavaScript."""
    return redirect(url_for('admin.equipment_management', mode='direct'))

# Route removed - consolidated into main equipment_management route

@bp.route('/equipment-test')
@admin_required
def equipment_test():
    """Test page for equipment edit functions."""
    return render_template('admin/direct_form_test.html')

@bp.route('/equipment/<string:equipment_id>')
@admin_required
def get_equipment_by_id(equipment_id):
    """API endpoint to get equipment data by ID."""
    equipment = equipment_manager.get_equipment_by_id(equipment_id)

    if equipment:
        return jsonify({
            'status': 'success',
            'equipment': equipment
        })
    else:
        return jsonify({
            'status': 'error',
            'message': f'Equipment with ID {equipment_id} not found'
        }), 404

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

@bp.route('/equipment/<string:equipment_id>/edit')
@admin_required
def edit_equipment_direct(equipment_id):
    """Direct equipment edit page with server-side form population."""
    from app import standard_values_manager

    # Get equipment by ID
    equipment = equipment_manager.get_equipment_by_id(equipment_id)

    if not equipment:
        flash(f'Equipment with ID {equipment_id} not found', 'danger')
        return redirect(url_for('admin.equipment_management'))

    # Print debug data to server console for troubleshooting
    print(f"DEBUG: Editing equipment with ID: {equipment_id}")
    print(f"DEBUG: Equipment data: {equipment}")

    # Get the equipment directly from JSON file as a fallback method
    json_file = os.path.join(equipment_manager.data_dir, 'equipment.json')
    try:
        with open(json_file, 'r') as f:
            all_equipment = json.load(f)

        # Find the equipment item by ID
        for item in all_equipment:
            if item.get('id') == equipment_id:
                equipment = item
                print(f"DEBUG: Found equipment in direct JSON: {equipment}")
                break
    except Exception as e:
        print(f"DEBUG: Error reading JSON file: {e}")

    # If we still don't have valid equipment data, show an error
    if not equipment:
        flash(f'Error: Could not retrieve equipment data for ID {equipment_id}', 'danger')
        return redirect(url_for('admin.equipment_management'))

    # Get standard values for dropdown lists
    standard_categories = standard_values_manager.get_categories()

    # Get equipment types based on the current category
    current_category = equipment.get('category', '')
    if current_category:
        standard_equipment_types = standard_values_manager.get_equipment_types(current_category)
    else:
        standard_equipment_types = standard_values_manager.get_equipment_types()

    # Create a dictionary of equipment types by category for JavaScript
    equipment_types_by_category = {}
    for category in standard_categories:
        equipment_types_by_category[category] = standard_values_manager.get_equipment_types(category)

    standard_manufacturers = standard_values_manager.get_manufacturers()
    standard_locations = standard_values_manager.get_locations()

    return render_template(
        'admin/equipment_direct_edit.html',
        equipment=equipment,
        standard_categories=standard_categories,
        standard_equipment_types=standard_equipment_types,
        standard_manufacturers=standard_manufacturers,
        standard_locations=standard_locations,
        equipment_types_by_category=equipment_types_by_category
    )

@bp.route('/equipment/<string:equipment_id>/update', methods=['POST'])
@admin_required
def update_equipment_direct(equipment_id):
    """Update equipment from the direct edit page."""
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

@bp.route('/equipment/<string:equipment_id>/qr')
@admin_required
def generate_qr_direct(equipment_id):
    """Generate QR code for equipment with server-side rendering."""
    # Get equipment by ID
    equipment = equipment_manager.get_equipment_by_id(equipment_id)

    if not equipment:
        flash(f'Equipment with ID {equipment_id} not found', 'danger')
        return redirect(url_for('admin.equipment_management'))

    # Create URL for QR code - ensure it's the equipment landing page
    qr_url = url_for('qr.equipment_detail', equipment_id=equipment_id, _external=True)

    # Create output directory
    static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
    qr_dir = os.path.join(static_dir, 'qrcodes')
    os.makedirs(qr_dir, exist_ok=True)

    # Create a unique filename for this QR code
    filename = f"qr_{equipment_id}_{uuid.uuid4().hex[:8]}.png"
    output_path = os.path.join(qr_dir, filename)

    try:
        # Try to use the advanced QR code generator first
        try:
            # Import the advanced generator from qrcodes directory
            sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'qrcodes'))
            from qr_generator import create_qr_in_flame

            # Get the logo path from Resources directory
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

            # Try multiple potential logo paths
            potential_paths = [
                os.path.join(root_dir, 'qrcodes', 'Resources', 'Mary Bird Perkins Cancer Center.png'),
                os.path.join(root_dir, 'Resources', 'Mary Bird Perkins Cancer Center.png'),
                os.path.join(root_dir, 'Resources', 'mbp.png')
            ]

            # Find the first existing logo file
            logo_path = None
            for path in potential_paths:
                if os.path.exists(path):
                    logo_path = path
                    break

            # If no logo file exists, fall back to the simple generator
            if not logo_path:
                raise FileNotFoundError(f"Logo file not found in any of the expected locations")

            print(f"Using logo at: {logo_path}")

            # Generate the fancy QR code with the flame logo
            create_qr_in_flame(
                logo_path=logo_path,
                url=qr_url,
                output_path=output_path,
                manufacturer=equipment.get('manufacturer', ''),
                model=equipment.get('model', ''),
                serial=equipment.get('serial_number', '')
            )

            print(f"Advanced QR code generated at {output_path}")

        except Exception as advanced_error:
            print(f"Error with advanced QR generator: {str(advanced_error)}")
            # Fall back to the simple generator
            from app.routes.simple_qr import generate_simple_qr

            success, result = generate_simple_qr(
                url=qr_url,
                output_path=output_path,
                equipment_id=equipment_id,
                manufacturer=equipment.get('manufacturer', ''),
                model=equipment.get('model', ''),
                serial=equipment.get('serial_number', '')
            )

            if not success:
                raise Exception(f"Simple QR code generator failed: {result}")

        # Generate URL for the QR code
        qr_code_url = url_for('static', filename=f'qrcodes/{filename}')

        # Create a QR display template
        return render_template(
            'ticket/qr_code.html',
            qr_code_url=qr_code_url,
            equipment=equipment,
            equipment_id=equipment_id,
            qr_url=qr_url,
            back_url=url_for('admin.equipment_management')
        )

    except Exception as e:
        flash(f'Error generating QR code: {str(e)}', 'danger')
        return redirect(url_for('admin.equipment_management'))

@bp.route('/equipment/generate-qr', methods=['POST'])
@admin_required
def generate_qr_code():
    """Generate a QR code for an equipment item."""
    try:
        # Get request data
        data = request.json
        print(f"Generate QR code request data: {data}")

        if not data:
            print("No data provided")
            return jsonify({
                "status": "error",
                "message": "No data provided"
            }), 400

        # Get required parameters
        url = data.get('url')
        equipment_id = data.get('equipment_id')
        manufacturer = data.get('manufacturer', '')
        model = data.get('model', '')
        serial = data.get('serial', '')

        print(f"QR Code parameters: url={url}, equipment_id={equipment_id}, manufacturer={manufacturer}, model={model}, serial={serial}")

        if not url or not equipment_id:
            print("URL and equipment ID are required")
            return jsonify({
                "status": "error",
                "message": "URL and equipment ID are required"
            }), 400

        # Create output directory
        static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
        qr_dir = os.path.join(static_dir, 'qrcodes')
        os.makedirs(qr_dir, exist_ok=True)
        print(f"QR code output directory: {qr_dir}")

        # Create a unique filename for this QR code
        filename = f"qr_{equipment_id}_{uuid.uuid4().hex[:8]}.png"
        output_path = os.path.join(qr_dir, filename)
        print(f"QR code output path: {output_path}")

        # Try to use the advanced QR code generator first
        try:
            # Import the advanced generator from qrcodes directory
            sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'qrcodes'))
            from qr_generator import create_qr_in_flame
            
            # Get the logo path
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
            logo_path = os.path.join(root_dir, 'qrcodes', 'Resources', 'Mary Bird Perkins Cancer Center.png')
            
            # If logo file doesn't exist, fall back to the simple generator
            if not os.path.exists(logo_path):
                raise FileNotFoundError(f"Logo file not found at {logo_path}")
            
            # Generate the fancy QR code with the flame logo
            create_qr_in_flame(
                logo_path=logo_path,
                url=url,
                output_path=output_path,
                manufacturer=manufacturer,
                model=model,
                serial=serial
            )
            
            print(f"Advanced QR code generated at {output_path}")
            
        except Exception as advanced_error:
            print(f"Error with advanced QR generator: {str(advanced_error)}")
            # Fall back to simple QR generator
            try:
                print("Using simple QR code generator...")
                from app.routes.simple_qr import generate_simple_qr
                
                success, result = generate_simple_qr(
                    url=url,
                    output_path=output_path,
                    equipment_id=equipment_id,
                    manufacturer=manufacturer,
                    model=model,
                    serial=serial
                )
                
                if not success:
                    print(f"Simple QR code generator failed: {result}")
                    raise Exception(f"Simple QR code generator failed: {result}")
                    
                print(f"Simple QR code generated at {output_path}")
                
            except Exception as e:
                print(f"Error with simple QR generator: {str(e)}")
                # Fallback to extremely basic QR code
                try:
                    print("Falling back to extremely basic QR code generation...")
                    import qrcode
                    
                    # Generate extremely basic QR code
                    qr = qrcode.QRCode(
                        version=1,
                        error_correction=qrcode.constants.ERROR_CORRECT_H,
                        box_size=10,
                        border=4,
                    )
                    qr.add_data(url)
                    qr.make(fit=True)
                    
                    img = qr.make_image(fill_color="black", back_color="white")
                    img.save(output_path)
                    print(f"Extremely basic QR code generated at {output_path}")
                except Exception as qr_error:
                    print(f"Fallback QR code generation failed: {str(qr_error)}")
                    return jsonify({
                        "status": "error",
                        "message": f"All QR code generation methods failed: {str(qr_error)}"
                    }), 500

        # Check if file was created
        if not os.path.exists(output_path):
            print(f"QR code file was not created at {output_path}")
            return jsonify({
                "status": "error",
                "message": "QR code file was not created"
            }), 500

        # Generate URL for the QR code
        qr_code_url = url_for('static', filename=f'qrcodes/{filename}')
        print(f"QR code URL: {qr_code_url}")

        return jsonify({
            "status": "success",
            "message": "QR code generated successfully",
            "qr_code_url": qr_code_url,
            "equipment_id": equipment_id,
            "qr_url": url
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"Error generating QR code: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Error generating QR code: {str(e)}"
        }), 500

@bp.route('/settings')
@admin_required
def settings():
    """Admin settings page for managing standard values."""
    from app import standard_values_manager, equipment_manager, checkout_manager

    # Get message from flash session
    message = request.args.get('message')
    message_type = request.args.get('type', 'info')

    # Get standard values
    categories = standard_values_manager.get_categories()

    # Create a dictionary of equipment types by category
    equipment_types = {}
    for category in categories:
        equipment_types[category] = standard_values_manager.get_equipment_types(category)

    manufacturers = standard_values_manager.get_manufacturers()
    locations = standard_values_manager.get_locations()

    # Get system statistics
    equipment_count = len(equipment_manager.get_all_equipment())

    # Get checkout count
    try:
        checkout_count = len(checkout_manager.get_all_checkouts())
    except:
        checkout_count = 0

    # Get user count
    try:
        user_count = len(checkout_manager.users)
    except:
        user_count = 0

    return render_template(
        'admin/settings.html',
        categories=categories,
        equipment_types=equipment_types,
        manufacturers=manufacturers,
        locations=locations,
        equipment_count=equipment_count,
        checkout_count=checkout_count,
        user_count=user_count,
        message=message,
        message_type=message_type
    )

@bp.route('/settings/add', methods=['POST'])
@admin_required
def add_standard_value():
    """Add a new standard value."""
    from app import standard_values_manager

    # Get form data
    value_type = request.form.get('value_type')
    value = request.form.get('value')
    category = request.form.get('category', '')

    if not value_type or not value:
        return redirect(url_for('admin.settings', message='Missing required fields', type='danger'))

    result = False

    # Add the value based on type
    if value_type == 'category':
        result = standard_values_manager.add_category(value)
    elif value_type == 'equipment_type':
        if not category:
            return redirect(url_for('admin.settings', message='Category is required for equipment types', type='danger'))
        result = standard_values_manager.add_equipment_type(value, category)
    elif value_type == 'manufacturer':
        result = standard_values_manager.add_manufacturer(value)
    elif value_type == 'location':
        result = standard_values_manager.add_location(value)

    if result:
        return redirect(url_for('admin.settings', message=f'{value_type.title()} "{value}" added successfully', type='success'))
    else:
        return redirect(url_for('admin.settings', message=f'Failed to add {value_type} "{value}"', type='danger'))

@bp.route('/settings/remove', methods=['POST'])
@admin_required
def remove_standard_value():
    """Remove a standard value."""
    from app import standard_values_manager

    # Get form data
    value_type = request.form.get('value_type')
    value = request.form.get('value')
    category = request.form.get('category', '')

    if not value_type or not value:
        return redirect(url_for('admin.settings', message='Missing required fields', type='danger'))

    result = False

    # Remove the value based on type
    if value_type == 'category':
        result = standard_values_manager.remove_category(value)
    elif value_type == 'equipment_type':
        if not category:
            return redirect(url_for('admin.settings', message='Category is required for equipment types', type='danger'))
        result = standard_values_manager.remove_equipment_type(value, category)
    elif value_type == 'manufacturer':
        result = standard_values_manager.remove_manufacturer(value)
    elif value_type == 'location':
        result = standard_values_manager.remove_location(value)

    if result:
        return redirect(url_for('admin.settings', message=f'{value_type.title()} "{value}" removed successfully', type='success'))
    else:
        return redirect(url_for('admin.settings', message=f'Failed to remove {value_type} "{value}"', type='danger'))

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
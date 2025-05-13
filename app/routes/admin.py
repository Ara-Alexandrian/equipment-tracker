"""
Admin routes for equipment management and reporting
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from app import equipment_manager, checkout_manager
from app.routes.checkout import admin_required, physicist_required
from app.routes.dashboard import ticket_manager
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

    # We now have ticket_manager and checkout_manager imported at the top of the file

    return render_template(
        template_name,
        equipment=filtered_equipment,
        stats=stats,
        manufacturers=manufacturers,
        locations=locations,
        categories=categories,
        selected_category=category,
        selected_location=location,
        selected_manufacturer=manufacturer,
        checkout_manager=checkout_manager,
        ticket_manager=ticket_manager
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
    
    # Load existing equipment data using our custom utilities
    from app.models.json_utils import load_json

    equipment_json = os.path.join(equipment_manager.data_dir, 'equipment.json')
    equipment_data = load_json(equipment_json) or []
    
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
    
    # Save the updated data using our custom utilities
    from app.models.json_utils import save_json

    try:
        success = save_json(equipment_data, equipment_json, indent=2)
        if success:
            flash(f'Equipment {equipment_id} added successfully', 'success')
            # Force reload of equipment data
            equipment_manager.load_data()
        else:
            flash(f'Error saving equipment data', 'danger')
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
    from app.models.json_utils import load_json

    equipment_json = os.path.join(equipment_manager.data_dir, 'equipment.json')
    equipment_data = load_json(equipment_json)

    if not equipment_data:
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
        from app.models.json_utils import save_json
        success = save_json(equipment_data, equipment_json, indent=2)
        if success:
            flash(f'Equipment {equipment_id} updated successfully', 'success')
            # Force reload of equipment data
            equipment_manager.load_data()
        else:
            flash(f'Error saving equipment data', 'danger')
    except Exception as e:
        flash(f'Error saving equipment data: {str(e)}', 'danger')
    
    return redirect(url_for('admin.equipment_management'))

@bp.route('/equipment/delete/<string:equipment_id>', methods=['POST'])
@admin_required
def delete_equipment(equipment_id):
    """
    Delete an equipment item and all related records:
    - Equipment data
    - Tickets associated with the equipment
    - Equipment status and checkout history
    - QR codes generated for the equipment
    """
    # Initialize counters for tracking what was deleted
    deleted_items = {
        'equipment': 0,
        'tickets': 0,
        'qr_codes': 0,
        'status': 0,
        'history': 0,
        'conditions': 0
    }

    try:
        # 1. First, load and delete the equipment record
        from app.models.json_utils import load_json

        equipment_json = os.path.join(equipment_manager.data_dir, 'equipment.json')
        equipment_data = load_json(equipment_json)

        if not equipment_data:
            flash('Error loading equipment data', 'danger')
            return redirect(url_for('admin.equipment_management'))

        # Find and remove the equipment item
        found = False
        for i, item in enumerate(equipment_data):
            if item.get('id') == equipment_id:
                del equipment_data[i]
                found = True
                deleted_items['equipment'] = 1
                break

        if not found:
            flash(f'Equipment with ID {equipment_id} not found', 'danger')
            return redirect(url_for('admin.equipment_management'))

        # 2. Delete all tickets associated with this equipment
        # First, get all tickets for this equipment
        related_tickets = ticket_manager.get_tickets_by_equipment(equipment_id)

        if related_tickets:
            # Create a copy of ticket_manager.tickets before we modify it
            tickets_dict = ticket_manager.tickets.copy()

            # Remove tickets for this equipment
            for ticket in related_tickets:
                if ticket.id in tickets_dict:
                    del tickets_dict[ticket.id]
                    deleted_items['tickets'] += 1

            # Replace the tickets dictionary and save
            ticket_manager.tickets = tickets_dict
            ticket_manager._save_tickets()

        # 3. Delete equipment condition record
        if equipment_id in ticket_manager.equipment_conditions:
            del ticket_manager.equipment_conditions[equipment_id]
            ticket_manager._save_equipment_conditions()
            deleted_items['conditions'] = 1

        # 4. Delete equipment status record
        if equipment_id in checkout_manager.equipment_status:
            del checkout_manager.equipment_status[equipment_id]
            checkout_manager._save_equipment_status()
            deleted_items['status'] = 1

        # 5. Filter checkout history to remove entries for this equipment
        if checkout_manager.checkout_history:
            original_count = len(checkout_manager.checkout_history)
            checkout_manager.checkout_history = [
                entry for entry in checkout_manager.checkout_history
                if entry.get('equipment_id') != equipment_id
            ]
            deleted_items['history'] = original_count - len(checkout_manager.checkout_history)
            checkout_manager._save_checkout_history()

        # 6. Delete QR code files associated with this equipment
        # Determine QR code directory
        static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
        qr_dir = os.path.join(static_dir, 'qrcodes')

        if os.path.exists(qr_dir):
            # Delete standard QR code
            standard_qr = os.path.join(qr_dir, f"qr_{equipment_id}.png")
            if os.path.exists(standard_qr):
                os.remove(standard_qr)
                deleted_items['qr_codes'] += 1

            # Delete legacy QR codes with hash
            import glob
            legacy_qr_pattern = os.path.join(qr_dir, f"qr_{equipment_id}_*.png")
            for qr_file in glob.glob(legacy_qr_pattern):
                os.remove(qr_file)
                deleted_items['qr_codes'] += 1

            # Delete URL text files if they exist
            url_file = os.path.join(qr_dir, f"temp_url_{equipment_id}.txt")
            if os.path.exists(url_file):
                os.remove(url_file)

        # 7. Finally, save the updated equipment data
        from app.models.json_utils import save_json
        save_json(equipment_data, equipment_json, indent=2)

        # Force reload of equipment data
        equipment_manager.load_data()

        # Create a detailed success message
        success_msg = f"Equipment {equipment_id} deleted successfully with {deleted_items['tickets']} tickets, "
        success_msg += f"{deleted_items['qr_codes']} QR codes, {deleted_items['history']} history records"
        flash(success_msg, 'success')

    except Exception as e:
        import traceback
        traceback.print_exc()
        flash(f'Error during cascade deletion: {str(e)}', 'danger')

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
    from app.models.json_utils import load_json

    json_file = os.path.join(equipment_manager.data_dir, 'equipment.json')
    all_equipment = load_json(json_file) or []

    # Find the equipment item by ID
    for item in all_equipment:
        if item.get('id') == equipment_id:
            equipment = item
            print(f"DEBUG: Found equipment in direct JSON: {equipment}")
            break

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
        equipment_types_by_category=equipment_types_by_category,
        checkout_manager=checkout_manager,
        ticket_manager=ticket_manager
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
    from app.models.json_utils import load_json

    equipment_json = os.path.join(equipment_manager.data_dir, 'equipment.json')
    equipment_data = load_json(equipment_json)

    if not equipment_data:
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
        from app.models.json_utils import save_json
        success = save_json(equipment_data, equipment_json, indent=2)
        if success:
            flash(f'Equipment {equipment_id} updated successfully', 'success')
            # Force reload of equipment data
            equipment_manager.load_data()
        else:
            flash(f'Error saving equipment data', 'danger')
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

    # Use consistent filename pattern for equipment QR codes
    # First, remove any existing QR codes for this equipment to avoid clutter
    import glob
    existing_qr_pattern = os.path.join(qr_dir, f"qr_{equipment_id}_*.png")
    for old_qr in glob.glob(existing_qr_pattern):
        try:
            os.remove(old_qr)
            print(f"Removed old QR code: {old_qr}")
        except Exception as e:
            print(f"Could not remove old QR code: {e}")

    # Create a predictable, consistent filename for each equipment
    # Always use the same formula so we can find it again later
    filename = f"qr_{equipment_id}.png"  # Simple, consistent, no randomness
    output_path = os.path.join(qr_dir, filename)

    try:
        # Use the direct QR code generator for more reliability
        from app.routes.direct_qr import generate_direct_qr

        success, result = generate_direct_qr(
            url=qr_url,
            output_path=output_path,
            equipment_id=equipment_id,
            manufacturer=equipment.get('manufacturer', ''),
            model=equipment.get('model', ''),
            serial=equipment.get('serial_number', '')
        )

        if not success:
            raise Exception(f"QR code generation failed: {result}")

        # Generate URL for the QR code
        qr_code_url = url_for('static', filename=f'qrcodes/{filename}')

        # Add cache buster to avoid browser caching
        import random
        qr_code_url = f"{qr_code_url}?v={random.randint(1000, 9999)}"

        # Instead of rendering a whole new page, return a JSON response with the QR data
        # This will allow us to handle it with JavaScript in a modal
        return jsonify({
            "status": "success",
            "message": "QR code generated successfully",
            "qr_code_url": qr_code_url,
            "equipment_id": equipment_id,
            "equipment": equipment,
            "qr_url": qr_url
        })

    except Exception as e:
        # Return error as JSON for easier handling with JavaScript
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": f"Error generating QR code: {str(e)}"
        }), 500

@bp.route('/equipment/check-qr/<string:equipment_id>', methods=['GET'])
@physicist_required
def check_qr_code(equipment_id):
    """Check if a QR code exists for the given equipment ID."""
    try:
        # Create output directory path
        static_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static')
        qr_dir = os.path.join(static_dir, 'qrcodes')

        # Check for standard filename
        filename = f"qr_{equipment_id}.png"
        qr_path = os.path.join(qr_dir, filename)

        if os.path.exists(qr_path):
            # Generate URL for the existing QR code
            qr_code_url = url_for('static', filename=f'qrcodes/{filename}')

            # Add cache buster to avoid browser caching
            import random
            qr_code_url_with_cache_buster = f"{qr_code_url}?v={random.randint(1000, 9999)}"

            return jsonify({
                "status": "success",
                "exists": True,
                "qr_code_url": qr_code_url_with_cache_buster,
                "equipment_id": equipment_id
            })

        # Also check for legacy format with hash
        import glob
        existing_qr_pattern = os.path.join(qr_dir, f"qr_{equipment_id}_*.png")
        existing_files = glob.glob(existing_qr_pattern)

        if existing_files:
            # Use the first matching file
            legacy_filename = os.path.basename(existing_files[0])
            qr_code_url = url_for('static', filename=f'qrcodes/{legacy_filename}')

            # Add cache buster to avoid browser caching
            import random
            qr_code_url_with_cache_buster = f"{qr_code_url}?v={random.randint(1000, 9999)}"

            return jsonify({
                "status": "success",
                "exists": True,
                "qr_code_url": qr_code_url_with_cache_buster,
                "equipment_id": equipment_id
            })

        return jsonify({
            "status": "success",
            "exists": False,
            "equipment_id": equipment_id
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": f"Error checking QR code: {str(e)}"
        }), 500

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

        # Use consistent filename pattern for equipment QR codes
        # Check if the code should be regenerated
        force_regenerate = data.get('force_regenerate', False)

        # Check if a QR code already exists with the new naming standard
        filename = f"qr_{equipment_id}.png"  # Simple, consistent, no randomness
        output_path = os.path.join(qr_dir, filename)

        # If the QR code already exists and we're not forcing regeneration, just return it
        if os.path.exists(output_path) and not force_regenerate:
            print(f"QR code already exists at {output_path} and force_regenerate is False, returning existing QR code")
            qr_code_url = url_for('static', filename=f'qrcodes/{filename}')
            import random
            qr_code_url_with_cache_buster = f"{qr_code_url}?v={random.randint(1000, 9999)}"

            return jsonify({
                "status": "success",
                "message": "QR code already exists",
                "qr_code_url": qr_code_url_with_cache_buster,
                "equipment_id": equipment_id,
                "qr_url": url
            })

        # If we're here, either the QR code doesn't exist or we're regenerating
        # First, remove any existing QR codes for this equipment to avoid clutter
        import glob
        existing_qr_pattern = os.path.join(qr_dir, f"qr_{equipment_id}_*.png")
        for old_qr in glob.glob(existing_qr_pattern):
            try:
                os.remove(old_qr)
                print(f"Removed old QR code: {old_qr}")
            except Exception as e:
                print(f"Could not remove old QR code: {e}")

        # Also remove the standardized filename if it exists
        if os.path.exists(output_path):
            try:
                os.remove(output_path)
                print(f"Removed existing QR code: {output_path}")
            except Exception as e:
                print(f"Could not remove existing QR code: {e}")

        print(f"QR code output path: {output_path}")

        # Use the direct QR code generator for more reliability
        try:
            print("Using direct QR code generator...")
            from app.routes.direct_qr import generate_direct_qr

            success, result = generate_direct_qr(
                url=url,
                output_path=output_path,
                equipment_id=equipment_id,
                manufacturer=manufacturer,
                model=model,
                serial=serial
            )

            if not success:
                print(f"Direct QR code generator failed: {result}")
                raise Exception(f"Direct QR code generator failed: {result}")

            print(f"QR code generated at {output_path}")

        except Exception as e:
            print(f"Error generating QR code: {str(e)}")
            return jsonify({
                "status": "error",
                "message": f"QR code generation failed: {str(e)}"
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

        # Add cache buster to avoid browser caching
        import random
        qr_code_url_with_cache_buster = f"{qr_code_url}?v={random.randint(1000, 9999)}"
        print(f"QR code URL: {qr_code_url_with_cache_buster}")

        return jsonify({
            "status": "success",
            "message": "QR code generated successfully",
            "qr_code_url": qr_code_url_with_cache_buster,
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

@bp.route('/settings/edit', methods=['POST'])
@admin_required
def edit_standard_value():
    """Edit an existing standard value."""
    from app import standard_values_manager

    # Get form data
    value_type = request.form.get('value_type')
    old_value = request.form.get('old_value')
    new_value = request.form.get('new_value')
    category = request.form.get('category', '')

    if not value_type or not old_value or not new_value:
        return redirect(url_for('admin.settings', message='Missing required fields', type='danger'))

    # Don't allow empty values
    if not new_value.strip():
        return redirect(url_for('admin.settings', message='New value cannot be empty', type='danger'))

    result = False

    # Edit the value based on type
    if value_type == 'category':
        result = standard_values_manager.edit_category(old_value, new_value)
    elif value_type == 'equipment_type':
        if not category:
            return redirect(url_for('admin.settings', message='Category is required for equipment types', type='danger'))
        result = standard_values_manager.edit_equipment_type(category, old_value, new_value)
    elif value_type == 'manufacturer':
        result = standard_values_manager.edit_manufacturer(old_value, new_value)
    elif value_type == 'location':
        result = standard_values_manager.edit_location(old_value, new_value)

    if result:
        return redirect(url_for('admin.settings', message=f'{value_type.title()} "{old_value}" updated to "{new_value}" successfully', type='success'))
    else:
        return redirect(url_for('admin.settings', message=f'Failed to update {value_type} - the new value may already exist', type='danger'))

@bp.route('/calendar')
@physicist_required
def calendar():
    """Calendar view for equipment deadlines and checkouts. Accessible to both admins and physicists."""
    return render_template('admin/calendar.html')

@bp.route('/calendar/test')
def calendar_test():
    """Test page for calendar functionality."""
    return render_template('admin/calendar_test.html')

@bp.route('/calendar/events')
@physicist_required
def calendar_events():
    """API endpoint to get calendar events for equipment deadlines and checkouts. Accessible to both admins and physicists."""
    from app import equipment_manager, checkout_manager
    from datetime import datetime, timedelta
    import re
    from flask import jsonify, Response

    # Get all equipment
    all_equipment = equipment_manager.get_all_equipment()

    # Parse dates
    today = datetime.now()

    # List for calendar events
    calendar_events = []

    # Process calibration deadlines
    for equipment in all_equipment:
        try:
            # Skip equipment without calibration dates
            if not equipment.get('calibration_due_date'):
                continue

            # Parse calibration date (format can be MM/YYYY or MM-YYYY)
            calibration_str = equipment['calibration_due_date']

            # If format is MM/YYYY or MM-YYYY, convert to a date
            if re.match(r'^\d{1,2}[/\-]\d{4}$', calibration_str):
                month, year = re.split(r'[/\-]', calibration_str)
                # Set due date to last day of the month
                month = int(month)
                year = int(year)

                # Get last day of month
                if month == 12:
                    next_month = 1
                    next_year = year + 1
                else:
                    next_month = month + 1
                    next_year = year

                last_day = (datetime(next_year, next_month, 1) - timedelta(days=1)).day
                calibration_date = datetime(year, month, last_day)
            else:
                # Try other formats
                try:
                    # Try MM/DD/YYYY format
                    calibration_date = datetime.strptime(calibration_str, '%m/%d/%Y')
                except:
                    try:
                        # Try YYYY-MM-DD format
                        calibration_date = datetime.strptime(calibration_str, '%Y-%m-%d')
                    except:
                        # Skip this equipment if we can't parse the date
                        print(f"Could not parse calibration date: {calibration_str} for equipment {equipment['id']}")
                        continue

            # Calculate days until calibration
            days_until_calibration = (calibration_date - today).days

            # Determine event class based on days until calibration
            if days_until_calibration < 0:
                event_class = 'event-calibration-overdue'
                status = 'Overdue'
            elif days_until_calibration < 60:
                event_class = 'event-calibration-soon'
                status = 'Due Soon'
            else:
                event_class = 'event-calibration-upcoming'
                status = 'Upcoming'

            # Create calibration event
            calendar_events.append({
                'id': f"cal-{equipment['id']}",
                'title': f"{equipment['manufacturer']} {equipment['model']} - Calibration Due",
                'start': calibration_date.strftime('%Y-%m-%d'),
                'className': event_class,
                'extendedProps': {
                    'equipmentId': equipment['id'],
                    'eventType': 'calibration',
                    'manufacturer': equipment['manufacturer'],
                    'model': equipment['model'],
                    'serialNumber': equipment['serial_number'],
                    'category': equipment['category'],
                    'status': status,
                    'notes': f"Calibration due in {days_until_calibration} days" if days_until_calibration >= 0 else f"Calibration overdue by {abs(days_until_calibration)} days"
                }
            })
        except Exception as e:
            print(f"Error processing calibration for equipment {equipment.get('id', 'unknown')}: {str(e)}")

    # Process checkouts and expected returns
    try:
        equipment_status = checkout_manager.get_all_status()

        for equipment_id, status in equipment_status.items():
            # Skip if not checked out
            if status.get('status') != 'Checked Out':
                continue

            # Find equipment details
            equipment_details = next((e for e in all_equipment if e['id'] == equipment_id), None)
            if not equipment_details:
                continue

            # Process checkout date
            checkout_time = status.get('checked_out_time')
            if checkout_time:
                try:
                    # Parse checkout date
                    checkout_date = datetime.fromisoformat(checkout_time)

                    # Add checkout event
                    calendar_events.append({
                        'id': f"co-{equipment_id}",
                        'title': f"{equipment_details['manufacturer']} {equipment_details['model']} - Checked Out",
                        'start': checkout_date.strftime('%Y-%m-%d'),
                        'className': 'event-checkout',
                        'extendedProps': {
                            'equipmentId': equipment_id,
                            'eventType': 'checkout',
                            'manufacturer': equipment_details['manufacturer'],
                            'model': equipment_details['model'],
                            'serialNumber': equipment_details['serial_number'],
                            'category': equipment_details['category'],
                            'status': 'Checked Out',
                            'user': status.get('checked_out_by', 'Unknown'),
                            'notes': status.get('notes', '')
                        }
                    })
                except Exception as e:
                    print(f"Error processing checkout date for equipment {equipment_id}: {str(e)}")

            # Process expected return date
            expected_return = status.get('expected_return')
            if expected_return:
                try:
                    # Parse return date
                    return_date = datetime.fromisoformat(expected_return)

                    # Add return event
                    calendar_events.append({
                        'id': f"ret-{equipment_id}",
                        'title': f"{equipment_details['manufacturer']} {equipment_details['model']} - Expected Return",
                        'start': return_date.strftime('%Y-%m-%d'),
                        'className': 'event-expected-return',
                        'extendedProps': {
                            'equipmentId': equipment_id,
                            'eventType': 'return',
                            'manufacturer': equipment_details['manufacturer'],
                            'model': equipment_details['model'],
                            'serialNumber': equipment_details['serial_number'],
                            'category': equipment_details['category'],
                            'status': 'Expected Return',
                            'user': status.get('checked_out_by', 'Unknown'),
                            'notes': status.get('notes', '')
                        }
                    })
                except Exception as e:
                    print(f"Error processing return date for equipment {equipment_id}: {str(e)}")
    except Exception as e:
        print(f"Error processing checkouts: {str(e)}")

    # Serialize the data to JSON manually to handle any datetime objects
    try:
        # Use the flask jsonify function with default handler for datetime objects
        return jsonify(calendar_events)
    except TypeError as e:
        # If there's a serialization error, manually convert datetime objects to strings
        print(f"Error serializing calendar events: {str(e)}")

        def handle_non_serializable(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            raise TypeError(f"Type {type(obj)} not serializable")

        import json
        return Response(
            json.dumps(calendar_events, default=handle_non_serializable),
            mimetype='application/json'
        )

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
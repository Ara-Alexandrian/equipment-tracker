"""
Report generation routes for equipment tracker
"""
from flask import Blueprint, render_template, request, send_file, jsonify, session
from app import equipment_manager, checkout_manager
import io
import csv
import datetime
import functools
import json
from datetime import datetime, timedelta

bp = Blueprint('reports', __name__, url_prefix='/reports')

def physicist_required(view):
    """View decorator that requires the user to be a physicist or administrator."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user' not in session:
            return jsonify({"error": "Authentication required"}), 401
        
        if session['user'].get('role') not in ['admin', 'physicist']:
            return jsonify({"error": "Insufficient permissions"}), 403
        
        return view(**kwargs)
    return wrapped_view

@bp.route('/')
@physicist_required
def index():
    """Report generation page."""
    return render_template('reports/index.html')

@bp.route('/generate', methods=['POST'])
@physicist_required
def generate_report():
    """Generate a report based on user specifications."""
    # Get report parameters
    report_type = request.form.get('report_type', 'inventory')
    report_format = request.form.get('report_format', 'pdf')
    date_range = request.form.get('date_range', 'all')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')
    include_fields = request.form.getlist('include_fields')
    
    # Get the current date and time for the report filename
    current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    # Parse date range
    start = None
    end = datetime.now()
    
    if date_range == 'custom' and start_date and end_date:
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d')
            end = datetime.strptime(end_date, '%Y-%m-%d')
        except:
            # Invalid date format, use defaults
            pass
    elif date_range == 'week':
        start = end - timedelta(days=7)
    elif date_range == 'month':
        start = end - timedelta(days=30)
    elif date_range == 'year':
        start = end - timedelta(days=365)
    
    # Generate report content based on report type
    if report_type == 'inventory':
        data = generate_inventory_report(include_fields)
        filename = f"inventory_report_{current_datetime}"
    elif report_type == 'checkout':
        data = generate_checkout_report(start, end, include_fields)
        filename = f"checkout_report_{current_datetime}"
    elif report_type == 'calibration':
        data = generate_calibration_report(include_fields)
        filename = f"calibration_report_{current_datetime}"
    elif report_type == 'maintenance':
        data = generate_maintenance_report(start, end, include_fields)
        filename = f"maintenance_report_{current_datetime}"
    else:
        return jsonify({"error": "Invalid report type"}), 400
    
    # Generate appropriate file format
    if report_format == 'pdf':
        # TODO: Implement actual PDF generation with a library like ReportLab or WeasyPrint
        # For now, we'll return HTML that could be converted to PDF
        html = render_template(
            'reports/pdf_template.html',
            report_type=report_type,
            date_range_text=get_date_range_text(date_range, start, end),
            data=data,
            current_datetime=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        return jsonify({
            "status": "success",
            "html": html,
            "message": "PDF report generation is simulated for demonstration. In a production environment, this would generate and download a PDF file."
        })
    
    elif report_format == 'excel':
        # For simplicity, we'll actually return CSV data
        csv_data = generate_csv_data(data)
        output = io.StringIO()
        csv_writer = csv.writer(output)
        
        # Write headers
        csv_writer.writerow(csv_data['headers'])
        
        # Write data rows
        for row in csv_data['rows']:
            csv_writer.writerow(row)
        
        return jsonify({
            "status": "success",
            "csv": output.getvalue(),
            "filename": f"{filename}.csv",
            "message": "Excel report generation is simulated for demonstration. In a production environment, this would generate and download an Excel file."
        })
    
    elif report_format == 'csv':
        csv_data = generate_csv_data(data)
        output = io.StringIO()
        csv_writer = csv.writer(output)
        
        # Write headers
        csv_writer.writerow(csv_data['headers'])
        
        # Write data rows
        for row in csv_data['rows']:
            csv_writer.writerow(row)
        
        return jsonify({
            "status": "success",
            "csv": output.getvalue(),
            "filename": f"{filename}.csv"
        })
    
    else:
        return jsonify({"error": "Invalid report format"}), 400

def get_date_range_text(date_range, start_date, end_date):
    """Get a text description of the date range."""
    if date_range == 'all':
        return "All Time"
    elif date_range == 'custom' and start_date and end_date:
        return f"Custom Range: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
    elif date_range == 'week':
        return "Past Week"
    elif date_range == 'month':
        return "Past Month"
    elif date_range == 'year':
        return "Past Year"
    else:
        return "Unknown Date Range"

def generate_inventory_report(include_fields):
    """Generate an inventory report with all equipment."""
    # Get all equipment
    equipment_list = equipment_manager.get_all_equipment()
    
    # Add status information
    for item in equipment_list:
        status = checkout_manager.get_equipment_status(item.get('id'))
        item['status'] = status.get('status', 'Unknown')
        item['current_location'] = status.get('location', 'Unknown')
    
    # Group by category
    grouped_data = {}
    for item in equipment_list:
        category = item.get('category', 'Unknown')
        if category not in grouped_data:
            grouped_data[category] = []
        grouped_data[category].append(item)
    
    # Count by status
    status_counts = {}
    for status in checkout_manager.STATUS_OPTIONS:
        status_counts[status] = len([item for item in equipment_list if item.get('status') == status])
    
    return {
        'title': 'Equipment Inventory Report',
        'equipment': equipment_list,
        'grouped_data': grouped_data,
        'status_counts': status_counts,
        'include_fields': include_fields,
        'total_count': len(equipment_list)
    }

def generate_checkout_report(start_date, end_date, include_fields):
    """Generate a checkout status and history report."""
    # Get currently checked out equipment
    checked_out = checkout_manager.get_checked_out_equipment()
    
    # Get overdue equipment
    overdue = checkout_manager.get_overdue_equipment()
    
    # Get checkout history
    history = checkout_manager.get_checkout_history()
    
    # Filter history by date range if specified
    if start_date and end_date:
        filtered_history = []
        for entry in history:
            try:
                entry_date = datetime.fromisoformat(entry.get('timestamp', '').split('T')[0])
                if start_date <= entry_date <= end_date:
                    filtered_history.append(entry)
            except:
                pass
        history = filtered_history
    
    return {
        'title': 'Equipment Checkout Report',
        'checked_out': checked_out,
        'overdue': overdue,
        'history': history,
        'include_fields': include_fields,
        'current_checkout_count': len(checked_out),
        'overdue_count': len(overdue)
    }

def generate_calibration_report(include_fields):
    """Generate a calibration status report."""
    # Get all equipment
    equipment_list = equipment_manager.get_all_equipment()
    
    # Get equipment with calibration due soon
    due_soon = equipment_manager.get_calibration_due_soon()
    
    # Organize by calibration status
    calibration_status = {
        'current': [],
        'due_soon': [],
        'overdue': [],
        'unknown': []
    }
    
    for item in equipment_list:
        cal_date = item.get('calibration_due_date')
        
        if not cal_date:
            calibration_status['unknown'].append(item)
        elif 'overdue' in str(cal_date).lower():
            calibration_status['overdue'].append(item)
        elif 'due soon' in str(cal_date).lower() or item.get('id') in [d.get('id') for d in due_soon]:
            calibration_status['due_soon'].append(item)
        else:
            calibration_status['current'].append(item)
    
    return {
        'title': 'Equipment Calibration Report',
        'equipment': equipment_list,
        'calibration_status': calibration_status,
        'include_fields': include_fields,
        'due_soon_count': len(calibration_status['due_soon']),
        'overdue_count': len(calibration_status['overdue'])
    }

def generate_maintenance_report(start_date, end_date, include_fields):
    """Generate a maintenance history report."""
    # Placeholder for maintenance data
    # In a real implementation, you would retrieve this from a database
    maintenance_records = []
    
    # Sample maintenance records for demonstration
    sample_records = [
        {
            'id': '1',
            'equipment_id': 'Chamber-CNMC-123',
            'date': '2025-03-15',
            'maintenance_type': 'Repair',
            'description': 'Replaced damaged cable',
            'technician': 'John Smith',
            'cost': 250.00
        },
        {
            'id': '2',
            'equipment_id': 'Electrometer-Keithley-456',
            'date': '2025-02-28',
            'maintenance_type': 'Calibration',
            'description': 'Annual calibration',
            'technician': 'Jane Doe',
            'cost': 500.00
        },
        {
            'id': '3',
            'equipment_id': 'Survey Meter-Ludlum-789',
            'date': '2025-01-10',
            'maintenance_type': 'Inspection',
            'description': 'Routine inspection and battery replacement',
            'technician': 'John Smith',
            'cost': 120.00
        }
    ]
    
    # Filter by date range
    if start_date and end_date:
        for record in sample_records:
            try:
                record_date = datetime.strptime(record['date'], '%Y-%m-%d')
                if start_date <= record_date <= end_date:
                    maintenance_records.append(record)
            except:
                maintenance_records.append(record)
    else:
        maintenance_records = sample_records
    
    # Group by equipment
    grouped_records = {}
    for record in maintenance_records:
        equipment_id = record['equipment_id']
        if equipment_id not in grouped_records:
            grouped_records[equipment_id] = []
        grouped_records[equipment_id].append(record)
    
    # Get costs
    total_cost = sum(record.get('cost', 0) for record in maintenance_records)
    cost_by_type = {}
    for record in maintenance_records:
        maint_type = record.get('maintenance_type', 'Unknown')
        if maint_type not in cost_by_type:
            cost_by_type[maint_type] = 0
        cost_by_type[maint_type] += record.get('cost', 0)
    
    return {
        'title': 'Equipment Maintenance Report',
        'maintenance_records': maintenance_records,
        'grouped_records': grouped_records,
        'include_fields': include_fields,
        'total_count': len(maintenance_records),
        'total_cost': total_cost,
        'cost_by_type': cost_by_type
    }

def generate_csv_data(data):
    """Convert report data to CSV format."""
    headers = []
    rows = []
    
    # Process different report types
    if 'title' in data and 'Equipment Inventory Report' in data['title']:
        # Inventory report
        headers = ['ID', 'Category', 'Type', 'Manufacturer', 'Model', 'Serial Number', 
                'Location', 'Status', 'Calibration Due Date']
        
        for item in data['equipment']:
            row = [
                item.get('id', ''),
                item.get('category', ''),
                item.get('equipment_type', ''),
                item.get('manufacturer', ''),
                item.get('model', ''),
                item.get('serial_number', ''),
                item.get('current_location', ''),
                item.get('status', ''),
                item.get('calibration_due_date', '')
            ]
            rows.append(row)
    
    elif 'title' in data and 'Equipment Checkout Report' in data['title']:
        # Checkout report
        headers = ['ID', 'Status', 'Current Location', 'Checked Out By', 
                'Checkout Time', 'Expected Return', 'Days Overdue', 'Notes']
        
        # Add currently checked out equipment
        for item in data['checked_out']:
            row = [
                item.get('id', ''),
                item.get('status', ''),
                item.get('location', ''),
                item.get('checked_out_by', ''),
                item.get('checked_out_time', ''),
                item.get('expected_return', ''),
                '',
                item.get('notes', '')
            ]
            rows.append(row)
        
        # Add overdue equipment
        for item in data['overdue']:
            row = [
                item.get('id', ''),
                item.get('status', ''),
                item.get('location', ''),
                item.get('checked_out_by', ''),
                item.get('checked_out_time', ''),
                item.get('expected_return', ''),
                item.get('days_overdue', ''),
                item.get('notes', '')
            ]
            rows.append(row)
    
    elif 'title' in data and 'Equipment Calibration Report' in data['title']:
        # Calibration report
        headers = ['ID', 'Category', 'Manufacturer', 'Model', 'Serial Number', 
                'Calibration Due Date', 'Status']
        
        # Add overdue calibrations
        for item in data['calibration_status']['overdue']:
            row = [
                item.get('id', ''),
                item.get('category', ''),
                item.get('manufacturer', ''),
                item.get('model', ''),
                item.get('serial_number', ''),
                item.get('calibration_due_date', ''),
                'Overdue'
            ]
            rows.append(row)
        
        # Add due soon calibrations
        for item in data['calibration_status']['due_soon']:
            row = [
                item.get('id', ''),
                item.get('category', ''),
                item.get('manufacturer', ''),
                item.get('model', ''),
                item.get('serial_number', ''),
                item.get('calibration_due_date', ''),
                'Due Soon'
            ]
            rows.append(row)
        
        # Add current calibrations
        for item in data['calibration_status']['current']:
            row = [
                item.get('id', ''),
                item.get('category', ''),
                item.get('manufacturer', ''),
                item.get('model', ''),
                item.get('serial_number', ''),
                item.get('calibration_due_date', ''),
                'Current'
            ]
            rows.append(row)
    
    elif 'title' in data and 'Equipment Maintenance Report' in data['title']:
        # Maintenance report
        headers = ['Equipment ID', 'Date', 'Maintenance Type', 'Description', 
                'Technician', 'Cost']
        
        for record in data['maintenance_records']:
            row = [
                record.get('equipment_id', ''),
                record.get('date', ''),
                record.get('maintenance_type', ''),
                record.get('description', ''),
                record.get('technician', ''),
                record.get('cost', '')
            ]
            rows.append(row)
    
    return {
        'headers': headers,
        'rows': rows
    }
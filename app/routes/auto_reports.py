"""
Automatic report generation routes
"""
from flask import Blueprint, render_template, request, jsonify, send_file, abort
from app import equipment_manager, checkout_manager
from app.models.auto_reports import auto_report_manager
import os
import json
import datetime
import functools

bp = Blueprint('auto_reports', __name__, url_prefix='/admin/auto-reports')

def admin_required(view):
    """View decorator that requires the user to be an administrator."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        # Check if user is in session
        from flask import session
        if 'user' not in session:
            return jsonify({"error": "Authentication required"}), 401
        
        # Check if user is an admin
        if session['user'].get('role') != 'admin':
            return jsonify({"error": "Admin privileges required"}), 403
        
        return view(**kwargs)
    return wrapped_view

@bp.route('/')
@admin_required
def index():
    """Render the automatic reports configuration page."""
    # Get configuration
    config = auto_report_manager.config
    
    # Get scheduler status
    is_running = auto_report_manager.is_running
    
    # Calculate next scheduled runs
    next_daily = None
    next_weekly = None
    next_monthly = None
    
    # Get generated reports
    reports = []
    if config['storage']['enabled']:
        storage_path = config['storage']['path']
        if os.path.exists(storage_path):
            for root, dirs, files in os.walk(storage_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_stats = os.stat(file_path)
                    file_size = file_stats.st_size
                    file_date = datetime.datetime.fromtimestamp(file_stats.st_mtime)
                    
                    # Determine report type and format
                    report_type = "Unknown"
                    if "inventory" in file:
                        report_type = "Inventory"
                    elif "checkout" in file:
                        report_type = "Checkout"
                    elif "calibration" in file:
                        report_type = "Calibration"
                    elif "maintenance" in file:
                        report_type = "Maintenance"
                    
                    report_format = file.split('.')[-1].upper()
                    
                    reports.append({
                        "name": file,
                        "path": file_path,
                        "type": report_type,
                        "format": report_format,
                        "generated": file_date.strftime("%Y-%m-%d %H:%M:%S"),
                        "size": f"{file_size / 1024:.1f} KB" if file_size < 1024 * 1024 else f"{file_size / (1024 * 1024):.1f} MB"
                    })
    
    # Sort reports by date (newest first)
    reports.sort(key=lambda x: x["generated"], reverse=True)
    
    # Calculate storage statistics
    report_count = len(reports)
    storage_size = sum(os.path.getsize(report["path"]) for report in reports)
    storage_size_text = f"{storage_size / 1024:.1f} KB" if storage_size < 1024 * 1024 else f"{storage_size / (1024 * 1024):.1f} MB"
    
    oldest_report = None
    if reports:
        oldest_report_date = min(datetime.datetime.strptime(report["generated"], "%Y-%m-%d %H:%M:%S") for report in reports)
        oldest_report = oldest_report_date.strftime("%Y-%m-%d")
    
    return render_template('admin/auto_reports.html',
                          config=config,
                          is_running=is_running,
                          next_daily=next_daily,
                          next_weekly=next_weekly,
                          next_monthly=next_monthly,
                          reports=reports,
                          report_count=report_count,
                          storage_size=storage_size_text,
                          oldest_report=oldest_report)

@bp.route('/save-schedules', methods=['POST'])
@admin_required
def save_schedules():
    """Save schedule settings."""
    try:
        data = request.json
        
        # Update configuration
        auto_report_manager.config['schedules'] = data['schedules']
        
        # Save configuration
        auto_report_manager.save_config()
        
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})

@bp.route('/save-email', methods=['POST'])
@admin_required
def save_email():
    """Save email settings."""
    try:
        data = request.json
        
        # Update configuration
        auto_report_manager.config['email'] = data['email']
        
        # Save configuration
        auto_report_manager.save_config()
        
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})

@bp.route('/save-storage', methods=['POST'])
@admin_required
def save_storage():
    """Save storage settings."""
    try:
        data = request.json
        
        # Update configuration
        auto_report_manager.config['storage'] = data['storage']
        
        # Save configuration
        auto_report_manager.save_config()
        
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})

@bp.route('/start-scheduler', methods=['POST'])
@admin_required
def start_scheduler():
    """Start the automatic report scheduler."""
    try:
        auto_report_manager.start_scheduler()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})

@bp.route('/stop-scheduler', methods=['POST'])
@admin_required
def stop_scheduler():
    """Stop the automatic report scheduler."""
    try:
        auto_report_manager.stop_scheduler()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})

@bp.route('/generate', methods=['POST'])
@admin_required
def generate_report():
    """Generate a report manually."""
    try:
        data = request.json
        report_type = data.get('report_type')
        report_format = data.get('report_format')
        
        # Validate inputs
        if not report_type or not report_format:
            return jsonify({"status": "error", "error": "Report type and format are required"})
        
        # Generate report
        report_file = auto_report_manager.generate_report(
            report_type=report_type,
            report_format=report_format,
            frequency="manual"
        )
        
        if not report_file:
            return jsonify({"status": "error", "error": "Failed to generate report"})
        
        return jsonify({
            "status": "success",
            "report_file": report_file
        })
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})

@bp.route('/list')
@admin_required
def list_reports():
    """List all generated reports."""
    try:
        # Get configuration
        config = auto_report_manager.config
        
        # Get generated reports
        reports = []
        if config['storage']['enabled']:
            storage_path = config['storage']['path']
            if os.path.exists(storage_path):
                for root, dirs, files in os.walk(storage_path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        file_stats = os.stat(file_path)
                        file_size = file_stats.st_size
                        file_date = datetime.datetime.fromtimestamp(file_stats.st_mtime)
                        
                        # Determine report type and format
                        report_type = "Unknown"
                        if "inventory" in file:
                            report_type = "Inventory"
                        elif "checkout" in file:
                            report_type = "Checkout"
                        elif "calibration" in file:
                            report_type = "Calibration"
                        elif "maintenance" in file:
                            report_type = "Maintenance"
                        
                        report_format = file.split('.')[-1].upper()
                        
                        reports.append({
                            "name": file,
                            "path": file_path,
                            "type": report_type,
                            "format": report_format,
                            "generated": file_date.strftime("%Y-%m-%d %H:%M:%S"),
                            "size": f"{file_size / 1024:.1f} KB" if file_size < 1024 * 1024 else f"{file_size / (1024 * 1024):.1f} MB"
                        })
        
        # Sort reports by date (newest first)
        reports.sort(key=lambda x: x["generated"], reverse=True)
        
        return jsonify({
            "status": "success",
            "reports": reports
        })
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})

@bp.route('/download/<path:report_path>')
@admin_required
def download_report(report_path):
    """Download a generated report."""
    try:
        # Validate that the file exists
        if not os.path.exists(report_path):
            abort(404)
        
        # Get filename
        filename = os.path.basename(report_path)
        
        # Send file
        return send_file(report_path, as_attachment=True, download_name=filename)
    except Exception as e:
        abort(500)

@bp.route('/delete', methods=['POST'])
@admin_required
def delete_report():
    """Delete a generated report."""
    try:
        data = request.json
        report_path = data.get('report_path')
        
        # Validate that the file exists
        if not os.path.exists(report_path):
            return jsonify({"status": "error", "error": "Report not found"})
        
        # Delete file
        os.remove(report_path)
        
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})

@bp.route('/cleanup', methods=['POST'])
@admin_required
def cleanup_reports():
    """Clean up old reports based on retention period."""
    try:
        auto_report_manager._clean_old_reports()
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})
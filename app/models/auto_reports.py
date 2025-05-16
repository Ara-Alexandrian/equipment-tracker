"""
Automatic Report Generation System for Equipment Tracker

This module provides functionality for scheduled automatic report generation.
It handles generating, archiving, and distributing reports on a configurable schedule.
"""
import os
import json
import time
import threading
import schedule
from datetime import datetime, timedelta
import io
import csv
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# Import necessary models and utilities
from app.models.json_utils import save_json, load_json, DateTimeEncoder
from app import equipment_manager, checkout_manager
from app.models.ticket import TicketManager
from app.models.transport_request import TransportManager

# Try to import PDF generation library
try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False
    print("WeasyPrint not available. PDF generation will be simulated.")

class AutoReportManager:
    """Manages automatic report generation, scheduling, and distribution."""
    
    DEFAULT_CONFIG = {
        "enabled": True,
        "schedules": {
            "daily": {
                "enabled": True,
                "time": "08:00",
                "reports": ["calibration"],
                "formats": ["pdf"],
                "email_distribution": True
            },
            "weekly": {
                "enabled": True,
                "day": "Monday",
                "time": "09:00",
                "reports": ["inventory", "checkout", "calibration"],
                "formats": ["pdf", "csv"],
                "email_distribution": True
            },
            "monthly": {
                "enabled": True,
                "day": 1,
                "time": "07:00",
                "reports": ["inventory", "checkout", "calibration", "maintenance"],
                "formats": ["pdf", "csv", "excel"],
                "email_distribution": True
            },
            "custom": {
                "enabled": False,
                "cron": "0 12 * * *",  # Example: noon every day
                "reports": ["custom"],
                "formats": ["pdf"],
                "email_distribution": True
            }
        },
        "email": {
            "enabled": True,
            "recipients": {
                "daily": ["physicists"],
                "weekly": ["physicists", "admin"],
                "monthly": ["physicists", "admin", "management"]
            },
            "subject_prefix": "[GearVue] ",
            "body_template": "Attached is the automatically generated {report_type} report for {date_range}."
        },
        "storage": {
            "enabled": True,
            "path": "reports/auto",
            "retention_days": 90,
            "organize_by_type": True
        }
    }
    
    def __init__(self, app=None, data_dir='app/data'):
        """Initialize the auto report manager.
        
        Args:
            app: Flask application instance
            data_dir: Directory for data storage
        """
        self.app = app
        self.data_dir = data_dir
        self.config_file = os.path.join(data_dir, 'auto_reports_config.json')
        self.report_schedule = {}
        self.scheduler_thread = None
        self.is_running = False
        self.ticket_manager = TicketManager()
        self.transport_manager = TransportManager()
        
        # Load or create configuration
        self.config = self._load_or_create_config()
        
        # Create report storage directory if it doesn't exist
        if self.config['storage']['enabled']:
            os.makedirs(self.config['storage']['path'], exist_ok=True)
        
        if app is not None:
            self.init_app(app)
            
    def init_app(self, app):
        """Initialize with Flask application instance."""
        self.app = app
        
        # Register CLI commands if in Flask context
        if hasattr(app, 'cli'):
            self._register_cli_commands()
    
    def _load_or_create_config(self):
        """Load existing config or create default config."""
        if os.path.exists(self.config_file):
            try:
                config = load_json(self.config_file)
                print(f"Loaded auto report configuration from {self.config_file}")
                return config
            except Exception as e:
                print(f"Error loading auto report config: {e}")
                return self.DEFAULT_CONFIG
        else:
            # Create default config
            save_json(self.DEFAULT_CONFIG, self.config_file)
            print(f"Created default auto report configuration at {self.config_file}")
            return self.DEFAULT_CONFIG
    
    def save_config(self):
        """Save current configuration to file."""
        save_json(self.config, self.config_file)
        print(f"Saved auto report configuration to {self.config_file}")
        
        # If running, restart scheduler to apply new configuration
        if self.is_running:
            self.stop_scheduler()
            self.start_scheduler()
    
    def _register_cli_commands(self):
        """Register CLI commands for the Flask application."""
        @self.app.cli.command("generate-report")
        def generate_report_command():
            """Generate reports manually from command line."""
            self.generate_all_reports()
            
        @self.app.cli.command("start-auto-reports")
        def start_auto_reports_command():
            """Start the automatic report scheduler."""
            self.start_scheduler()
            
        @self.app.cli.command("stop-auto-reports")
        def stop_auto_reports_command():
            """Stop the automatic report scheduler."""
            self.stop_scheduler()
    
    def start_scheduler(self):
        """Start the automatic report scheduler."""
        if self.is_running:
            print("Scheduler is already running")
            return
        
        if not self.config['enabled']:
            print("Automatic reporting is disabled in configuration")
            return
        
        # Clear any existing schedule
        schedule.clear()
        
        # Set up daily reports
        if self.config['schedules']['daily']['enabled']:
            schedule.every().day.at(self.config['schedules']['daily']['time']).do(
                self.generate_daily_reports
            )
            print(f"Scheduled daily reports at {self.config['schedules']['daily']['time']}")
        
        # Set up weekly reports
        if self.config['schedules']['weekly']['enabled']:
            day = self.config['schedules']['weekly']['day']
            time = self.config['schedules']['weekly']['time']
            
            if day == "Monday":
                schedule.every().monday.at(time).do(self.generate_weekly_reports)
            elif day == "Tuesday":
                schedule.every().tuesday.at(time).do(self.generate_weekly_reports)
            elif day == "Wednesday":
                schedule.every().wednesday.at(time).do(self.generate_weekly_reports)
            elif day == "Thursday":
                schedule.every().thursday.at(time).do(self.generate_weekly_reports)
            elif day == "Friday":
                schedule.every().friday.at(time).do(self.generate_weekly_reports)
            elif day == "Saturday":
                schedule.every().saturday.at(time).do(self.generate_weekly_reports)
            elif day == "Sunday":
                schedule.every().sunday.at(time).do(self.generate_weekly_reports)
                
            print(f"Scheduled weekly reports on {day} at {time}")
        
        # Set up monthly reports
        if self.config['schedules']['monthly']['enabled']:
            day = self.config['schedules']['monthly']['day']
            time = self.config['schedules']['monthly']['time']
            
            schedule.every().month.at(f"{day:02d} {time}").do(self.generate_monthly_reports)
            print(f"Scheduled monthly reports on day {day} at {time}")
        
        # Start the scheduler in a background thread
        def run_scheduler():
            self.is_running = True
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        
        self.scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        self.scheduler_thread.start()
        print("Automatic report scheduler started")
    
    def stop_scheduler(self):
        """Stop the automatic report scheduler."""
        if not self.is_running:
            print("Scheduler is not running")
            return
        
        self.is_running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=2.0)
            self.scheduler_thread = None
        
        schedule.clear()
        print("Automatic report scheduler stopped")
    
    def generate_daily_reports(self):
        """Generate daily reports according to configuration."""
        print(f"Generating daily reports at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        reports = self.config['schedules']['daily']['reports']
        formats = self.config['schedules']['daily']['formats']
        
        # Set date range for reports (last 24 hours)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=1)
        
        generated_reports = []
        
        for report_type in reports:
            for report_format in formats:
                try:
                    report_file = self.generate_report(
                        report_type=report_type,
                        report_format=report_format,
                        start_date=start_date,
                        end_date=end_date,
                        frequency="daily"
                    )
                    if report_file:
                        generated_reports.append(report_file)
                except Exception as e:
                    print(f"Error generating daily {report_type} report in {report_format} format: {e}")
        
        # Send email with reports if configured
        if self.config['schedules']['daily']['email_distribution'] and generated_reports:
            self._send_report_emails(generated_reports, "daily")
            
        return f"Generated {len(generated_reports)} daily reports"
    
    def generate_weekly_reports(self):
        """Generate weekly reports according to configuration."""
        print(f"Generating weekly reports at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        reports = self.config['schedules']['weekly']['reports']
        formats = self.config['schedules']['weekly']['formats']
        
        # Set date range for reports (last 7 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        generated_reports = []
        
        for report_type in reports:
            for report_format in formats:
                try:
                    report_file = self.generate_report(
                        report_type=report_type,
                        report_format=report_format,
                        start_date=start_date,
                        end_date=end_date,
                        frequency="weekly"
                    )
                    if report_file:
                        generated_reports.append(report_file)
                except Exception as e:
                    print(f"Error generating weekly {report_type} report in {report_format} format: {e}")
        
        # Send email with reports if configured
        if self.config['schedules']['weekly']['email_distribution'] and generated_reports:
            self._send_report_emails(generated_reports, "weekly")
            
        return f"Generated {len(generated_reports)} weekly reports"
    
    def generate_monthly_reports(self):
        """Generate monthly reports according to configuration."""
        print(f"Generating monthly reports at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        reports = self.config['schedules']['monthly']['reports']
        formats = self.config['schedules']['monthly']['formats']
        
        # Set date range for reports (last 30 days)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        generated_reports = []
        
        for report_type in reports:
            for report_format in formats:
                try:
                    report_file = self.generate_report(
                        report_type=report_type,
                        report_format=report_format,
                        start_date=start_date,
                        end_date=end_date,
                        frequency="monthly"
                    )
                    if report_file:
                        generated_reports.append(report_file)
                except Exception as e:
                    print(f"Error generating monthly {report_type} report in {report_format} format: {e}")
        
        # Send email with reports if configured
        if self.config['schedules']['monthly']['email_distribution'] and generated_reports:
            self._send_report_emails(generated_reports, "monthly")
            
        # Clean up old reports
        self._clean_old_reports()
            
        return f"Generated {len(generated_reports)} monthly reports"
    
    def generate_all_reports(self):
        """Generate all configured reports for all frequencies."""
        print(f"Generating all reports at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        self.generate_daily_reports()
        self.generate_weekly_reports()
        self.generate_monthly_reports()
    
    def generate_report(self, report_type, report_format, start_date=None, end_date=None, frequency="daily"):
        """Generate a single report and save it to the configured storage location.
        
        Args:
            report_type: Type of report (inventory, checkout, calibration, maintenance)
            report_format: Format of report (pdf, csv, excel)
            start_date: Start date for report data
            end_date: End date for report data
            frequency: Frequency for file naming (daily, weekly, monthly)
            
        Returns:
            Path to the generated report file, or None if generation failed
        """
        if not self.config['storage']['enabled']:
            print("Report storage is disabled in configuration")
            return None
        
        # Create timestamp for filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Set up directory path
        base_path = self.config['storage']['path']
        if self.config['storage']['organize_by_type']:
            report_path = os.path.join(base_path, report_type)
        else:
            report_path = base_path
        
        # Create directory if it doesn't exist
        os.makedirs(report_path, exist_ok=True)
        
        # Generate filename
        filename = f"{report_type}_{frequency}_{timestamp}.{report_format}"
        file_path = os.path.join(report_path, filename)
        
        # Generate report data
        if report_type == 'inventory':
            report_data = self._generate_inventory_report_data()
        elif report_type == 'checkout':
            report_data = self._generate_checkout_report_data(start_date, end_date)
        elif report_type == 'calibration':
            report_data = self._generate_calibration_report_data()
        elif report_type == 'maintenance':
            report_data = self._generate_maintenance_report_data(start_date, end_date)
        else:
            print(f"Unknown report type: {report_type}")
            return None
        
        # Generate the actual report file
        if report_format == 'pdf':
            success = self._generate_pdf_report(file_path, report_type, report_data, start_date, end_date)
        elif report_format == 'csv':
            success = self._generate_csv_report(file_path, report_type, report_data)
        elif report_format == 'excel':
            success = self._generate_excel_report(file_path, report_type, report_data)
        else:
            print(f"Unknown report format: {report_format}")
            return None
        
        if success:
            print(f"Generated {report_type} report in {report_format} format: {file_path}")
            return file_path
        else:
            print(f"Failed to generate {report_type} report in {report_format} format")
            return None
    
    def _generate_inventory_report_data(self):
        """Generate data for inventory report."""
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
            'total_count': len(equipment_list)
        }
    
    def _generate_checkout_report_data(self, start_date, end_date):
        """Generate data for checkout report."""
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
                    timestamp = entry.get('timestamp', '')
                    if timestamp:
                        # Handle ISO format strings
                        if isinstance(timestamp, str):
                            if 'T' in timestamp:
                                entry_date = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            else:
                                # Try to parse date
                                entry_date = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                        else:
                            entry_date = timestamp
                        
                        if start_date <= entry_date <= end_date:
                            filtered_history.append(entry)
                except Exception as e:
                    print(f"Error parsing timestamp: {e}")
            
            history = filtered_history
        
        return {
            'title': 'Equipment Checkout Report',
            'checked_out': checked_out,
            'overdue': overdue,
            'history': history,
            'current_checkout_count': len(checked_out),
            'overdue_count': len(overdue)
        }
    
    def _generate_calibration_report_data(self):
        """Generate data for calibration report."""
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
            'due_soon_count': len(calibration_status['due_soon']),
            'overdue_count': len(calibration_status['overdue'])
        }
    
    def _generate_maintenance_report_data(self, start_date, end_date):
        """Generate data for maintenance report."""
        # Get tickets related to maintenance from the ticket manager
        tickets = self.ticket_manager.get_tickets_by_type('maintenance')
        
        # Filter tickets by date range if specified
        if start_date and end_date:
            filtered_tickets = []
            for ticket in tickets:
                created_at = ticket.get('created_at')
                if created_at:
                    if isinstance(created_at, str):
                        if 'T' in created_at:
                            ticket_date = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
                        else:
                            # Try to parse date
                            ticket_date = datetime.strptime(created_at, '%Y-%m-%d %H:%M:%S')
                    else:
                        ticket_date = created_at
                    
                    if start_date <= ticket_date <= end_date:
                        filtered_tickets.append(ticket)
            
            tickets = filtered_tickets
        
        # Convert tickets to maintenance records format
        maintenance_records = []
        for ticket in tickets:
            record = {
                'id': ticket.get('id'),
                'equipment_id': ticket.get('equipment_id'),
                'date': ticket.get('created_at'),
                'maintenance_type': 'Maintenance',
                'description': ticket.get('description'),
                'technician': ticket.get('assigned_to', 'Unassigned'),
                'cost': 0.00  # Placeholder - no cost tracking in tickets
            }
            maintenance_records.append(record)
        
        # Group by equipment
        grouped_records = {}
        for record in maintenance_records:
            equipment_id = record['equipment_id']
            if equipment_id not in grouped_records:
                grouped_records[equipment_id] = []
            grouped_records[equipment_id].append(record)
        
        return {
            'title': 'Equipment Maintenance Report',
            'maintenance_records': maintenance_records,
            'grouped_records': grouped_records,
            'total_count': len(maintenance_records)
        }
    
    def _generate_pdf_report(self, file_path, report_type, report_data, start_date, end_date):
        """Generate a PDF report and save it to the specified path."""
        if not WEASYPRINT_AVAILABLE:
            # Create a simple PDF if WeasyPrint is not available
            try:
                with open(file_path, 'wb') as f:
                    f.write(b'%PDF-1.4\n1 0 obj\n<</Type /Catalog/Pages 2 0 R>>\nendobj\n2 0 obj\n<</Type /Pages/Kids [3 0 R]/Count 1>>\nendobj\n3 0 obj\n<</Type /Page/Parent 2 0 R/Resources 4 0 R/MediaBox [0 0 612 792]/Contents 5 0 R>>\nendobj\n4 0 obj\n<</Font <</F1 6 0 R>>>>\nendobj\n5 0 obj\n<</Length 108>>\nstream\nBT\n/F1 24 Tf\n50 700 Td\n(Equipment Report) Tj\n/F1 12 Tf\n0 -40 Td\n(This is a simulated PDF report) Tj\nET\nendstream\nendobj\n6 0 obj\n<</Type /Font/Subtype /Type1/BaseFont /Helvetica>>\nendobj\nxref\n0 7\n0000000000 65535 f\n0000000009 00000 n\n0000000056 00000 n\n0000000111 00000 n\n0000000212 00000 n\n0000000253 00000 n\n0000000413 00000 n\ntrailer\n<</Size 7/Root 1 0 R>>\nstartxref\n483\n%%EOF')
                return True
            except Exception as e:
                print(f"Error creating simulated PDF: {e}")
                return False
        
        try:
            # Generate HTML content first
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>{report_data['title']}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 20px; }}
                    h1 {{ color: #333366; }}
                    h2 {{ color: #666699; margin-top: 20px; }}
                    table {{ border-collapse: collapse; width: 100%; margin-top: 10px; }}
                    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                    th {{ background-color: #f2f2f2; }}
                    .summary {{ background-color: #f9f9f9; padding: 10px; margin: 10px 0; }}
                    .header {{ border-bottom: 1px solid #ddd; padding-bottom: 10px; margin-bottom: 20px; }}
                    .footer {{ margin-top: 30px; font-size: 0.8em; color: #666; text-align: center; }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>{report_data['title']}</h1>
                    <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                    <p>Date Range: {start_date.strftime('%Y-%m-%d') if start_date else 'All'} to {end_date.strftime('%Y-%m-%d') if end_date else 'Present'}</p>
                </div>
            """
            
            # Add report-specific content
            if report_type == 'inventory':
                html_content += self._generate_inventory_html(report_data)
            elif report_type == 'checkout':
                html_content += self._generate_checkout_html(report_data)
            elif report_type == 'calibration':
                html_content += self._generate_calibration_html(report_data)
            elif report_type == 'maintenance':
                html_content += self._generate_maintenance_html(report_data)
            
            # Add footer
            html_content += """
                <div class="footer">
                    <p>Generated by GearVue Equipment Tracker</p>
                </div>
            </body>
            </html>
            """
            
            # Generate PDF using WeasyPrint
            HTML(string=html_content).write_pdf(file_path)
            return os.path.exists(file_path)
            
        except Exception as e:
            print(f"Error generating PDF report: {e}")
            return False
    
    def _generate_csv_report(self, file_path, report_type, report_data):
        """Generate a CSV report and save it to the specified path."""
        try:
            with open(file_path, 'w', newline='') as csvfile:
                csv_writer = csv.writer(csvfile)
                
                if report_type == 'inventory':
                    # Write header
                    csv_writer.writerow(['ID', 'Category', 'Type', 'Manufacturer', 'Model', 
                                       'Serial Number', 'Location', 'Status', 'Calibration Due Date'])
                    
                    # Write data
                    for item in report_data['equipment']:
                        csv_writer.writerow([
                            item.get('id', ''),
                            item.get('category', ''),
                            item.get('equipment_type', ''),
                            item.get('manufacturer', ''),
                            item.get('model', ''),
                            item.get('serial_number', ''),
                            item.get('current_location', ''),
                            item.get('status', ''),
                            item.get('calibration_due_date', '')
                        ])
                
                elif report_type == 'checkout':
                    # Write header
                    csv_writer.writerow(['ID', 'Status', 'Current Location', 'Checked Out By', 
                                       'Checkout Time', 'Expected Return', 'Days Overdue', 'Notes'])
                    
                    # Write currently checked out equipment
                    for item in report_data['checked_out']:
                        csv_writer.writerow([
                            item.get('id', ''),
                            item.get('status', ''),
                            item.get('location', ''),
                            item.get('checked_out_by', ''),
                            item.get('checked_out_time', ''),
                            item.get('expected_return', ''),
                            item.get('days_overdue', ''),
                            item.get('notes', '')
                        ])
                
                elif report_type == 'calibration':
                    # Write header
                    csv_writer.writerow(['ID', 'Category', 'Manufacturer', 'Model', 
                                       'Serial Number', 'Calibration Due Date', 'Status'])
                    
                    # Write overdue calibrations
                    for item in report_data['calibration_status']['overdue']:
                        csv_writer.writerow([
                            item.get('id', ''),
                            item.get('category', ''),
                            item.get('manufacturer', ''),
                            item.get('model', ''),
                            item.get('serial_number', ''),
                            item.get('calibration_due_date', ''),
                            'Overdue'
                        ])
                    
                    # Write due soon calibrations
                    for item in report_data['calibration_status']['due_soon']:
                        csv_writer.writerow([
                            item.get('id', ''),
                            item.get('category', ''),
                            item.get('manufacturer', ''),
                            item.get('model', ''),
                            item.get('serial_number', ''),
                            item.get('calibration_due_date', ''),
                            'Due Soon'
                        ])
                
                elif report_type == 'maintenance':
                    # Write header
                    csv_writer.writerow(['Equipment ID', 'Date', 'Maintenance Type', 
                                       'Description', 'Technician', 'Cost'])
                    
                    # Write maintenance records
                    for record in report_data['maintenance_records']:
                        csv_writer.writerow([
                            record.get('equipment_id', ''),
                            record.get('date', ''),
                            record.get('maintenance_type', ''),
                            record.get('description', ''),
                            record.get('technician', ''),
                            record.get('cost', '')
                        ])
            
            return os.path.exists(file_path)
            
        except Exception as e:
            print(f"Error generating CSV report: {e}")
            return False
    
    def _generate_excel_report(self, file_path, report_type, report_data):
        """Generate an Excel report and save it to the specified path.
        
        For demonstration, we'll generate a CSV and call it Excel, but in a
        real implementation this would use a library like openpyxl or xlsxwriter.
        """
        return self._generate_csv_report(file_path, report_type, report_data)
    
    def _generate_inventory_html(self, report_data):
        """Generate HTML for inventory report."""
        html = """
            <div class="summary">
                <h2>Summary</h2>
                <p>Total Equipment: {}</p>
                <table>
                    <tr>
                        <th>Category</th>
                        <th>Count</th>
                    </tr>
        """.format(report_data['total_count'])
        
        # Add category counts
        category_counts = {}
        for item in report_data['equipment']:
            category = item.get('category', 'Unknown')
            if category not in category_counts:
                category_counts[category] = 0
            category_counts[category] += 1
        
        for category, count in sorted(category_counts.items()):
            html += f"<tr><td>{category}</td><td>{count}</td></tr>"
        
        html += """
                </table>
                
                <h3>Status Summary</h3>
                <table>
                    <tr>
                        <th>Status</th>
                        <th>Count</th>
                    </tr>
        """
        
        # Add status counts
        for status, count in sorted(report_data['status_counts'].items()):
            html += f"<tr><td>{status}</td><td>{count}</td></tr>"
        
        html += """
                </table>
            </div>
            
            <h2>Equipment Details</h2>
        """
        
        # Add equipment tables by category
        for category, items in sorted(report_data['grouped_data'].items()):
            html += f"""
                <h3>{category}</h3>
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Manufacturer</th>
                        <th>Model</th>
                        <th>Serial Number</th>
                        <th>Location</th>
                        <th>Status</th>
                        <th>Cal Due Date</th>
                    </tr>
            """
            
            for item in items:
                html += f"""
                    <tr>
                        <td>{item.get('id', '')}</td>
                        <td>{item.get('manufacturer', '')}</td>
                        <td>{item.get('model', '')}</td>
                        <td>{item.get('serial_number', '')}</td>
                        <td>{item.get('current_location', '')}</td>
                        <td>{item.get('status', '')}</td>
                        <td>{item.get('calibration_due_date', '')}</td>
                    </tr>
                """
            
            html += "</table>"
        
        return html
    
    def _generate_checkout_html(self, report_data):
        """Generate HTML for checkout report."""
        html = """
            <div class="summary">
                <h2>Summary</h2>
                <p>Current Checkouts: {}</p>
                <p>Overdue: {}</p>
            </div>
            
            <h2>Currently Checked Out Equipment</h2>
            <table>
                <tr>
                    <th>ID</th>
                    <th>Location</th>
                    <th>Checked Out By</th>
                    <th>Checkout Time</th>
                    <th>Expected Return</th>
                    <th>Days Overdue</th>
                </tr>
        """.format(report_data['current_checkout_count'], report_data['overdue_count'])
        
        for item in report_data['checked_out']:
            # Format the checkout time
            checkout_time = item.get('checked_out_time', '')
            if checkout_time:
                try:
                    if isinstance(checkout_time, str):
                        if 'T' in checkout_time:
                            checkout_time = datetime.fromisoformat(checkout_time.replace('Z', '+00:00'))
                            checkout_time = checkout_time.strftime('%Y-%m-%d %H:%M')
                except:
                    pass
            
            # Format the expected return
            expected_return = item.get('expected_return', '')
            if expected_return:
                try:
                    if isinstance(expected_return, str):
                        if 'T' in expected_return:
                            expected_return = datetime.fromisoformat(expected_return.replace('Z', '+00:00'))
                            expected_return = expected_return.strftime('%Y-%m-%d %H:%M')
                except:
                    pass
            
            days_overdue = item.get('days_overdue', '')
            
            html += f"""
                <tr>
                    <td>{item.get('id', '')}</td>
                    <td>{item.get('location', '')}</td>
                    <td>{item.get('checked_out_by', '')}</td>
                    <td>{checkout_time}</td>
                    <td>{expected_return}</td>
                    <td>{days_overdue}</td>
                </tr>
            """
        
        html += """
            </table>
            
            <h2>Checkout History</h2>
            <table>
                <tr>
                    <th>Equipment ID</th>
                    <th>Timestamp</th>
                    <th>Previous Status</th>
                    <th>New Status</th>
                    <th>Previous Location</th>
                    <th>New Location</th>
                    <th>User</th>
                </tr>
        """
        
        for item in report_data['history']:
            html += f"""
                <tr>
                    <td>{item.get('equipment_id', '')}</td>
                    <td>{item.get('timestamp', '')}</td>
                    <td>{item.get('previous_status', '')}</td>
                    <td>{item.get('new_status', '')}</td>
                    <td>{item.get('previous_location', '')}</td>
                    <td>{item.get('new_location', '')}</td>
                    <td>{item.get('user', '')}</td>
                </tr>
            """
        
        html += "</table>"
        
        return html
    
    def _generate_calibration_html(self, report_data):
        """Generate HTML for calibration report."""
        html = """
            <div class="summary">
                <h2>Summary</h2>
                <p>Equipment with Calibration Due Soon: {}</p>
                <p>Equipment with Overdue Calibration: {}</p>
            </div>
            
            <h2>Overdue Calibrations</h2>
        """.format(report_data['due_soon_count'], report_data['overdue_count'])
        
        if report_data['calibration_status']['overdue']:
            html += """
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Category</th>
                        <th>Manufacturer</th>
                        <th>Model</th>
                        <th>Serial Number</th>
                        <th>Calibration Due Date</th>
                    </tr>
            """
            
            for item in report_data['calibration_status']['overdue']:
                html += f"""
                    <tr>
                        <td>{item.get('id', '')}</td>
                        <td>{item.get('category', '')}</td>
                        <td>{item.get('manufacturer', '')}</td>
                        <td>{item.get('model', '')}</td>
                        <td>{item.get('serial_number', '')}</td>
                        <td>{item.get('calibration_due_date', '')}</td>
                    </tr>
                """
            
            html += "</table>"
        else:
            html += "<p>No overdue calibrations found.</p>"
        
        html += """
            <h2>Calibrations Due Soon</h2>
        """
        
        if report_data['calibration_status']['due_soon']:
            html += """
                <table>
                    <tr>
                        <th>ID</th>
                        <th>Category</th>
                        <th>Manufacturer</th>
                        <th>Model</th>
                        <th>Serial Number</th>
                        <th>Calibration Due Date</th>
                    </tr>
            """
            
            for item in report_data['calibration_status']['due_soon']:
                html += f"""
                    <tr>
                        <td>{item.get('id', '')}</td>
                        <td>{item.get('category', '')}</td>
                        <td>{item.get('manufacturer', '')}</td>
                        <td>{item.get('model', '')}</td>
                        <td>{item.get('serial_number', '')}</td>
                        <td>{item.get('calibration_due_date', '')}</td>
                    </tr>
                """
            
            html += "</table>"
        else:
            html += "<p>No calibrations due soon found.</p>"
        
        return html
    
    def _generate_maintenance_html(self, report_data):
        """Generate HTML for maintenance report."""
        html = """
            <div class="summary">
                <h2>Summary</h2>
                <p>Total Maintenance Records: {}</p>
            </div>
            
            <h2>Maintenance Records</h2>
            <table>
                <tr>
                    <th>Equipment ID</th>
                    <th>Date</th>
                    <th>Type</th>
                    <th>Description</th>
                    <th>Technician</th>
                    <th>Cost</th>
                </tr>
        """.format(len(report_data['maintenance_records']))
        
        for record in report_data['maintenance_records']:
            html += f"""
                <tr>
                    <td>{record.get('equipment_id', '')}</td>
                    <td>{record.get('date', '')}</td>
                    <td>{record.get('maintenance_type', '')}</td>
                    <td>{record.get('description', '')}</td>
                    <td>{record.get('technician', '')}</td>
                    <td>${record.get('cost', '0.00')}</td>
                </tr>
            """
        
        html += """
            </table>
            
            <h2>Maintenance by Equipment</h2>
        """
        
        for equipment_id, records in report_data['grouped_records'].items():
            html += f"""
                <h3>Equipment: {equipment_id}</h3>
                <table>
                    <tr>
                        <th>Date</th>
                        <th>Type</th>
                        <th>Description</th>
                        <th>Technician</th>
                        <th>Cost</th>
                    </tr>
            """
            
            for record in records:
                html += f"""
                    <tr>
                        <td>{record.get('date', '')}</td>
                        <td>{record.get('maintenance_type', '')}</td>
                        <td>{record.get('description', '')}</td>
                        <td>{record.get('technician', '')}</td>
                        <td>${record.get('cost', '0.00')}</td>
                    </tr>
                """
            
            html += "</table>"
        
        return html
    
    def _send_report_emails(self, report_files, frequency):
        """Send email with generated reports.
        
        Args:
            report_files: List of report file paths
            frequency: Email frequency (daily, weekly, monthly)
        """
        if not self.config['email']['enabled']:
            print("Email distribution is disabled in configuration")
            return
        
        # Get email recipients based on frequency
        recipient_groups = self.config['email']['recipients'].get(frequency, [])
        recipients = self._get_recipients_by_group(recipient_groups)
        
        if not recipients:
            print(f"No recipients configured for {frequency} report emails")
            return
        
        # Create email message
        subject = f"{self.config['email']['subject_prefix']}Automatic {frequency.capitalize()} Reports"
        
        # Create date range description
        current_date = datetime.now()
        if frequency == 'daily':
            date_range = f"{(current_date - timedelta(days=1)).strftime('%Y-%m-%d')} to {current_date.strftime('%Y-%m-%d')}"
        elif frequency == 'weekly':
            date_range = f"{(current_date - timedelta(days=7)).strftime('%Y-%m-%d')} to {current_date.strftime('%Y-%m-%d')}"
        elif frequency == 'monthly':
            date_range = f"{(current_date - timedelta(days=30)).strftime('%Y-%m-%d')} to {current_date.strftime('%Y-%m-%d')}"
        else:
            date_range = current_date.strftime('%Y-%m-%d')
        
        # Create email body
        body = self.config['email']['body_template'].format(
            report_type=frequency.capitalize(),
            date_range=date_range
        )
        
        # Placeholder for sending email
        # In a real implementation, this would use Flask-Mail or similar
        print(f"Would send email to {recipients} with subject '{subject}' and {len(report_files)} attachments")
        print(f"Email body: {body}")
        
        # Log email attempt
        print(f"Emails would be sent to: {', '.join(recipients)}")
        print(f"Reports attached: {', '.join(report_files)}")
    
    def _get_recipients_by_group(self, groups):
        """Get email recipients based on groups.
        
        Args:
            groups: List of recipient groups (physicists, admin, management)
            
        Returns:
            List of email addresses
        """
        recipients = []
        
        # Placeholder implementation - in a real app, query user database
        if 'physicists' in groups:
            # Get physicists from user database
            recipients.append('physicists@example.com')
        
        if 'admin' in groups:
            # Get admins from user database
            recipients.append('admin@example.com')
        
        if 'management' in groups:
            # Get management from user database
            recipients.append('management@example.com')
        
        return recipients
    
    def _clean_old_reports(self):
        """Delete reports older than the configured retention period."""
        if not self.config['storage']['enabled'] or not self.config['storage']['retention_days']:
            return
        
        retention_days = self.config['storage']['retention_days']
        base_path = self.config['storage']['path']
        
        if not os.path.exists(base_path):
            return
        
        # Calculate the cutoff date
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        
        # Walk through all files in the report directory
        for root, dirs, files in os.walk(base_path):
            for file in files:
                file_path = os.path.join(root, file)
                
                # Get file modification time
                try:
                    file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    # Delete if older than retention period
                    if file_mod_time < cutoff_date:
                        try:
                            os.remove(file_path)
                            print(f"Deleted old report: {file_path}")
                        except Exception as e:
                            print(f"Error deleting old report {file_path}: {e}")
                except Exception as e:
                    print(f"Error checking file age for {file_path}: {e}")
                    
# Create an instance of the manager
auto_report_manager = AutoReportManager()
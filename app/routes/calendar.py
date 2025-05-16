"""
Calendar routes for tracking equipment deadlines and events
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, send_file, Response
from app import equipment_manager, checkout_manager
from app.models.ticket import TicketManager
from datetime import datetime, timedelta
import json
import uuid
import os
import io
import icalendar
import pytz

bp = Blueprint('calendar', __name__, url_prefix='/calendar')

# Initialize ticket manager
ticket_manager = TicketManager()

@bp.route('/')
def index():
    """Render the unified calendar page showing all deadlines."""
    # Get upcoming calibrations
    upcoming_calibrations = get_upcoming_calibrations()
    
    # Get equipment returns
    equipment_returns = get_equipment_returns()
    
    # Generate calendar events for FullCalendar
    calendar_events = generate_calendar_events(upcoming_calibrations, equipment_returns)
    
    return render_template(
        'calendar/index.html',
        upcoming_calibrations=upcoming_calibrations,
        equipment_returns=equipment_returns,
        calendar_events=json.dumps(calendar_events),
        today=datetime.now().strftime('%Y-%m-%d')
    )

@bp.route('/events')
def get_events():
    """API endpoint for calendar events."""
    # Get date range from query parameters (for future pagination)
    start_date = request.args.get('start')
    end_date = request.args.get('end')
    
    # Get upcoming calibrations
    upcoming_calibrations = get_upcoming_calibrations()
    
    # Get equipment returns
    equipment_returns = get_equipment_returns()
    
    # Generate calendar events
    calendar_events = generate_calendar_events(upcoming_calibrations, equipment_returns)
    
    return jsonify(calendar_events)

@bp.route('/ical')
def ical_feed():
    """Generate iCalendar feed for subscription."""
    # Create calendar
    cal = icalendar.Calendar()
    cal.add('prodid', '-//GearVue Equipment Tracker//EN')
    cal.add('version', '2.0')
    cal.add('calscale', 'GREGORIAN')
    cal.add('method', 'PUBLISH')
    cal.add('x-wr-calname', 'GearVue Equipment Deadlines')
    cal.add('x-wr-caldesc', 'Calendar for equipment calibration and checkout deadlines')
    
    # Get upcoming calibrations
    upcoming_calibrations = get_upcoming_calibrations()
    
    # Get equipment returns
    equipment_returns = get_equipment_returns()
    
    # Add calibration events
    for item in upcoming_calibrations:
        event = icalendar.Event()
        uid = f"cal-{item['id']}-{uuid.uuid4().hex}"
        event.add('uid', uid)
        
        # Parse date
        try:
            due_date = datetime.strptime(item['calibration_due_date'], '%m/%Y')
            # Set to the last day of the month
            if due_date.month == 12:
                end_date = datetime(due_date.year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = datetime(due_date.year, due_date.month + 1, 1) - timedelta(days=1)
        except:
            # Default to today + 30 days if parsing fails
            end_date = datetime.now() + timedelta(days=30)
        
        event.add('dtstart', end_date.date())
        event.add('dtend', end_date.date())
        event.add('dtstamp', datetime.now())
        
        summary = f"Calibration Due: {item['manufacturer']} {item['model']}"
        event.add('summary', summary)
        
        description = f"Equipment: {item['manufacturer']} {item['model']} ({item['id']})\n"
        description += f"Serial Number: {item['serial_number']}\n"
        description += f"Category: {item['category']}\n"
        description += f"Calibration Due: {item['calibration_due_date']}"
        event.add('description', description)
        
        # Add alarm 7 days before
        alarm = icalendar.Alarm()
        alarm.add('action', 'DISPLAY')
        alarm.add('description', f"Calibration due soon for {item['manufacturer']} {item['model']}")
        alarm.add('trigger', timedelta(days=-7))
        event.add_component(alarm)
        
        cal.add_component(event)
    
    # Add checkout return events
    for item in equipment_returns:
        event = icalendar.Event()
        uid = f"ret-{item['id']}-{uuid.uuid4().hex}"
        event.add('uid', uid)
        
        # Parse date
        try:
            due_date = datetime.fromisoformat(item['expected_return'])
        except:
            # Default to today + 1 day if parsing fails
            due_date = datetime.now() + timedelta(days=1)
        
        event.add('dtstart', due_date.date())
        event.add('dtend', due_date.date())
        event.add('dtstamp', datetime.now())
        
        summary = f"Equipment Return: {item['id']}"
        event.add('summary', summary)
        
        description = f"Equipment ID: {item['id']}\n"
        description += f"Checked out by: {item['checked_out_by']}\n"
        description += f"Location: {item['location']}\n"
        description += f"Return due: {due_date.strftime('%Y-%m-%d')}"
        event.add('description', description)
        
        # Add alarm 1 day before
        alarm = icalendar.Alarm()
        alarm.add('action', 'DISPLAY')
        alarm.add('description', f"Equipment return due tomorrow: {item['id']}")
        alarm.add('trigger', timedelta(days=-1))
        event.add_component(alarm)
        
        cal.add_component(event)
    
    # Generate iCalendar file
    ical_data = cal.to_ical()
    
    # Send as attachment
    return Response(
        ical_data,
        mimetype='text/calendar',
        headers={'Content-Disposition': 'attachment; filename=gearvue_equipment.ics'}
    )

def get_upcoming_calibrations():
    """Get upcoming and overdue calibrations with days left calculation."""
    all_equipment = equipment_manager.get_all_equipment()
    today = datetime.now()
    upcoming = []
    
    for item in all_equipment:
        if 'calibration_due_date' not in item or not item['calibration_due_date']:
            continue
        
        # Parse calibration due date
        due_date_str = item['calibration_due_date']
        try:
            # Assuming format is MM/YYYY
            due_date = datetime.strptime(due_date_str, '%m/%Y')
            # Set to the last day of the month
            if due_date.month == 12:
                end_date = datetime(due_date.year + 1, 1, 1) - timedelta(days=1)
            else:
                end_date = datetime(due_date.year, due_date.month + 1, 1) - timedelta(days=1)
            
            # Calculate days left
            days_left = (end_date - today).days
            
            # Only include if due within 90 days or overdue
            if days_left <= 90:
                equipment_item = item.copy()
                equipment_item['days_left'] = days_left
                equipment_item['due_date'] = end_date.strftime('%Y-%m-%d')
                upcoming.append(equipment_item)
        except Exception as e:
            print(f"Error parsing date '{due_date_str}' for equipment {item.get('id')}: {e}")
            continue
    
    # Sort by days left (ascending)
    upcoming.sort(key=lambda x: x['days_left'])
    
    return upcoming

def get_equipment_returns():
    """Get upcoming equipment returns with days left calculation."""
    checked_out = checkout_manager.get_checked_out_equipment()
    today = datetime.now()
    returns = []
    
    for item in checked_out:
        if 'expected_return' not in item or not item['expected_return']:
            continue
        
        # Parse expected return date
        return_date_str = item['expected_return']
        try:
            return_date = datetime.fromisoformat(return_date_str)
            
            # Calculate days left
            days_left = (return_date - today).days
            
            # Add days left to item
            return_item = item.copy()
            return_item['days_left'] = days_left
            return_item['due_date'] = return_date.strftime('%Y-%m-%d')
            
            # Include equipment details
            equipment = equipment_manager.get_equipment_by_id(item['id'])
            if equipment:
                return_item['manufacturer'] = equipment.get('manufacturer', '')
                return_item['model'] = equipment.get('model', '')
                return_item['serial_number'] = equipment.get('serial_number', '')
                return_item['category'] = equipment.get('category', '')
            
            returns.append(return_item)
        except Exception as e:
            print(f"Error parsing date '{return_date_str}' for equipment {item.get('id')}: {e}")
            continue
    
    # Sort by days left (ascending)
    returns.sort(key=lambda x: x['days_left'])
    
    return returns

def generate_calendar_events(calibrations, returns):
    """Generate events for FullCalendar from calibration and checkout data."""
    events = []
    
    # Add calibration events
    for item in calibrations:
        try:
            # Parse due date
            due_date_str = item.get('due_date') or item.get('calibration_due_date')
            if not due_date_str:
                continue
                
            if 'due_date' in item:
                # Already parsed date in YYYY-MM-DD format
                due_date = due_date_str
            else:
                # Parse from MM/YYYY format
                try:
                    month_year = datetime.strptime(due_date_str, '%m/%Y')
                    # Set to the last day of the month
                    if month_year.month == 12:
                        end_date = datetime(month_year.year + 1, 1, 1) - timedelta(days=1)
                    else:
                        end_date = datetime(month_year.year, month_year.month + 1, 1) - timedelta(days=1)
                    due_date = end_date.strftime('%Y-%m-%d')
                except:
                    # Skip if date parsing fails
                    continue
            
            # Determine status and className based on days left
            days_left = item.get('days_left', 0)
            if days_left < 0:
                status = 'Overdue'
                className = 'event-calibration bg-danger'
            elif days_left <= 30:
                status = 'Due Soon'
                className = 'event-calibration bg-warning'
            else:
                status = 'Upcoming'
                className = 'event-calibration'
            
            # Create event
            event = {
                'id': f"cal-{item['id']}",
                'title': f"Calibration: {item['manufacturer']} {item['model']}",
                'start': due_date,
                'allDay': True,
                'className': className,
                'extendedProps': {
                    'type': 'calibration',
                    'equipment': f"{item['manufacturer']} {item['model']} ({item['serial_number']})",
                    'equipmentId': item['id'],
                    'status': status,
                    'details': f"Calibration due on {due_date_str}. {abs(days_left)} days {'overdue' if days_left < 0 else 'remaining'}."
                }
            }
            
            events.append(event)
        except Exception as e:
            print(f"Error creating calibration event for {item.get('id')}: {e}")
            continue
    
    # Add return events
    for item in returns:
        try:
            # Parse return date
            due_date_str = item.get('due_date') or item.get('expected_return')
            if not due_date_str:
                continue
                
            if 'due_date' in item:
                # Already parsed date in YYYY-MM-DD format
                due_date = due_date_str
            else:
                # Parse from ISO format
                try:
                    return_date = datetime.fromisoformat(due_date_str)
                    due_date = return_date.strftime('%Y-%m-%d')
                except:
                    # Skip if date parsing fails
                    continue
            
            # Determine status and className based on days left
            days_left = item.get('days_left', 0)
            if days_left < 0:
                status = 'Overdue'
                className = 'event-checkout bg-danger'
            elif days_left <= 2:
                status = 'Due Soon'
                className = 'event-checkout bg-warning'
            else:
                status = 'Upcoming'
                className = 'event-checkout'
            
            # Get equipment details
            manufacturer = item.get('manufacturer', 'Unknown')
            model = item.get('model', 'Unknown')
            
            # Create event
            event = {
                'id': f"ret-{item['id']}",
                'title': f"Return: {manufacturer} {model}",
                'start': due_date,
                'allDay': True,
                'className': className,
                'extendedProps': {
                    'type': 'checkout',
                    'equipment': f"{manufacturer} {model}",
                    'equipmentId': item['id'],
                    'status': status,
                    'details': f"Equipment checked out by {item['checked_out_by']}. Return due on {due_date}. {abs(days_left)} days {'overdue' if days_left < 0 else 'remaining'}."
                }
            }
            
            events.append(event)
        except Exception as e:
            print(f"Error creating return event for {item.get('id')}: {e}")
            continue
    
    # Add maintenance events (from tickets)
    maintenance_tickets = ticket_manager.get_tickets_by_type('MAINTENANCE')
    for ticket in maintenance_tickets:
        if ticket.get('status') == 'CLOSED':
            continue
        
        try:
            # Use created date + 14 days as the target date
            created_date_str = ticket.get('created_at')
            if not created_date_str:
                continue
                
            try:
                created_date = datetime.fromisoformat(created_date_str)
                due_date = created_date + timedelta(days=14)
                due_date_str = due_date.strftime('%Y-%m-%d')
            except:
                # Skip if date parsing fails
                continue
            
            # Get equipment details
            equipment_id = ticket.get('equipment_id')
            equipment = equipment_manager.get_equipment_by_id(equipment_id)
            
            if not equipment:
                continue
                
            manufacturer = equipment.get('manufacturer', 'Unknown')
            model = equipment.get('model', 'Unknown')
            
            # Create event
            event = {
                'id': f"maint-{ticket['id']}",
                'title': f"Maintenance: {manufacturer} {model}",
                'start': due_date_str,
                'allDay': True,
                'className': 'event-maintenance',
                'extendedProps': {
                    'type': 'maintenance',
                    'equipment': f"{manufacturer} {model}",
                    'equipmentId': equipment_id,
                    'status': ticket.get('status', 'OPEN'),
                    'details': f"Maintenance ticket: {ticket.get('title')}. Created by {ticket.get('created_by')}."
                }
            }
            
            events.append(event)
        except Exception as e:
            print(f"Error creating maintenance event for ticket {ticket.get('id')}: {e}")
            continue
    
    return events
#!/usr/bin/env python3
"""
Flask app to test the calendar functionality directly.
"""
from flask import Flask, render_template, jsonify
from datetime import datetime, timedelta

app = Flask(__name__, 
    template_folder='/config/github/equipment-tracker/app/templates',
    static_folder='/config/github/equipment-tracker/app/static')

@app.route('/')
def index():
    return "Calendar Test App is running. Go to /calendar to see the calendar."

@app.route('/calendar')
def calendar():
    return render_template('admin/calendar.html')

@app.route('/calendar/test')
def calendar_test():
    return render_template('admin/calendar_test.html')

@app.route('/calendar/events')
def calendar_events():
    # Generate test events
    events = []
    
    # Today's date
    today = datetime.now()
    
    # Create some test events
    events.append({
        'id': 'cal-1',
        'title': 'Test Calibration Due Soon',
        'start': (today + timedelta(days=30)).strftime('%Y-%m-%d'),
        'className': 'event-calibration-soon',
        'extendedProps': {
            'equipmentId': 'Chamber-TEST-123',
            'eventType': 'calibration',
            'manufacturer': 'Test Manufacturer',
            'model': 'Test Model',
            'serialNumber': 'Test123',
            'category': 'Chamber',
            'status': 'Due Soon',
            'notes': 'Calibration due in 30 days'
        }
    })
    
    events.append({
        'id': 'cal-2',
        'title': 'Test Calibration Overdue',
        'start': (today - timedelta(days=30)).strftime('%Y-%m-%d'),
        'className': 'event-calibration-overdue',
        'extendedProps': {
            'equipmentId': 'Chamber-TEST-456',
            'eventType': 'calibration',
            'manufacturer': 'Test Manufacturer',
            'model': 'Test Model 2',
            'serialNumber': 'Test456',
            'category': 'Chamber',
            'status': 'Overdue',
            'notes': 'Calibration overdue by 30 days'
        }
    })
    
    events.append({
        'id': 'co-1',
        'title': 'Test Equipment Checkout',
        'start': (today - timedelta(days=5)).strftime('%Y-%m-%d'),
        'className': 'event-checkout',
        'extendedProps': {
            'equipmentId': 'Chamber-TEST-789',
            'eventType': 'checkout',
            'manufacturer': 'Test Manufacturer',
            'model': 'Test Model 3',
            'serialNumber': 'Test789',
            'category': 'Chamber',
            'status': 'Checked Out',
            'user': 'test_user',
            'notes': 'Test checkout for debugging'
        }
    })
    
    events.append({
        'id': 'ret-1',
        'title': 'Test Equipment Return',
        'start': (today + timedelta(days=5)).strftime('%Y-%m-%d'),
        'className': 'event-expected-return',
        'extendedProps': {
            'equipmentId': 'Chamber-TEST-789',
            'eventType': 'return',
            'manufacturer': 'Test Manufacturer',
            'model': 'Test Model 3',
            'serialNumber': 'Test789',
            'category': 'Chamber',
            'status': 'Expected Return',
            'user': 'test_user',
            'notes': 'Test return for debugging'
        }
    })
    
    return jsonify(events)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)
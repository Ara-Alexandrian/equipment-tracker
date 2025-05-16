#!/usr/bin/env python3
"""
Test script for the Equipment Tracker application.
"""
from flask import Flask, json
from app.models.json_utils import DateTimeEncoder
import os
import datetime

app = Flask(__name__)

# Configure Flask's JSON encoder to handle datetime objects
app.json.encoder = DateTimeEncoder

@app.route('/')
def index():
    """Test route that returns a JSON response with a datetime."""
    data = {
        'message': 'Hello from the Equipment Tracker!',
        'timestamp': datetime.datetime.now(),
        'version': '1.0.0'
    }
    return data

@app.route('/test-encoder')
def test_encoder():
    """Test route to test JSON encoder."""
    test_data = {
        'string': 'Hello',
        'number': 42,
        'datetime': datetime.datetime.now(),
        'date': datetime.date.today(),
        'list': [1, 2, 3, datetime.datetime.now()]
    }
    return test_data

if __name__ == '__main__':
    print("Starting test app...")
    app.run(debug=True, host='127.0.0.1', port=5000)
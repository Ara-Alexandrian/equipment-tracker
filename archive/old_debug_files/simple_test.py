#!/usr/bin/env python3
"""
Simple Flask test script
"""
from flask import Flask, jsonify
from datetime import datetime
import json

class DateTimeEncoder(json.JSONEncoder):
    """JSON encoder that handles datetime objects."""
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

app = Flask(__name__)
app.json.encoder = DateTimeEncoder  # Use this for Flask 2.3+ (for older versions use app.json_encoder)

@app.route('/')
def index():
    data = {
        'message': 'Hello from Flask!',
        'timestamp': datetime.now()
    }
    return jsonify(data)

if __name__ == '__main__':
    print("Starting simple test app...")
    app.run(debug=True, host='127.0.0.1', port=5000)
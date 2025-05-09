#!/usr/bin/env python3
"""
Run the Equipment Tracker Flask application
"""
from app import app
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Run the Equipment Tracker application")
    parser.add_argument('--port', type=int, default=5000, help='Port to run the application on')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--debug', action='store_true', default=False, help='Run in debug mode')
    args = parser.parse_args()
    
    print(f"Starting Flask server at http://{args.host}:{args.port}")
    app.run(debug=args.debug, host=args.host, port=args.port)
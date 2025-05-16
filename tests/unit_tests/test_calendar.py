#!/usr/bin/env python3
import sys
import requests
import json
from datetime import datetime
import os

# Set up base URL - default to localhost if no args given
base_url = 'http://localhost:5000'
if len(sys.argv) > 1:
    base_url = sys.argv[1]

# Test URLs
calendar_page_url = f"{base_url}/admin/calendar"
calendar_test_url = f"{base_url}/admin/calendar/test"
calendar_events_url = f"{base_url}/admin/calendar/events"

print(f"Testing calendar functionality at {base_url}...")

# Check calendar page
print(f"\nTesting calendar page: {calendar_page_url}")
try:
    response = requests.get(calendar_page_url)
    print(f"Status: {response.status_code}")
    print(f"Response size: {len(response.text)} bytes")
    if response.status_code == 200:
        print("✓ Calendar page accessible")
    else:
        print("✗ Calendar page not accessible")
        print(f"Response: {response.text[:100]}...")
except Exception as e:
    print(f"Error accessing calendar page: {str(e)}")

# Check calendar test page
print(f"\nTesting calendar test page: {calendar_test_url}")
try:
    response = requests.get(calendar_test_url)
    print(f"Status: {response.status_code}")
    print(f"Response size: {len(response.text)} bytes")
    if response.status_code == 200:
        print("✓ Calendar test page accessible")
    else:
        print("✗ Calendar test page not accessible")
        print(f"Response: {response.text[:100]}...")
except Exception as e:
    print(f"Error accessing calendar test page: {str(e)}")

# Check calendar events API
print(f"\nTesting calendar events API: {calendar_events_url}")
try:
    response = requests.get(calendar_events_url)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"Received {len(data)} calendar events")
            if len(data) > 0:
                print("Sample event:")
                print(json.dumps(data[0], indent=2))
            print("✓ Calendar events API accessible")
        except Exception as e:
            print(f"Error parsing JSON: {str(e)}")
            print(f"Raw response: {response.text[:500]}...")
    else:
        print("✗ Calendar events API not accessible")
        print(f"Response: {response.text[:100]}...")
except Exception as e:
    print(f"Error accessing calendar events API: {str(e)}")

print("\nTest completed!")
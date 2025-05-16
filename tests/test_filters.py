#!/usr/bin/env python3
"""
Test script to verify that all filters in the dashboard are working correctly.
This script makes requests to different filter endpoints and checks the results.
"""
import requests
import sys
from pprint import pprint
from urllib.parse import urljoin

BASE_URL = "http://127.0.0.1:5000"

def test_filters():
    """Test all filter combinations and print results"""
    print("Testing filters...")
    
    # Test status filter
    status_filters = [
        {"name": "All", "url": "/equipment"},
        {"name": "Available", "url": "/equipment?status=available"},
        {"name": "Checked Out", "url": "/equipment?status=checked_out"},
        {"name": "In Transport", "url": "/equipment?status=in_transport"}
    ]

    # Test condition filter
    condition_filters = [
        {"name": "All Conditions", "url": "/equipment"},
        {"name": "Normal", "url": "/equipment?condition=normal"},
        {"name": "Warning", "url": "/equipment?condition=warning"},
        {"name": "Critical", "url": "/equipment?condition=critical"}
    ]

    # Test combined filters
    combined_filters = [
        {"name": "Available + Normal", "url": "/equipment?status=available&condition=normal"},
        {"name": "Available + Critical", "url": "/equipment?status=available&condition=critical"},
        {"name": "In Transport + Normal", "url": "/equipment?status=in_transport&condition=normal"}
    ]
    
    all_filters = status_filters + condition_filters + combined_filters
    
    results = {}
    
    # Make requests to each filter URL
    for filter_test in all_filters:
        filter_name = filter_test["name"]
        filter_url = filter_test["url"]
        full_url = urljoin(BASE_URL, filter_url)
        
        try:
            response = requests.get(full_url)
            if response.status_code == 200:
                # Count equipment items in the response
                # This is a very simple and brittle check just for testing
                # In a real test, you'd parse the HTML properly
                equipment_count = response.text.count('<td class="manufacturer-cell">')
                results[filter_name] = {
                    "url": filter_url,
                    "status": "Success",
                    "equipment_count": equipment_count,
                    "http_status": response.status_code
                }
            else:
                results[filter_name] = {
                    "url": filter_url,
                    "status": "Error",
                    "message": f"HTTP status: {response.status_code}",
                    "http_status": response.status_code
                }
        except Exception as e:
            results[filter_name] = {
                "url": filter_url,
                "status": "Exception",
                "message": str(e)
            }
    
    # Print results
    print("\n=== FILTER TEST RESULTS ===\n")
    for filter_name, result in results.items():
        status_emoji = "✅" if result.get("status") == "Success" else "❌"
        count_info = f"Items: {result.get('equipment_count', 'N/A')}" if result.get("status") == "Success" else result.get("message", "Unknown error")
        print(f"{status_emoji} {filter_name}: {count_info}")
        print(f"    URL: {result['url']}")
        print()

if __name__ == "__main__":
    # Check if server is running first
    try:
        health_check = requests.get(f"{BASE_URL}/")
        if health_check.status_code == 200:
            print(f"Server is running at {BASE_URL}")
            test_filters()
        else:
            print(f"Server may not be running or not responding. Status: {health_check.status_code}")
    except requests.exceptions.ConnectionError:
        print(f"Error: Cannot connect to server at {BASE_URL}. Is the server running?")
        sys.exit(1)
#!/usr/bin/env python3
"""
Simple test script to test filter routes directly.
"""
import requests

BASE_URL = "http://127.0.0.1:5000"

def test_base_url():
    """Test the base URL to see if server is running"""
    print("Testing base URL...")
    response = requests.get(BASE_URL)
    print(f"Status code: {response.status_code}")
    print(f"URL: {response.url}")
    
    if response.status_code == 200:
        print("Server is running!")
    else:
        print("Server might not be running properly.")

def test_dashboard_urls():
    """Test various URLs for the dashboard to find the correct one"""
    test_urls = [
        "/",
        "/dashboard",
        "/dashboard/",
        "/dashboard/equipment",
        "/dashboard/equipment_list",
        "/dashboard/equipment-list",
        "/equipment",
        "/equipment_list",
        "/equipment-list"
    ]
    
    print("\nTesting possible dashboard URLs...")
    for url in test_urls:
        full_url = BASE_URL + url
        response = requests.get(full_url)
        print(f"{response.status_code} - {url}")

if __name__ == "__main__":
    test_base_url()
    test_dashboard_urls()
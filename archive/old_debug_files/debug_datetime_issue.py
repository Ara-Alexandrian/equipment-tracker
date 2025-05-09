#!/usr/bin/env python3
"""
Debug script to find and fix datetime serialization issues
"""
import os
import json
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.models.json_utils import DateTimeEncoder

def check_json_file(file_path):
    """Check if a JSON file has datetime-like strings that need parsing."""
    print(f"Checking {file_path}...")
    
    try:
        # Load the JSON file
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # If it's a list, convert to dict with indices as keys
        if isinstance(data, list):
            data_dict = {i: item for i, item in enumerate(data)}
        else:
            data_dict = data
        
        # Find fields that look like ISO datetime strings
        datetime_fields = []
        for key, value in data_dict.items():
            if isinstance(value, dict):
                for k, v in value.items():
                    if isinstance(v, str) and 'T' in v and len(v) >= 19:
                        try:
                            datetime.fromisoformat(v)
                            datetime_fields.append(f"{key}.{k}")
                        except:
                            pass
        
        if datetime_fields:
            print(f"  Found potential datetime fields: {datetime_fields}")
        else:
            print("  No potential datetime fields found")
        
        # Try serializing the data
        try:
            json_str = json.dumps(data)
            print("  Successfully serialized data with default encoder")
        except TypeError as e:
            print(f"  Serialization error with default encoder: {e}")
            # Try with DateTimeEncoder
            try:
                json_str = json.dumps(data, cls=DateTimeEncoder)
                print("  Successfully serialized data with DateTimeEncoder")
            except TypeError as e:
                print(f"  Serialization error with DateTimeEncoder: {e}")
                return False
        
        return True
    
    except Exception as e:
        print(f"  Error checking file: {e}")
        return False

def main():
    """Main function to check all JSON files."""
    data_dir = 'app/data'
    
    # Get all JSON files
    json_files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith('.json')]
    
    # Check each file
    for file_path in json_files:
        check_json_file(file_path)
        print()
    
    # Print how to fix the issue
    print("To fix datetime serialization issues:")
    print("1. Make sure all code that saves JSON data uses the DateTimeEncoder")
    print("2. For JSON that already has datetime objects, use the fix_json_files.py script")

if __name__ == '__main__':
    main()
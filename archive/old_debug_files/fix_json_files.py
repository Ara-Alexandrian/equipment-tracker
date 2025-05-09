#!/usr/bin/env python3
"""
Fix JSON files with datetime serialization issues.
This script loads each JSON file, converts any datetime objects to ISO format strings,
and then saves the file back with proper encoding.
"""
import os
import json
import sys
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.models.json_utils import DateTimeEncoder

def fix_json_file(file_path):
    """Fix datetime serialization issues in a JSON file."""
    print(f"Fixing {file_path}...")
    
    try:
        # Load the JSON file
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Save the file back with DateTimeEncoder
        with open(file_path, 'w') as f:
            json.dump(data, f, cls=DateTimeEncoder, indent=2)
        
        print(f"  Successfully fixed {file_path}")
        return True
    
    except Exception as e:
        print(f"  Error fixing file: {e}")
        return False

def main():
    """Main function to fix all JSON files."""
    data_dir = 'app/data'
    
    # Get all JSON files
    json_files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith('.json')]
    
    # Fix each file
    for file_path in json_files:
        fix_json_file(file_path)
        print()
    
    print("All JSON files have been processed.")

if __name__ == '__main__':
    main()
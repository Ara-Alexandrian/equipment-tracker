#!/usr/bin/env python3
"""
Script to validate and check JSON files
"""
import os
import json
import sys

def validate_json_file(filepath):
    """Validate a JSON file and check for formatting issues."""
    print(f"Validating {filepath}...")
    
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            
        # Check for common issues in the content
        for i, char in enumerate(content):
            if ord(char) > 127:
                print(f"  WARNING: Non-ASCII character at position {i}: {repr(char)}")
        
        # Try to parse the JSON
        data = json.loads(content)
        print(f"  ✓ Valid JSON format!")
        
        # Check the structure
        if isinstance(data, list):
            print(f"  ✓ File contains a list with {len(data)} items")
            if data:
                print(f"  ✓ First item sample: {list(data[0].keys())[:5]}")
        elif isinstance(data, dict):
            print(f"  ✓ File contains a dictionary with {len(data)} keys")
            if data:
                print(f"  ✓ First key sample: {list(data.keys())[:5]}")
        
        return True
    except json.JSONDecodeError as e:
        print(f"  ✗ Invalid JSON: {e}")
        position = e.pos
        context = content[max(0, position-20):position+20]
        print(f"  Context around error: {repr(context)}")
        return False
    except Exception as e:
        print(f"  ✗ Error validating file: {e}")
        return False

def main():
    """Main function to run validations on JSON files."""
    # Check data directory
    data_dir = "app/data"
    if not os.path.exists(data_dir):
        print(f"Error: Data directory not found at {data_dir}")
        return 1
    
    # Get all JSON files
    json_files = [os.path.join(data_dir, f) for f in os.listdir(data_dir) if f.endswith('.json')]
    
    if not json_files:
        print(f"No JSON files found in {data_dir}")
        return 1
    
    # Validate each file
    all_valid = True
    for file_path in json_files:
        if not validate_json_file(file_path):
            all_valid = False
        print()
    
    if all_valid:
        print("All JSON files are valid!")
    else:
        print("Some JSON files have validation errors!")
    
    return 0 if all_valid else 1

if __name__ == "__main__":
    sys.exit(main())
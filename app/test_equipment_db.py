#!/usr/bin/env python3
"""
Test script to verify database field names and values.
This script displays the first few equipment records to help debug field names.
"""
import os
import json
import sys

def main():
    """Print database records and field names to verify structure."""
    try:
        # Get the absolute path to equipment.json
        script_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(script_dir, 'data', 'equipment.json')
        
        # Open and read the equipment.json file
        with open(json_path, 'r') as f:
            equipment_data = json.load(f)
            
        # Print info about the database
        print(f"Database path: {json_path}")
        print(f"Total records: {len(equipment_data)}")
        print("-" * 40)
        
        # Print the first 3 records with field names
        for i, item in enumerate(equipment_data[:3]):
            print(f"\nRECORD #{i+1}:")
            print("-" * 20)
            for field, value in item.items():
                print(f"  {field}: {value}")
                
        # Print all field names in the first record
        if equipment_data:
            print("\nALL FIELD NAMES:")
            print(", ".join(equipment_data[0].keys()))
            
    except Exception as e:
        print(f"Error: {e}")
        
if __name__ == "__main__":
    main()
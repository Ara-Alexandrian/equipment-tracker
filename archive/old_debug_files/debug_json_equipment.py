#!/usr/bin/env python3
"""
Debug script to trace the datetime serialization issue in json_equipment.py
"""
import os
import sys
import traceback
import json
import pandas as pd
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from app.models.json_utils import DateTimeEncoder

class JsonEquipmentDebugger:
    """Debug version of JsonEquipmentDataManager with more error handling and tracing."""
    
    def __init__(self, data_dir='app/data'):
        """Initialize with the data directory."""
        self.data_dir = data_dir
        self.equipment_json = os.path.join(data_dir, 'equipment.json')
        
        # Try loading the data
        self.debug_load_data()
    
    def debug_load_data(self):
        """Debug version of load_data with more error checking."""
        print(f"Attempting to load equipment data from {self.equipment_json}")
        
        try:
            # Check if JSON file exists
            if not os.path.exists(self.equipment_json):
                print(f"Warning: Equipment JSON file not found at {self.equipment_json}")
                return
            
            # Read the file content directly
            with open(self.equipment_json, 'r') as f:
                file_content = f.read()
                print(f"Successfully read file content ({len(file_content)} bytes)")
            
            # Attempt to parse with default decoder
            try:
                print("Attempting to parse with default JSON decoder...")
                equipment_data = json.loads(file_content)
                print("Success: Parsed with default decoder")
            except Exception as e:
                print(f"Error parsing with default decoder: {e}")
                try:
                    print("Attempting with custom DateTimeEncoder...")
                    # DateTimeEncoder is for encoding, not decoding, but check parse after encode
                    json_str = json.dumps(json.loads(file_content), cls=DateTimeEncoder)
                    equipment_data = json.loads(json_str)
                    print("Success: Parsed with custom encoding/decoding cycle")
                except Exception as nested_e:
                    print(f"Error with custom encoding approach: {nested_e}")
                    raise
            
            # Analyze the equipment data
            print(f"Equipment data is a {type(equipment_data).__name__} with {len(equipment_data)} items")
            
            # Convert to DataFrame
            print("Converting to pandas DataFrame...")
            try:
                self.all_equipment_df = pd.DataFrame(equipment_data)
                print(f"Success: Created DataFrame with shape {self.all_equipment_df.shape}")
            except Exception as e:
                print(f"Error creating DataFrame: {e}")
                traceback.print_exc()
                raise
                
            # Check if we can create a to_dict directly from the data
            try:
                print("Testing to_dict creation...")
                test_dict = {}
                for idx, item in enumerate(equipment_data):
                    if 'id' in item:
                        test_dict[item['id']] = item
                    else:
                        test_dict[f"item_{idx}"] = item
                print(f"Success: Created dictionary with {len(test_dict)} items")
            except Exception as e:
                print(f"Error creating dictionary: {e}")
                traceback.print_exc()
                
            # Try the to_dict method with the DataFrame
            try:
                print("Testing DataFrame to_dict() method...")
                if 'id' in self.all_equipment_df.columns:
                    print("Setting 'id' as index...")
                    self.all_equipment_df = self.all_equipment_df.set_index('id')
                test_dict = self.all_equipment_df.to_dict('index')
                print(f"Success: Created dictionary with {len(test_dict)} items")
            except Exception as e:
                print(f"Error with DataFrame to_dict(): {e}")
                traceback.print_exc()
            
            print("Data loading diagnostics complete")
            
        except Exception as e:
            print(f"Critical error loading equipment data: {e}")
            traceback.print_exc()

def main():
    """Main function to run the debug tests."""
    print("Starting debug tests...")
    debugger = JsonEquipmentDebugger()
    print("Debug tests complete")

if __name__ == '__main__':
    main()
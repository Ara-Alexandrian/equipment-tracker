#!/usr/bin/env python3
"""
Extract data from Excel files and save to JSON format for the application database.
This script is used to create the initial JSON database from Excel files.
"""
import pandas as pd
import json
import os
import sys
import argparse
from datetime import datetime

# Add parent directory to path so we can import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def clean_dataframe(df):
    """Clean up the dataframe by removing empty rows and handling headers."""
    # Skip rows at the beginning that are empty or contain headers
    if df.shape[0] > 3:
        df = df.iloc[3:].reset_index(drop=True)
    
    # Use the first row as column names if they exist
    if not df.empty:
        df.columns = pd.Series(df.iloc[0]).fillna(f'Col{pd.Series(df.columns).str.replace("Unnamed: ", "")}')
        df = df.iloc[1:].reset_index(drop=True)
    
    # Drop completely empty rows
    df = df.dropna(how='all')
    
    return df

def normalize_column_name(name):
    """Normalize column names to a standard format."""
    if pd.isna(name):
        return None
    
    # Convert to string and lowercase
    name_str = str(name).lower().strip()
    
    # Map known column names to standard names
    column_map = {
        'type': 'equipment_type',
        'manufacturer': 'manufacturer',
        'model': 'model',
        'sn': 'serial_number',
        'location': 'location',
        'cal due date': 'calibration_due_date',
        'comments': 'notes',
        'chk source': 'check_source'
    }
    
    # Try to match with standard names
    for key, value in column_map.items():
        if key in name_str:
            return value
    
    # Return original if no match
    return name_str

def extract_chambers_data(file_path):
    """Extract chambers data from Excel file."""
    try:
        # Read chambers sheet
        chambers_df = pd.read_excel(file_path, sheet_name='Chambers')
        chambers_df = clean_dataframe(chambers_df)
        
        # Normalize column names
        new_columns = []
        for col in chambers_df.columns:
            new_columns.append(normalize_column_name(col))
        chambers_df.columns = new_columns
        
        # Convert to list of dictionaries
        chambers_data = []
        for idx, row in chambers_df.iterrows():
            # Skip rows that don't have equipment_type or are NaN
            if 'equipment_type' not in chambers_df.columns or pd.isna(row['equipment_type']):
                continue
            
            # Create a clean record
            manufacturer = row['manufacturer'] if 'manufacturer' in chambers_df.columns and not pd.isna(row['manufacturer']) else 'Unknown'
            serial = row['serial_number'] if 'serial_number' in chambers_df.columns and not pd.isna(row['serial_number']) else f"unknown-{idx}"
            
            record = {
                'category': 'Chamber',
                'id': f"Chamber-{manufacturer}-{serial}".replace(' ', '_'),
            }
            
            # Add other fields
            for col in chambers_df.columns:
                if col and col in row.index and not pd.isna(row[col]):
                    record[col] = str(row[col])
            
            chambers_data.append(record)
        
        return chambers_data
    
    except Exception as e:
        print(f"Error extracting chambers data: {e}")
        import traceback
        traceback.print_exc()
        return []

def extract_electrometers_data(file_path):
    """Extract electrometers data from Excel file."""
    try:
        # Read electrometers sheet
        electrometers_df = pd.read_excel(file_path, sheet_name='Electrometers')
        electrometers_df = clean_dataframe(electrometers_df)
        
        # Normalize column names
        new_columns = []
        for col in electrometers_df.columns:
            new_columns.append(normalize_column_name(col))
        electrometers_df.columns = new_columns
        
        # Convert to list of dictionaries
        electrometers_data = []
        for idx, row in electrometers_df.iterrows():
            # Skip rows that don't have equipment_type or are NaN
            if 'equipment_type' not in electrometers_df.columns or pd.isna(row['equipment_type']):
                continue
            
            # Create a clean record
            manufacturer = row['manufacturer'] if 'manufacturer' in electrometers_df.columns and not pd.isna(row['manufacturer']) else 'Unknown'
            serial = row['serial_number'] if 'serial_number' in electrometers_df.columns and not pd.isna(row['serial_number']) else f"unknown-{idx}"
            
            record = {
                'category': 'Electrometer',
                'id': f"Electrometer-{manufacturer}-{serial}".replace(' ', '_'),
            }
            
            # Add other fields
            for col in electrometers_df.columns:
                if col and col in row.index and not pd.isna(row[col]):
                    record[col] = str(row[col])
            
            electrometers_data.append(record)
        
        return electrometers_data
    
    except Exception as e:
        print(f"Error extracting electrometers data: {e}")
        import traceback
        traceback.print_exc()
        return []

def extract_survey_meters_data(file_path):
    """Extract survey meters data from Excel file."""
    try:
        # Read survey meters sheet
        survey_meters_df = pd.read_excel(file_path, sheet_name='Survey Meters')
        survey_meters_df = clean_dataframe(survey_meters_df)
        
        # Normalize column names
        new_columns = []
        for col in survey_meters_df.columns:
            new_columns.append(normalize_column_name(col))
        survey_meters_df.columns = new_columns
        
        # Convert to list of dictionaries
        survey_meters_data = []
        for idx, row in survey_meters_df.iterrows():
            # Skip rows that don't have equipment_type or are NaN
            if 'equipment_type' not in survey_meters_df.columns or pd.isna(row['equipment_type']):
                continue
            
            # Create a clean record
            manufacturer = row['manufacturer'] if 'manufacturer' in survey_meters_df.columns and not pd.isna(row['manufacturer']) else 'Unknown'
            serial = row['serial_number'] if 'serial_number' in survey_meters_df.columns and not pd.isna(row['serial_number']) else f"unknown-{idx}"
            
            record = {
                'category': 'Survey Meter',
                'id': f"SurveyMeter-{manufacturer}-{serial}".replace(' ', '_'),
            }
            
            # Add other fields
            for col in survey_meters_df.columns:
                if col and col in row.index and not pd.isna(row[col]):
                    record[col] = str(row[col])
            
            survey_meters_data.append(record)
        
        return survey_meters_data
    
    except Exception as e:
        print(f"Error extracting survey meters data: {e}")
        import traceback
        traceback.print_exc()
        return []

def generate_initial_equipment_status(equipment_data):
    """Generate initial equipment status data."""
    status_data = {}
    
    for item in equipment_data:
        equipment_id = item.get('id')
        if not equipment_id:
            continue
        
        # Set default status
        status_data[equipment_id] = {
            "status": "In Storage",
            "location": item.get('location', 'Default Location'),
            "checked_out_by": None,
            "checked_out_time": None,
            "expected_return": None,
            "notes": "",
            "last_updated": datetime.now().isoformat(),
            "updated_by": "system"
        }
    
    return status_data

def main():
    """Main function to extract data and save to JSON."""
    parser = argparse.ArgumentParser(description='Extract data from Excel files and save to JSON')
    parser.add_argument('--chambers-file', default='Resources/2025 Health Physics Equipment List_Chambers & Electrometers.xls',
                        help='Path to chambers and electrometers Excel file')
    parser.add_argument('--survey-meters-file', default='Resources/2025 Survey Meter Inventory & Calibration_updated 0425.xls',
                        help='Path to survey meters Excel file')
    parser.add_argument('--output-dir', default='app/data', help='Output directory for JSON files')
    args = parser.parse_args()

    print(f"Extracting data from Excel files...")
    
    # Extract data from Excel files
    chambers_data = extract_chambers_data(args.chambers_file)
    electrometers_data = extract_electrometers_data(args.chambers_file)
    survey_meters_data = extract_survey_meters_data(args.survey_meters_file)
    
    # Combine all equipment data
    all_equipment = chambers_data + electrometers_data + survey_meters_data
    
    # Generate initial equipment status
    equipment_status = generate_initial_equipment_status(all_equipment)
    
    # Create output directory if it doesn't exist
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Save equipment data to JSON file
    equipment_file = os.path.join(args.output_dir, 'equipment.json')
    with open(equipment_file, 'w') as f:
        json.dump(all_equipment, f, indent=2)
    
    print(f"Saved {len(all_equipment)} equipment items to {equipment_file}")
    
    # Save equipment status to JSON file
    status_file = os.path.join(args.output_dir, 'equipment_status.json')
    with open(status_file, 'w') as f:
        json.dump(equipment_status, f, indent=2)
    
    print(f"Saved equipment status to {status_file}")

if __name__ == '__main__':
    main()
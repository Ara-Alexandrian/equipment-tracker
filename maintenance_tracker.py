#!/usr/bin/env python3
import pandas as pd
import os
import sys
import matplotlib.pyplot as plt
from datetime import datetime
import csv
import re

# Set file paths
CHAMBERS_FILE = os.path.join('Resources', '2025 Health Physics Equipment List_Chambers & Electrometers.xls')
SURVEY_METERS_FILE = os.path.join('Resources', '2025 Survey Meter Inventory & Calibration_updated 0425.xls')
MAINTENANCE_LOG = os.path.join('Resources', 'maintenance_log.csv')
OUTPUT_DIR = 'output'

def ensure_output_dir():
    """Ensure the output directory exists"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

def create_maintenance_log_if_missing():
    """Create maintenance log file if it doesn't exist"""
    if not os.path.exists(MAINTENANCE_LOG):
        # Create the Resources directory if it doesn't exist
        os.makedirs(os.path.dirname(MAINTENANCE_LOG), exist_ok=True)
        
        # Create an empty maintenance log with headers
        with open(MAINTENANCE_LOG, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'equipment_type', 'model', 'serial_number', 'date', 
                'maintenance_type', 'description', 'technician', 'cost'
            ])
        print(f"Created new maintenance log file: {MAINTENANCE_LOG}")
    else:
        print(f"Using existing maintenance log: {MAINTENANCE_LOG}")

def extract_maintenance_entries():
    """Extract maintenance entries from Excel files"""
    maintenance_entries = []
    
    try:
        # Extract from chambers file
        chambers_df = pd.read_excel(CHAMBERS_FILE, sheet_name='Chambers')
        chambers_df = chambers_df.iloc[3:].reset_index(drop=True)  # Skip header rows
        
        # Try to find column with maintenance notes
        comments_cols = [col for col in chambers_df.columns if 'comment' in str(col).lower()]
        if comments_cols:
            comments_col = comments_cols[0]
            
            # Look for maintenance-related comments
            for idx, row in chambers_df.iterrows():
                comment = row.get(comments_col)
                if isinstance(comment, str) and ('repair' in comment.lower() or 'maintenance' in comment.lower()):
                    # Try to extract date and maintenance info
                    date_match = re.search(r'(\d{1,2}/\d{2,4})', comment)
                    date_str = date_match.group(1) if date_match else "Unknown"
                    
                    # Create maintenance entry
                    entry = {
                        'equipment_type': 'Chamber',
                        'model': row.get('Manufacturer', 'Unknown'),
                        'serial_number': row.get('SN', 'Unknown'),
                        'date': date_str,
                        'maintenance_type': 'Repair' if 'repair' in comment.lower() else 'Maintenance',
                        'description': comment,
                        'technician': 'Unknown',
                        'cost': 0.0
                    }
                    maintenance_entries.append(entry)
        
        # Similar extraction from Electrometers sheet
        electrometers_df = pd.read_excel(CHAMBERS_FILE, sheet_name='Electrometers')
        electrometers_df = electrometers_df.iloc[3:].reset_index(drop=True)  # Skip header rows
        
        # Try to find column with maintenance notes
        comments_cols = [col for col in electrometers_df.columns if 'comment' in str(col).lower()]
        if comments_cols:
            comments_col = comments_cols[0]
            
            # Look for maintenance-related comments
            for idx, row in electrometers_df.iterrows():
                comment = row.get(comments_col)
                if isinstance(comment, str) and ('repair' in comment.lower() or 'maintenance' in comment.lower()):
                    # Try to extract date and maintenance info
                    date_match = re.search(r'(\d{1,2}/\d{2,4})', comment)
                    date_str = date_match.group(1) if date_match else "Unknown"
                    
                    # Create maintenance entry
                    entry = {
                        'equipment_type': 'Electrometer',
                        'model': row.get('Manufacturer', 'Unknown'),
                        'serial_number': row.get('SN', 'Unknown'),
                        'date': date_str,
                        'maintenance_type': 'Repair' if 'repair' in comment.lower() else 'Maintenance',
                        'description': comment,
                        'technician': 'Unknown',
                        'cost': 0.0
                    }
                    maintenance_entries.append(entry)
        
        # Extract from survey meters file
        survey_meters_df = pd.read_excel(SURVEY_METERS_FILE, sheet_name='Survey Meters')
        survey_meters_df = survey_meters_df.iloc[3:].reset_index(drop=True)  # Skip header rows
        
        # Try to find column with maintenance notes
        comments_cols = [col for col in survey_meters_df.columns if 'comment' in str(col).lower()]
        if comments_cols:
            comments_col = comments_cols[0]
            
            # Look for maintenance-related comments
            for idx, row in survey_meters_df.iterrows():
                comment = row.get(comments_col)
                if isinstance(comment, str) and ('repair' in comment.lower() or 'maintenance' in comment.lower()):
                    # Try to extract date and maintenance info
                    date_match = re.search(r'(\d{1,2}/\d{2,4})', comment)
                    date_str = date_match.group(1) if date_match else "Unknown"
                    
                    # Create maintenance entry
                    entry = {
                        'equipment_type': 'Survey Meter',
                        'model': row.get('Manufacturer', 'Unknown'),
                        'serial_number': row.get('SN', 'Unknown'),
                        'date': date_str,
                        'maintenance_type': 'Repair' if 'repair' in comment.lower() else 'Maintenance',
                        'description': comment,
                        'technician': 'Unknown',
                        'cost': 0.0
                    }
                    maintenance_entries.append(entry)
    
    except Exception as e:
        print(f"Error extracting maintenance entries: {e}")
    
    return maintenance_entries

def add_new_maintenance_entry():
    """Add a new maintenance entry interactively"""
    print("\nAdd New Maintenance Entry")
    print("=" * 40)
    
    # Get equipment type
    print("\nEquipment Type:")
    print("1. Chamber")
    print("2. Electrometer")
    print("3. Survey Meter")
    
    equipment_choice = input("Enter equipment type (1-3): ")
    if equipment_choice == '1':
        equipment_type = 'Chamber'
    elif equipment_choice == '2':
        equipment_type = 'Electrometer'
    elif equipment_choice == '3':
        equipment_type = 'Survey Meter'
    else:
        print("Invalid choice. Using 'Other'.")
        equipment_type = 'Other'
    
    # Get model
    model = input("Enter model: ")
    
    # Get serial number
    serial_number = input("Enter serial number: ")
    
    # Get date (default to today)
    date_input = input("Enter date (MM/DD/YYYY) or press Enter for today's date: ")
    if date_input.strip():
        date = date_input
    else:
        date = datetime.now().strftime("%m/%d/%Y")
    
    # Get maintenance type
    print("\nMaintenance Type:")
    print("1. Calibration")
    print("2. Repair")
    print("3. Routine Maintenance")
    print("4. Inspection")
    print("5. Other")
    
    maintenance_choice = input("Enter maintenance type (1-5): ")
    if maintenance_choice == '1':
        maintenance_type = 'Calibration'
    elif maintenance_choice == '2':
        maintenance_type = 'Repair'
    elif maintenance_choice == '3':
        maintenance_type = 'Routine Maintenance'
    elif maintenance_choice == '4':
        maintenance_type = 'Inspection'
    elif maintenance_choice == '5':
        maintenance_type = 'Other'
    else:
        print("Invalid choice. Using 'Other'.")
        maintenance_type = 'Other'
    
    # Get description
    description = input("Enter description: ")
    
    # Get technician
    technician = input("Enter technician name: ")
    
    # Get cost
    cost_input = input("Enter cost (if applicable): ")
    try:
        cost = float(cost_input) if cost_input.strip() else 0.0
    except:
        print("Invalid cost format. Using 0.0.")
        cost = 0.0
    
    # Create new entry
    entry = [
        equipment_type, model, serial_number, date, 
        maintenance_type, description, technician, cost
    ]
    
    # Add to maintenance log
    with open(MAINTENANCE_LOG, 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(entry)
    
    print(f"\nMaintenance entry added for {equipment_type} {model} (SN: {serial_number}).")

def view_maintenance_history():
    """View maintenance history"""
    print("\nMaintenance History")
    print("=" * 40)
    
    if not os.path.exists(MAINTENANCE_LOG):
        print("No maintenance log found.")
        return
    
    try:
        # Load maintenance log
        maintenance_df = pd.read_csv(MAINTENANCE_LOG)
        
        if maintenance_df.empty:
            print("No maintenance entries found.")
            return
        
        # Option to filter
        print("\nFilter options:")
        print("1. View all entries")
        print("2. Filter by equipment type")
        print("3. Filter by date range")
        print("4. Filter by maintenance type")
        
        filter_choice = input("Enter filter option (1-4): ")
        
        if filter_choice == '1':
            filtered_df = maintenance_df
        elif filter_choice == '2':
            equipment_type = input("Enter equipment type (Chamber/Electrometer/Survey Meter): ")
            filtered_df = maintenance_df[maintenance_df['equipment_type'].str.lower() == equipment_type.lower()]
        elif filter_choice == '3':
            start_date = input("Enter start date (MM/DD/YYYY): ")
            end_date = input("Enter end date (MM/DD/YYYY): ")
            # Simple filtering - a proper implementation would parse and compare dates
            filtered_df = maintenance_df
        elif filter_choice == '4':
            maintenance_type = input("Enter maintenance type: ")
            filtered_df = maintenance_df[maintenance_df['maintenance_type'].str.lower() == maintenance_type.lower()]
        else:
            print("Invalid choice. Showing all entries.")
            filtered_df = maintenance_df
        
        # Display filtered entries
        if filtered_df.empty:
            print("No entries match the filter criteria.")
        else:
            print(f"\nFound {len(filtered_df)} entries:")
            pd.set_option('display.max_columns', None)
            pd.set_option('display.width', 120)
            print(filtered_df)
        
        # Option to export
        export_choice = input("\nExport results to CSV? (y/n): ")
        if export_choice.lower() == 'y':
            ensure_output_dir()
            export_path = os.path.join(OUTPUT_DIR, 'maintenance_report.csv')
            filtered_df.to_csv(export_path, index=False)
            print(f"Exported to {export_path}")
        
    except Exception as e:
        print(f"Error viewing maintenance history: {e}")

def generate_maintenance_report():
    """Generate maintenance report and visualizations"""
    print("\nGenerating Maintenance Report")
    print("=" * 40)
    
    if not os.path.exists(MAINTENANCE_LOG):
        print("No maintenance log found.")
        return
    
    try:
        # Load maintenance log
        maintenance_df = pd.read_csv(MAINTENANCE_LOG)
        
        if maintenance_df.empty:
            print("No maintenance entries found.")
            return
        
        ensure_output_dir()
        
        # Summary by equipment type
        equipment_counts = maintenance_df['equipment_type'].value_counts()
        
        plt.figure(figsize=(10, 6))
        equipment_counts.plot.bar()
        plt.title('Maintenance Activities by Equipment Type')
        plt.xlabel('Equipment Type')
        plt.ylabel('Number of Maintenance Activities')
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'maintenance_by_equipment.png'))
        plt.close()
        
        # Summary by maintenance type
        maintenance_type_counts = maintenance_df['maintenance_type'].value_counts()
        
        plt.figure(figsize=(10, 6))
        maintenance_type_counts.plot.bar()
        plt.title('Maintenance Activities by Type')
        plt.xlabel('Maintenance Type')
        plt.ylabel('Number of Activities')
        plt.tight_layout()
        plt.savefig(os.path.join(OUTPUT_DIR, 'maintenance_by_type.png'))
        plt.close()
        
        # If costs are available, add cost analysis
        if 'cost' in maintenance_df.columns and maintenance_df['cost'].sum() > 0:
            # Total cost by equipment type
            cost_by_equipment = maintenance_df.groupby('equipment_type')['cost'].sum()
            
            plt.figure(figsize=(10, 6))
            cost_by_equipment.plot.bar()
            plt.title('Maintenance Costs by Equipment Type')
            plt.xlabel('Equipment Type')
            plt.ylabel('Total Cost')
            plt.tight_layout()
            plt.savefig(os.path.join(OUTPUT_DIR, 'maintenance_cost_by_equipment.png'))
            plt.close()
        
        print(f"Maintenance report visualizations saved to {OUTPUT_DIR} directory.")
        
    except Exception as e:
        print(f"Error generating maintenance report: {e}")

def import_maintenance_data():
    """Import maintenance data from Excel files"""
    print("\nImporting Maintenance Data from Excel Files")
    print("=" * 40)
    
    # Extract maintenance entries from Excel files
    maintenance_entries = extract_maintenance_entries()
    
    if not maintenance_entries:
        print("No maintenance entries found in Excel files.")
        return
    
    print(f"Found {len(maintenance_entries)} maintenance entries in Excel files.")
    
    # Create maintenance log if it doesn't exist
    create_maintenance_log_if_missing()
    
    # Check for existing entries to avoid duplicates
    existing_entries = []
    try:
        if os.path.exists(MAINTENANCE_LOG):
            existing_df = pd.read_csv(MAINTENANCE_LOG)
            for _, row in existing_df.iterrows():
                key = f"{row['equipment_type']}_{row['model']}_{row['serial_number']}_{row['date']}_{row['description'][:20]}"
                existing_entries.append(key)
    except Exception as e:
        print(f"Error reading existing maintenance log: {e}")
    
    # Add new entries to maintenance log
    new_entries = 0
    with open(MAINTENANCE_LOG, 'a', newline='') as f:
        writer = csv.writer(f)
        
        for entry in maintenance_entries:
            # Create a key to check for duplicates
            key = f"{entry['equipment_type']}_{entry['model']}_{entry['serial_number']}_{entry['date']}_{entry['description'][:20]}"
            
            if key not in existing_entries:
                writer.writerow([
                    entry['equipment_type'],
                    entry['model'],
                    entry['serial_number'],
                    entry['date'],
                    entry['maintenance_type'],
                    entry['description'],
                    entry['technician'],
                    entry['cost']
                ])
                new_entries += 1
    
    print(f"Imported {new_entries} new maintenance entries.")

def main():
    """Main function for the maintenance tracker"""
    print("Equipment Maintenance Tracker")
    print("=" * 40)
    
    # Create maintenance log if it doesn't exist
    create_maintenance_log_if_missing()
    
    while True:
        print("\nMaintenance Tracker Menu:")
        print("1. View Maintenance History")
        print("2. Add New Maintenance Entry")
        print("3. Generate Maintenance Report")
        print("4. Import Maintenance Data from Excel Files")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ")
        
        if choice == '1':
            view_maintenance_history()
        elif choice == '2':
            add_new_maintenance_entry()
        elif choice == '3':
            generate_maintenance_report()
        elif choice == '4':
            import_maintenance_data()
        elif choice == '5':
            print("\nExiting Maintenance Tracker.")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

if __name__ == "__main__":
    main()
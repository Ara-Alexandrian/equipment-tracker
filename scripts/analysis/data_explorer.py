#!/usr/bin/env python3
import pandas as pd
import os
import sys

# Set file paths
CHAMBERS_FILE = os.path.join('Resources', '2025 Health Physics Equipment List_Chambers & Electrometers.xls')
SURVEY_METERS_FILE = os.path.join('Resources', '2025 Survey Meter Inventory & Calibration_updated 0425.xls')

def explorer():
    """Interactive data explorer"""
    print("Equipment Tracker - Data Explorer")
    print("=" * 50)
    
    try:
        # Load all sheets
        print("\nLoading Excel files...")
        chambers_excel = pd.ExcelFile(CHAMBERS_FILE)
        meters_excel = pd.ExcelFile(SURVEY_METERS_FILE)
        
        print(f"\nAvailable sheets in {os.path.basename(CHAMBERS_FILE)}:")
        for i, sheet in enumerate(chambers_excel.sheet_names):
            print(f"  {i+1}. {sheet}")
            
        print(f"\nAvailable sheets in {os.path.basename(SURVEY_METERS_FILE)}:")
        for i, sheet in enumerate(meters_excel.sheet_names):
            print(f"  {i+1}. {sheet}")
        
        # Interactive exploration
        while True:
            print("\n" + "=" * 50)
            print("Data Explorer Options:")
            print("1. View sheet headers")
            print("2. Search for equipment")
            print("3. Show sheets structure")
            print("4. Display sample data")
            print("5. Exit")
            
            choice = input("\nEnter your choice (1-5): ")
            
            if choice == '1':
                file_choice = input("Which file? (1 for Chambers/Electrometers, 2 for Survey Meters): ")
                
                if file_choice == '1':
                    excel = chambers_excel
                    file_desc = "Chambers & Electrometers"
                elif file_choice == '2':
                    excel = meters_excel
                    file_desc = "Survey Meters"
                else:
                    print("Invalid choice.")
                    continue
                    
                sheet_name = input(f"Enter sheet name from {file_desc}: ")
                try:
                    df = pd.read_excel(excel, sheet_name=sheet_name)
                    print(f"\nColumns in {sheet_name}:")
                    for col in df.columns:
                        print(f"  - {col}")
                except:
                    print("Sheet not found.")
                    
            elif choice == '2':
                search_term = input("Enter search term: ")
                
                print("\nSearching for equipment containing: " + search_term)
                print("-" * 50)
                
                # Search in chambers
                try:
                    chambers_df = pd.read_excel(CHAMBERS_FILE, sheet_name='Chambers')
                    chambers_df = chambers_df.fillna('')
                    
                    chambers_results = chambers_df[chambers_df.apply(
                        lambda row: search_term.lower() in ' '.join(row.astype(str)).lower(), axis=1)]
                    
                    if not chambers_results.empty:
                        print(f"\nFound {len(chambers_results)} matches in Chambers sheet:")
                        print(chambers_results)
                except:
                    print("Error searching Chambers sheet")
                
                # Search in electrometers
                try:
                    electrometers_df = pd.read_excel(CHAMBERS_FILE, sheet_name='Electrometers')
                    electrometers_df = electrometers_df.fillna('')
                    
                    electrometers_results = electrometers_df[electrometers_df.apply(
                        lambda row: search_term.lower() in ' '.join(row.astype(str)).lower(), axis=1)]
                    
                    if not electrometers_results.empty:
                        print(f"\nFound {len(electrometers_results)} matches in Electrometers sheet:")
                        print(electrometers_results)
                except:
                    print("Error searching Electrometers sheet")
                
                # Search in survey meters
                try:
                    survey_meters_df = pd.read_excel(SURVEY_METERS_FILE, sheet_name='Survey Meters')
                    survey_meters_df = survey_meters_df.fillna('')
                    
                    survey_meters_results = survey_meters_df[survey_meters_df.apply(
                        lambda row: search_term.lower() in ' '.join(row.astype(str)).lower(), axis=1)]
                    
                    if not survey_meters_results.empty:
                        print(f"\nFound {len(survey_meters_results)} matches in Survey Meters sheet:")
                        print(survey_meters_results)
                except:
                    print("Error searching Survey Meters sheet")
                
            elif choice == '3':
                file_choice = input("Which file? (1 for Chambers/Electrometers, 2 for Survey Meters): ")
                
                if file_choice == '1':
                    excel = chambers_excel
                elif file_choice == '2':
                    excel = meters_excel
                else:
                    print("Invalid choice.")
                    continue
                
                for sheet_name in excel.sheet_names:
                    try:
                        df = pd.read_excel(excel, sheet_name=sheet_name)
                        print(f"\n{sheet_name} Shape: {df.shape}")
                        print(f"Column Data Types:")
                        for col, dtype in df.dtypes.items():
                            print(f"  - {col}: {dtype}")
                    except:
                        print(f"Error reading sheet {sheet_name}")
                        
            elif choice == '4':
                file_choice = input("Which file? (1 for Chambers/Electrometers, 2 for Survey Meters): ")
                
                if file_choice == '1':
                    excel = chambers_excel
                    file_desc = "Chambers & Electrometers"
                elif file_choice == '2':
                    excel = meters_excel
                    file_desc = "Survey Meters"
                else:
                    print("Invalid choice.")
                    continue
                    
                sheet_name = input(f"Enter sheet name from {file_desc}: ")
                try:
                    df = pd.read_excel(excel, sheet_name=sheet_name)
                    print(f"\nSample data from {sheet_name} (first 5 rows):")
                    print(df.head())
                except:
                    print("Sheet not found.")
                    
            elif choice == '5':
                print("\nExiting data explorer.")
                break
                
            else:
                print("Invalid choice. Please enter a number between 1 and 5.")
    
    except Exception as e:
        print(f"Error in data explorer: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(explorer())
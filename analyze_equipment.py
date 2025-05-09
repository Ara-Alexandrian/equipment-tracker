#!/usr/bin/env python3
import pandas as pd
import os
import matplotlib.pyplot as plt
from datetime import datetime

# Set file paths
chambers_file = os.path.join('Resources', '2025 Health Physics Equipment List_Chambers & Electrometers.xls')
survey_meters_file = os.path.join('Resources', '2025 Survey Meter Inventory & Calibration_updated 0425.xls')

def clean_dataframe(df):
    """Clean up the dataframe by removing empty rows and handling headers"""
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

def extract_calibration_dates(df, date_column_name):
    """Extract and process calibration dates from the dataframe"""
    dates = []
    
    # Find column that might contain calibration dates
    date_cols = [col for col in df.columns if date_column_name.lower() in str(col).lower()]
    
    if date_cols:
        date_col = date_cols[0]
        
        # Extract dates, handling different formats
        for date_str in df[date_col].dropna():
            try:
                # Try to extract date - could be in different formats
                if isinstance(date_str, str):
                    # Extract just the date part if there's additional text
                    date_parts = date_str.split(' - ')[0].strip()
                    
                    # Try different date formats (add more as needed)
                    date_formats = ['%m/%Y', '%m/%d/%Y', '%B %Y', '%b %Y']
                    
                    for fmt in date_formats:
                        try:
                            date = datetime.strptime(date_parts, fmt)
                            dates.append(date)
                            break
                        except:
                            continue
            except:
                continue
    
    return dates

def analyze_equipment_files():
    """Analyze both equipment files and prepare report"""
    print("Equipment Tracker - Analysis Report")
    print("="*50)
    
    # Chamber & Electrometers Analysis
    chambers_df = None
    electrometers_df = None
    
    try:
        # Read chambers sheet
        chambers_df = pd.read_excel(chambers_file, sheet_name='Chambers')
        chambers_df = clean_dataframe(chambers_df)
        
        # Read electrometers sheet
        electrometers_df = pd.read_excel(chambers_file, sheet_name='Electrometers')
        electrometers_df = clean_dataframe(electrometers_df)
        
        print("\n1. CHAMBERS & ELECTROMETERS ANALYSIS")
        print("-" * 40)
        
        if chambers_df is not None:
            chamber_types = chambers_df.iloc[:, 0].value_counts()
            print(f"\nChamber Types Count:")
            for chamber_type, count in chamber_types.items():
                if pd.notna(chamber_type) and str(chamber_type).strip():
                    print(f"  - {chamber_type}: {count}")
                    
            # Extract calibration dates
            chamber_cal_dates = extract_calibration_dates(chambers_df, 'cal')
            if chamber_cal_dates:
                print(f"\nChamber Calibrations:")
                print(f"  - Total chambers with calibration dates: {len(chamber_cal_dates)}")
                
                # Check if any calibrations are due soon (within 3 months)
                current_date = datetime.now()
                due_soon = sum(1 for date in chamber_cal_dates if 
                              (date.year == current_date.year and date.month <= current_date.month + 3))
                print(f"  - Calibrations due within 3 months: {due_soon}")
        
        if electrometers_df is not None:
            electrometer_models = electrometers_df.iloc[:, 1].value_counts()
            print(f"\nElectrometer Models:")
            for model, count in electrometer_models.items():
                if pd.notna(model) and str(model).strip():
                    print(f"  - {model}: {count}")
    
    except Exception as e:
        print(f"Error analyzing chambers file: {e}")
    
    # Survey Meters Analysis
    survey_meters_df = None
    
    try:
        # Read survey meters sheet
        survey_meters_df = pd.read_excel(survey_meters_file, sheet_name='Survey Meters')
        survey_meters_df = clean_dataframe(survey_meters_df)
        
        print("\n2. SURVEY METERS ANALYSIS")
        print("-" * 40)
        
        if survey_meters_df is not None:
            # Count meter types
            meter_types = survey_meters_df.iloc[:, 0].value_counts()
            print(f"\nSurvey Meter Types:")
            for meter_type, count in meter_types.items():
                if pd.notna(meter_type) and str(meter_type).strip():
                    print(f"  - {meter_type}: {count}")
                    
            # Extract locations if available
            location_cols = [col for col in survey_meters_df.columns if 'location' in str(col).lower()]
            if location_cols:
                locations = survey_meters_df[location_cols[0]].value_counts()
                print(f"\nMeter Locations:")
                for location, count in locations.items():
                    if pd.notna(location) and str(location).strip():
                        print(f"  - {location}: {count}")
                        
            # Extract calibration dates
            meter_cal_dates = extract_calibration_dates(survey_meters_df, 'cal')
            if meter_cal_dates:
                print(f"\nSurvey Meter Calibrations:")
                print(f"  - Total meters with calibration dates: {len(meter_cal_dates)}")
                
                # Check if any calibrations are due soon (within 3 months)
                current_date = datetime.now()
                due_soon = sum(1 for date in meter_cal_dates if 
                              (date.year == current_date.year and date.month <= current_date.month + 3))
                print(f"  - Calibrations due within 3 months: {due_soon}")
    
    except Exception as e:
        print(f"Error analyzing survey meters file: {e}")
    
    return {
        'chambers_df': chambers_df,
        'electrometers_df': electrometers_df,
        'survey_meters_df': survey_meters_df
    }

if __name__ == "__main__":
    analyze_equipment_files()